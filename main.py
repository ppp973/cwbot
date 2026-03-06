import os
import logging
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TERI CREDENTIALS
API_ID = 21503125
API_HASH = "bab9855c442e9e4e87f413cb5b9dc3f9"
BOT_TOKEN = "8768725493:AAFDhnWucAWD9Tl9djbRtOr6v5bUUOFmCQY"

# Simple HTTP handler for Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running!')
    
    def log_message(self, format, *args):
        # Suppress HTTP logs
        pass

def run_http_server():
    """Run HTTP server for Render health checks"""
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"✅ HTTP Server running on port {port}")
    server.serve_forever()

# Pyrogram Client
app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    sleep_threshold=30
)

# ==================== HANDLERS ====================
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("✅ **BOT IS WORKING ON WEB SERVICE!**")
    logger.info(f"Start from {message.from_user.id}")

@app.on_message(filters.command("cwextractfree"))
async def extract(client, message):
    await message.reply_text("📥 **Extract command received**")
    logger.info(f"Extract from {message.from_user.id}")

@app.on_message(filters.text)
async def echo(client, message):
    await message.reply_text(f"You said: {message.text}")

# ==================== MAIN ====================
async def main():
    # Start HTTP server in background thread
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    # Start bot
    logger.info("🚀 Starting bot...")
    await app.start()
    
    me = await app.get_me()
    logger.info(f"✅ Bot @{me.username} is running!")
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
