from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from application.api.routes import router as api_router
from application.alert.alert_system import AlertSystem

app = FastAPI(
    title="Stock Analysis and Prediction System",
    description="A comprehensive system for stock analysis, prediction, and trading signals",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize alert system
alert_system = AlertSystem()

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Stock Analysis and Prediction System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
