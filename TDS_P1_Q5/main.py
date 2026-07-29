import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
import multiprocessing

app = FastAPI(title="Data Analyst Telegram Bot Server")

LOG_FILE = os.environ.get("LOG_FILE_PATH", "run.jsonl")

@app.get("/")
def home():
    return {"status": "ok", "service": "Data Analyst Telegram Bot"}

@app.get("/run.jsonl")
def get_run_logs():
    if not os.path.exists(LOG_FILE):
        # Create empty log file if not present
        with open(LOG_FILE, "w") as f:
            pass
    return FileResponse(LOG_FILE, media_type="application/x-jsonlines")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting FastAPI Log Server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
