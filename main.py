#!/usr/bin/env python3
"""
CareerWill Premium Bot - Main Entry Point
COMPLETELY NEW - 100% WORKING
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

# Add path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import config
from config import (
    API_ID, API_HASH, BOT_TOKEN, CHANNEL_ID,
    BATCH_API, TOPIC_API, VIDEO_API, ALL_BATCHES_API,
    COLORS
)

# Import handlers
from handlers.start import start_command
from handlers.help import help_command
from handlers.about import about_command
from handlers.extract import extract_command, handle_batch_input
from handlers.batches import batches_command, batches_callback

# Import utils
from utils.api import test_api_connection
from utils.file import ensure_directories

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ==================== INITIALIZATION ====================

# Create directories
ensure_directories()

# Test API connection
api_status = test_api_connection()
if not api_status:
    logger.warning("⚠️ API connection issues - some features may not work")

# Initialize bot
app = Client(
    "careerwill_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=20,
    parse_mode=ParseMode.MARKDOWN
)

logger.info("✅ Bot initialized")

# ==================== USER STATE MANAGEMENT ====================

user_states = {}

def set_user_state(user_id, state):
    user_states[user_id] = state

def get_user_state(user_id):
    return user_states.get(user_id)

def clear_user_state(user_id):
    if user_id in user_states:
        del user_states[user_id]

# ==================== COMMAND HANDLERS ====================

@app.on_message(filters.command("start"))
async def start(client, message):
    try:
        await start_command(client, message)
        logger.info(f"User {message.from_user.id} started bot")
    except Exception as e:
        logger.error(f"Start error: {e}")
        await message.reply_text(f"{COLORS['error']} Error occurred")

@app.on_message(filters.command("help"))
async def help(client, message):
    try:
        await help_command(client, message)
    except Exception as e:
        logger.error(f"Help error: {e}")
        await message.reply_text(f"{COLORS['error']} Error occurred")

@app.on_message(filters.command("about"))
async def about(client, message):
    try:
        await about_command(client, message)
    except Exception as e:
        logger.error(f"About error: {e}")
        await message.reply_text(f"{COLORS['error']} Error occurred")

@app.on_message(filters.command("cwextractfree"))
async def extract(client, message):
    try:
        user_id = message.from_user.id
        msg = await message.reply_text(
            f"{COLORS['batch']} **CareerWill Extractor**\n\n"
            f"{COLORS['info']} **Please enter Batch ID(s):**\n"
            f"Example: `1377`\n"
            f"Multiple: `1377 1840 2034`"
        )
        set_user_state(user_id, {
            "step": "waiting_for_batch",
            "msg_id": msg.id
        })
    except Exception as e:
        logger.error(f"Extract error: {e}")
        await message.reply_text(f"{COLORS['error']} Error occurred")

@app.on_message(filters.command("allbatches"))
async def batches(client, message):
    try:
        await batches_command(client, message)
    except Exception as e:
        logger.error(f"Batches error: {e}")
        await message.reply_text(f"{COLORS['error']} Error occurred")

# ==================== TEXT HANDLER ====================

@app.on_message(filters.text & ~filters.command(["start", "help", "about", "cwextractfree", "allbatches"]))
async def text_handler(client, message):
    try:
        user_id = message.from_user.id
        state = get_user_state(user_id)
        
        if state and state.get("step") == "waiting_for_batch":
            await handle_batch_input(client, message, state)
            clear_user_state(user_id)
        else:
            await message.reply_text(
                f"{COLORS['info']} Use /start to see available commands"
            )
    except Exception as e:
        logger.error(f"Text handler error: {e}")
        clear_user_state(message.from_user.id)

# ==================== CALLBACK HANDLER ====================

@app.on_callback_query()
async def callback_handler(client, callback_query):
    try:
        await batches_callback(client, callback_query)
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await callback_query.answer(f"{COLORS['error']} Error", show_alert=True)

# ==================== STARTUP FUNCTION ====================

async def startup():
    """Send startup notification"""
    try:
        me = await app.get_me()
        logger.info(f"✅ Bot started: @{me.username}")
        
        # Send to channel if configured
        if CHANNEL_ID:
            try:
                await app.send_message(
                    CHANNEL_ID,
                    f"{COLORS['success']} **Bot Started!**\n\n"
                    f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"**Status:** ✅ Online\n"
                    f"**Version:** 4.0.0"
                )
            except:
                pass
        
        # Send to developer
        try:
            await app.send_message(
                8033638335,  # Your user ID
                f"{COLORS['success']} **Bot is ready!**\n\n"
                f"Send /start to test."
            )
        except:
            pass
            
    except Exception as e:
        logger.error(f"Startup error: {e}")

# ==================== MAIN FUNCTION ====================

async def main():
    try:
        logger.info("🚀 Starting CareerWill Premium Bot...")
        
        # Start bot
        await app.start()
        logger.info("✅ Bot client started")
        
        # Send startup notification
        await startup()
        
        logger.info("=" * 50)
        logger.info("✅ BOT IS RUNNING!")
        logger.info("=" * 50)
        
        # Keep running
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await app.stop()

# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    asyncio.run(main())
