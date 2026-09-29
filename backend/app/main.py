from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .api.routes import router

app = FastAPI(
    title="SIH26086: Hyperlocal Monsoon Onset & Break Prediction System",
    description="Operational API for MoES Block & Village scale monsoon onset, break spell prediction, and agricultural advisories",
    version="1.0.0"
)

# Enable CORS for local development and frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

from fastapi.responses import RedirectResponse

# Mount frontend static directory if exists
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_path):
    app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="frontend")

@app.get("/")
def root():
    return RedirectResponse(url="/app/")
