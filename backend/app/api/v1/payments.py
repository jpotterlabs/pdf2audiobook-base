from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Annotated
from sqlalchemy.orm import Session
from loguru import logger

from app.core.config import settings
from app.core.database import get_db
from app.services.payment import PaymentService, PaddleCheckoutRequest
from app.schemas import Job, Product, User as UserSchema
from app.services.auth import get_current_user
from app.models import User as UserModel, Product as ProductModel

router = APIRouter()


@router.get(
    "/products",
    response_model=List[Product],
    summary="List all available products",
    description="Returns a list of all active products and their details.",
)
async def get_products(db: Annotated[Session, Depends(get_db)]):
    """
    Retrieves all products that are currently marked as active.
    """
    products = db.query(ProductModel).filter(ProductModel.is_active == True).all()
    return products


class CheckoutURLRequest(BaseModel):
    product_id: Union[str, int] = Field(
        ..., json_schema_extra={"example": 1}, description="The internal ID (int) or Paddle ID (string) of the product to purchase."
    )


class CheckoutURLResponse(BaseModel):
    checkout_url: str = Field(..., description="The unique Paddle checkout URL.")


@router.post(
    "/checkout-url",
    response_model=CheckoutURLResponse,
    summary="Generate a Payment Checkout URL",
    description="Creates a unique Paddle checkout URL for a specific product and the currently authenticated user.",
)
async def create_checkout_url(
    request: CheckoutURLRequest, 
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Generates a Paddle checkout URL for the authenticated user to purchase a product.

    - **product_id**: The internal database ID (int) or Paddle ID (string) of the product to buy.
    """
    # 1. Look up the product in our database
    if isinstance(request.product_id, int):
        product = db.query(ProductModel).filter(ProductModel.id == request.product_id).first()
    else:
        # If it's a string, it might be a Paddle Product ID (pro_...) or a numeric ID passed as a string
        if request.product_id.isdigit():
             product = db.query(ProductModel).filter(ProductModel.id == int(request.product_id)).first()
        else:
             product = db.query(ProductModel).filter(ProductModel.paddle_product_id == request.product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {request.product_id} not found"
        )
    
    # 2. Ensure we have a Paddle ID for this product
    if not product.paddle_product_id or product.paddle_product_id.startswith(("free_", "pro_", "enterprise_")):
        logger.warning(f"Product {product.name} (ID: {product.id}) has missing or placeholder Paddle ID: {product.paddle_product_id}")
        # In production, this should be a hard error. In dev/sandbox, we might want to allow it if mocked.
        if not settings.DEBUG:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This product is not correctly configured for payments. Please contact support."
            )

    payment_service = PaymentService()
    
    # 3. Create the checkout request using the Paddle Price ID (paddle_product_id)
    checkout_request = PaddleCheckoutRequest(
        product_id=product.paddle_product_id, 
        customer_email=current_user.email
    )

    try:
        checkout_url = payment_service.generate_checkout_url(checkout_request)
        return CheckoutURLResponse(checkout_url=checkout_url)
    except Exception as e:
        logger.error(f"Failed to generate checkout URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate checkout with payment provider."
        ) from e
