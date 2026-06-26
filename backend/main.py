from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# FastAPI app initialization
app = FastAPI(
    title="Fnance Dashboard API",
    description="Personal finance dashboard with AI tranzaction categorization",
    version="0.1.0"
)

# FE <-> BE communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Finance Dashboard API is running"}