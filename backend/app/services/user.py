from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from loguru import logger

from app.models import User, Subscription, Transaction, Product
from app.schemas import UserCreate, UserUpdate

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_auth_id(self, auth_provider_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.auth_provider_id == auth_provider_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_or_create_user(self, user_data: dict) -> User:
        # Check if user exists
        user = self.get_user_by_auth_id(user_data["auth_provider_id"])
        
        if user:
            # Update user info if needed
            if user_data.get("first_name") != user.first_name or \
               user_data.get("last_name") != user.last_name:
                user.first_name = user_data.get("first_name")
                user.last_name = user_data.get("last_name")
                self.db.commit()
                self.db.refresh(user)
            return user
        
        # Create new user
        user = User(
            auth_provider_id=user_data["auth_provider_id"],
            email=user_data["email"],
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name")
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        for field, value in user_update.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def handle_subscription_created(self, webhook_data: dict):
        """Handle subscription creation webhook from Paddle (Classic and Billing)"""
        data = webhook_data.get("data", webhook_data) # Billing uses 'data' key
        
        email = data.get("email")
        if not email:
            # Try Billing custom_data or nested customer info
            email = data.get("custom_data", {}).get("user_email")
            
        subscription_id = data.get("subscription_id") or data.get("id")
        # In billing, price_id is in items
        items = data.get("items", [])
        product_id = data.get("product_id") or (items[0].get("price_id") if items else None)
        
        user = self.get_user_by_email(email) if email else None
        if not user:
            # Fallback: if we can't find by email, log and return or try customer_id
            customer_id = data.get("customer_id")
            logger.warning(f"Could not find user for subscription {subscription_id} (email: {email}, customer_id: {customer_id})")
            return
            
        # Update user subscription info
        product = self.db.query(Product).filter(Product.paddle_product_id == product_id).first()
        if product and product.subscription_tier:
            user.subscription_tier = product.subscription_tier
        
        user.paddle_customer_id = data.get("customer_id")
        
        # Create or update subscription record
        subscription = self.db.query(Subscription).filter(
            Subscription.paddle_subscription_id == subscription_id
        ).first()
        
        if not subscription:
            subscription = Subscription(
                user_id=user.id,
                product_id=product.id if product else None,
                paddle_subscription_id=subscription_id,
                status="active",
                next_billing_date=datetime.fromisoformat(data.get("next_payment_date").replace('Z', '+00:00')) if data.get("next_payment_date") else None
            )
            self.db.add(subscription)
        
        # Grant initial credits for subscription
        if product and product.credits_included:
            user.credit_balance = (user.credit_balance or 0) + product.credits_included
        
        self.db.commit()
    
    def handle_subscription_payment(self, webhook_data: dict):
        """Handle successful subscription payment (Classic and Billing)"""
        data = webhook_data.get("data", webhook_data)
        subscription_id = data.get("subscription_id") or data.get("id")
        
        subscription = self.db.query(Subscription).filter(
            Subscription.paddle_subscription_id == subscription_id
        ).first()
        
        if subscription:
            subscription.status = "active"
            
            # Reset monthly tracking and grant new credits
            user = subscription.user
            user.monthly_credits_used = 0
            
            if subscription.product and subscription.product.credits_included:
                user.credit_balance = (user.credit_balance or 0) + subscription.product.credits_included
            
            self.db.commit()
    
    def handle_subscription_cancelled(self, webhook_data: dict):
        """Handle subscription cancellation (Classic and Billing)"""
        data = webhook_data.get("data", webhook_data)
        subscription_id = data.get("subscription_id") or data.get("id")
        
        subscription = self.db.query(Subscription).filter(
            Subscription.paddle_subscription_id == subscription_id
        ).first()
        
        if subscription:
            subscription.status = "cancelled"
            subscription.cancelled_at = datetime.now()
            self.db.commit()
    
    def handle_payment_succeeded(self, webhook_data: dict):
        """Handle one-time payment / transaction completed (Classic and Billing)"""
        data = webhook_data.get("data", webhook_data)
        
        email = data.get("email") or data.get("custom_data", {}).get("user_email")
        # For Billing transaction.completed, items are in data['items']
        items = data.get("items", [])
        product_id = data.get("product_id") or (items[0].get("price_id") if items else None)
        transaction_id = data.get("checkout_id") or data.get("id")
        
        # Billing might have amount in details.totals
        amount_raw = data.get("sale_gross") or data.get("details", {}).get("totals", {}).get("grand_total", 0)
        amount = float(amount_raw) / 100 if data.get("details") else float(amount_raw) # Billing uses cents/lowest unit usually but check SDK
        
        user = self.get_user_by_email(email) if email else None
        if not user:
            logger.warning(f"Could not find user for payment {transaction_id} (email: {email})")
            return
        
        product = self.db.query(Product).filter(Product.paddle_product_id == product_id).first()
        
        # Add credits to user account
        if product and product.credits_included:
            user.one_time_credits += product.credits_included
            user.credit_balance = (user.credit_balance or 0) + product.credits_included
        
        # Create transaction record
        transaction = Transaction(
            user_id=user.id,
            product_id=product.id if product else None,
            paddle_transaction_id=transaction_id,
            amount=amount,
            credits_added=product.credits_included if product else None
        )
        
        self.db.add(transaction)
        self.db.commit()