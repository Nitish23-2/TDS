import os
import sys
import json
import time
import requests
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from agent import DataAnalystAgent

app = FastAPI(title="Data Analyst Telegram Bot - Vercel Serverless")

agent = DataAnalystAgent()

# In-memory & ephemeral disk log store for Vercel Serverless
LOG_ENTRIES = []
LOG_FILE_PATH = "/tmp/run.jsonl"

def append_log_entry(chat_id: int, question: str, thoughts: list, tool_calls: list, answer: dict, log_url: str):
    entry = {
        "timestamp": time.time(),
        "chat_id": chat_id,
        "question": question,
        "thoughts": thoughts,
        "tool_calls": tool_calls,
        "answer": answer,
        "log_url": log_url
    }
    LOG_ENTRIES.append(entry)
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

@app.get("/")
def home():
    return {"status": "ok", "service": "Data Analyst Telegram Bot Vercel Serverless"}

@app.get("/run.jsonl")
def get_run_logs(request: Request):
    """Exposes agent execution run logs as public, wget-able JSONL format."""
    lines = []
    # Read from /tmp/run.jsonl if present
    if os.path.exists(LOG_FILE_PATH):
        try:
            with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
        except Exception:
            pass
    if not lines and LOG_ENTRIES:
        lines = [json.dumps(e, ensure_ascii=False) for e in LOG_ENTRIES]
    
    content = "\n".join(lines) + ("\n" if lines else "")
    return PlainTextResponse(content, media_type="application/x-jsonlines")

@app.get("/set_webhook")
def set_webhook(request: Request):
    """Helper route to auto-register Vercel Webhook with Telegram @BotFather API."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        return JSONResponse({"status": "error", "message": "TELEGRAM_BOT_TOKEN environment variable is missing"}, status_code=400)
    
    host_url = os.environ.get("PUBLIC_HOST_URL")
    if not host_url:
        # Auto-detect Vercel Host URL from request headers
        scheme = request.headers.get("x-forwarded-proto", "https")
        host = request.headers.get("host", "")
        host_url = f"{scheme}://{host}"
    
    webhook_target = f"{host_url.rstrip('/')}/webhook"
    telegram_api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_target}"
    
    try:
        res = requests.get(telegram_api_url, timeout=10).json()
        return {"status": "success", "webhook_target": webhook_target, "telegram_response": res}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.post("/webhook")
@app.post("/")
async def telegram_webhook(request: Request):
    """Processes incoming Telegram update webhooks from Telegram servers on Vercel."""
    try:
        data = await request.json()
    except Exception:
        return {"status": "invalid json"}
    
    message = data.get("message") or data.get("edited_message")
    if not message or "text" not in message:
        return {"status": "no text message"}
    
    chat_id = message["chat"]["id"]
    user_text = message["text"].strip()
    
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    host_url = os.environ.get("PUBLIC_HOST_URL")
    if not host_url:
        scheme = request.headers.get("x-forwarded-proto", "https")
        host = request.headers.get("host", "")
        host_url = f"{scheme}://{host}"
        
    log_url = f"{host_url.rstrip('/')}/run.jsonl"
    
    # Solve question using Data Analyst Agent
    answer_dict, thoughts, tool_calls = agent.solve(user_text)
    
    # Append to run.jsonl log
    append_log_entry(chat_id, user_text, thoughts, tool_calls, answer_dict, log_url)
    
    # Reply MUST be exactly ONE JSON object with two keys: "answer" and "log_url"
    response_payload = {
        "answer": answer_dict,
        "log_url": log_url
    }
    
    reply_json_text = json.dumps(response_payload, ensure_ascii=False)
    
    # Send reply back to Telegram
    if bot_token:
        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(send_url, json={"chat_id": chat_id, "text": reply_json_text}, timeout=10)
        
    return response_payload
