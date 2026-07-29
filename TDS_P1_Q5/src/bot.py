import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from logger import log_agent_run
from agent import DataAnalystAgent

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
PUBLIC_HOST_URL = os.environ.get("PUBLIC_HOST_URL", "https://your-host.com")
LOG_URL = f"{PUBLIC_HOST_URL.rstrip('/')}/run.jsonl"

agent = DataAnalystAgent()
# Conversation history per chat_id for multi-turn sequences
chat_history = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    chat_id = update.effective_chat.id
    user_text = update.message.text.strip()
    
    logging.info(f"Received message from chat_id {chat_id}: {user_text}")
    
    # Store message history for multi-turn context
    if chat_id not in chat_history:
        chat_history[chat_id] = []
    chat_history[chat_id].append(user_text)
    
    # The requirement specifies: "Some tasks are multi-turn — answer the LAST one."
    last_question = chat_history[chat_id][-1]
    
    # Solve question using agent
    answer_dict, thoughts, tool_calls = agent.solve(last_question)
    
    # Log run line to run.jsonl
    log_agent_run(chat_id, last_question, thoughts, tool_calls, answer_dict, LOG_URL)
    
    # Final reply MUST be exactly one JSON object and nothing else with keys: "answer" and "log_url"
    response_payload = {
        "answer": answer_dict,
        "log_url": LOG_URL
    }
    
    # Send single raw JSON text response
    await update.message.reply_text(json.dumps(response_payload, ensure_ascii=False))

def main():
    if TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("Please set TELEGRAM_BOT_TOKEN environment variable before running bot.")
        return
        
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Telegram Data Analyst Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
