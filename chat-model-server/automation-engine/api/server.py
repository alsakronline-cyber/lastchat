from fastapi import FastAPI
from datetime import datetime
app = FastAPI()
@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
