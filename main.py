# main.py in the root directory
from fastapi import FastAPI
import importlib

# List of service modules (you can automate this discovery)
services = [
    "services.upload.upload_api",
    "services.vector_search_retrieval.vector_search_api",
    #"services.general-retrieval.general_retrieval_api",
    #"services.user-management.user_management_api",
    #"services.tasks.tasks_api",
    #"services.tools.tools_api",
    #"services.agent.agent_api"
]

# Create FastAPI app
app = FastAPI(
    title="E4E API",
    description="API for E4E services",
    version="0.1.0"
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning welcome message and API information."""
    return {
        "message": "Welcome to E4E API",
        "services": [service.split(".")[-1].replace("_api", "") for service in services],
        "docs_url": "/docs"
    }

# Register all service routers
for service_module in services:
    try:
        # Fix module names with hyphens for import
        import_path = service_module.replace("-", "_")
        module = importlib.import_module(import_path)
        
        # Look for the include_router function in each service module
        if hasattr(module, "include_router"):
            module.include_router(app)
            print(f"Successfully loaded API routes from {service_module}")
        else:
            print(f"Module {service_module} does not have include_router function")
    except ImportError as e:
        print(f"Could not import {service_module}: {e}")
