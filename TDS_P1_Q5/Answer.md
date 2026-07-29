# Question 5: Data Analyst Telegram Bot (37.5 Marks)

## Submission Identifiers

Paste your registration identifiers in your portal below:

```text
https://github.com/YOUR_GITHUB_USERNAME/data-analyst-telegram-bot, @YourDataAnalystBot
```

- **GitHub Repository URL**: Public repository containing the agent codebase (`q5/src/`).
- **Telegram Bot Username**: Active Telegram bot username (must end in `bot`).

---

## Codebase Architecture Summary

- **Bot Handler (`q5/src/bot.py`)**: Uses `python-telegram-bot` to receive plain-text Telegram messages. Maintains per-chat message history for multi-turn conversations and answers the **last** question in the turn sequence.
- **Data Analyst Agent (`q5/src/agent.py`)**: Autonomous data processor that extracts embedded datasets/URLs, runs Python execution loops (with `pandas` & `duckdb`), and returns the exact JSON shape requested.
- **Log Server & Logger (`q5/src/logger.py` & `q5/main.py`)**: Logs every agent run as a single JSON object line to `run.jsonl` and exposes it via a public, `wget`-able HTTP endpoint (`/run.jsonl`).

---

## Output Contract & Worked Example

### Grading Account Message Received:
```pgsql
Which state has the highest maternal mortality rate based on MOSPI data? Reply with ONLY this JSON object and nothing else: {"answer": {"state": "<state name>"}, "log_url": "<public wget-able URL to your agent's JSONL log>"}
```

### Bot Response (Exactly ONE JSON Object):
```json
{
  "answer": {
    "state": "Assam"
  },
  "log_url": "https://your-host.com/run.jsonl"
}
```

---

## Deployment Instructions

1. **Environment Variables**:
   - `TELEGRAM_BOT_TOKEN`: Token obtained from Telegram `@BotFather`.
   - `PUBLIC_HOST_URL`: Your deployed server URL (e.g. `https://data-analyst-bot.onrender.com` or `https://your-domain.com`).
   - `OPENAI_API_KEY`: API key for LLM reasoning & tool calls.

2. **Docker Deployment**:
   ```bash
   docker build -t data-analyst-bot .
   docker run -d -p 8000:8000 -e TELEGRAM_BOT_TOKEN="your_token" -e PUBLIC_HOST_URL="https://your-app.onrender.com" data-analyst-bot
   ```

3. **Local Testing & Evaluation**:
   - Run `python test_bot.py` locally to verify message parsing and single-JSON response structure.
   - Test against the official evaluation suite: `github.com/Jivraj-18/tds-p1-t2-2026-telegram-bot`.
