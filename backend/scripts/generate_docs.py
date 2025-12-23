import json
import os
import sys
from pathlib import Path

# Add backend directory to sys.path to allow imports
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))

from main import app

def generate_openapi_spec():
    print("Generating OpenAPI Spec...")
    openapi_data = app.openapi()
    
    output_path = backend_dir / "openapi.json"
    with open(output_path, "w") as f:
        json.dump(openapi_data, f, indent=2)
    print(f"OpenAPI Spec saved to: {output_path}")
    return openapi_data, output_path

def convert_to_postman(openapi_data):
    print("Converting to Postman Collection...")
    
    info = openapi_data.get("info", {})
    title = info.get("title", "API Collection")
    description = info.get("description", "")
    version = info.get("version", "1.0.0")
    
    collection = {
        "info": {
            "name": title,
            "description": description,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [],
        "variable": [
            {
                "key": "baseUrl",
                "value": "http://localhost:8000",
                "type": "string"
            }
        ]
    }

    paths = openapi_data.get("paths", {})
    
    for path, methods in paths.items():
        # Clean path for name (e.g., /api/v1/jobs/{job_id} -> api/v1/jobs/:job_id)
        # Postman uses :param for path variables
        postman_path = path.strip("/").split("/")
        
        for method, details in methods.items():
            method = method.upper()
            operation_id = details.get("operationId", "")
            summary = details.get("summary", operation_id)
            
            # Construct Request
            request_item = {
                "name": summary,
                "request": {
                    "method": method,
                    "header": [],
                    "url": {
                        "raw": "{{baseUrl}}" + path,
                        "host": ["{{baseUrl}}"],
                        "path": postman_path,
                        "variable": []
                    }
                }
            }
            
            # Handle Path Variables
            if "{" in path:
                # Simple extraction of path variables
                import re
                params = re.findall(r"\{([^}]+)\}", path)
                for param in params:
                    request_item["request"]["url"]["variable"].append({
                        "key": param,
                        "value": "",
                        "description": f"Value for {param}"
                    })

            # Handle Query Parameters
            if "parameters" in details:
                query_params = []
                for param in details["parameters"]:
                    if param.get("in") == "query":
                        query_params.append({
                            "key": param["name"],
                            "value": "",
                            "description": param.get("description", "")
                        })
                if query_params:
                    request_item["request"]["url"]["query"] = query_params

            # Handle Request Body (JSON)
            if "requestBody" in details:
                content = details["requestBody"].get("content", {})
                if "application/json" in content:
                    schema = content["application/json"].get("schema", {})
                    # Try to generate example body from schema ref? 
                    # For now just set mode to raw/json
                    request_item["request"]["body"] = {
                        "mode": "raw",
                        "raw": "{\n  \n}",
                        "options": {
                            "raw": {
                                "language": "json"
                            }
                        }
                    }

            # Handle Auth (Bearer)
            # Check security schemes generally, but for now assuming global or specific
            if "security" in details:
                request_item["request"]["auth"] = {
                    "type": "bearer",
                    "bearer": [
                        {
                            "key": "token",
                            "value": "{{token}}",
                            "type": "string"
                        }
                    ]
                }

            collection["item"].append(request_item)

    output_path = backend_dir / "postman_collection.json"
    with open(output_path, "w") as f:
        json.dump(collection, f, indent=2)
    print(f"Postman Collection saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    spec_data, _ = generate_openapi_spec()
    convert_to_postman(spec_data)
