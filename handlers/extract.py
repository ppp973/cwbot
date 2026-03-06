import asyncio
import time
from pyrogram.types import Message
from utils.api import extract_batch, validate_batch
from utils.file import save_to_file, cleanup_file
from config import COLORS, CHANNEL_ID
import logging

logger = logging.getLogger(__name__)

# Store user states
user_states = {}

async def extract_command(client, message: Message):
    """Handle /cwextractfree command"""
    user_id = message.from_user.id
    
    msg = await message.reply_text(
        f"{COLORS['batch']} **CareerWill Extractor**\n\n"
        f"{COLORS['info']} **Please enter Batch ID(s):**\n"
        f"Example: `1377`\n"
        f"Multiple: `1377 1840 2034`"
    )
    
    # Store user state
    user_states[user_id] = {
        "step": "waiting_for_batch",
        "msg_id": msg.id
    }
    
    logger.info(f"User {user_id} started extraction")

async def handle_batch_input(client, message: Message, state):
    """Handle batch ID input from user"""
    user_id = message.from_user.id
    batch_input = message.text.strip()
    
    try:
        await message.delete()
        status = await client.get_messages(message.chat.id, state["msg_id"])
        await status.delete()
    except Exception as e:
        logger.error(f"Error getting status message: {e}")
    
    # Parse batch IDs
    if " " in batch_input:
        batch_ids = batch_input.split()
    else:
        batch_ids = [batch_input]
    
    for idx, batch_id in enumerate(batch_ids, 1):
        batch_id = batch_id.strip()
        if not batch_id:
            continue
        
        # Validate batch ID
        if not validate_batch(batch_id):
            await message.reply_text(f"{COLORS['error']} Invalid ID: `{batch_id}`")
            continue
        
        # Progress message
        progress = await message.reply_text(
            f"{COLORS['processing']} Processing {idx}/{len(batch_ids)}: `{batch_id}`"
        )
        
        def update_progress(text):
            asyncio.create_task(progress.edit(text))
        
        # Extract batch
        stats = extract_batch(batch_id, update_progress)
        
        if not stats:
            await progress.edit(f"{COLORS['error']} Extraction failed")
            continue
        
        # Save to file
        filename = await save_to_file(
            stats['name'],
            batch_id,
            stats['items']
        )
        
        # Create caption
        caption = f"""
{COLORS['batch']} **Extraction Complete** {COLORS['batch']}

━━━━━━━━━━━━━━━━━━━━━━
**📋 Batch:** `{batch_id}`
**📝 Name:** {stats['name'][:50]}
**📊 Total:** {stats['total']}

**Statistics:**
├ {COLORS['video']} Videos: {stats['videos']}
├ {COLORS['pdf']} PDFs: {stats['pdfs']}
├ {COLORS['drm']} DRM: {stats['drm']}
└ {COLORS['time']} Time: {stats['time']:.1f}s

━━━━━━━━━━━━━━━━━━━━━━
**⚡ @sdfvghhghhbnm_bot**
"""
        
        # Send file
        await message.reply_document(
            document=filename,
            caption=caption
        )
        
        # Log to channel if configured
        if CHANNEL_ID:
            try:
                await client.send_document(
                    CHANNEL_ID,
                    filename,
                    caption=f"New: {stats['name'][:50]}"
                )
            except Exception as e:
                logger.error(f"Channel log error: {e}")
        
        # Cleanup file
        await cleanup_file(filename)
        
        # Update progress message
        await progress.edit(f"{COLORS['success']} Batch {batch_id} completed!")
    
    # Clear user state
    if user_id in user_states:
        del user_states[user_id]

# Export functions
__all__ = ['extract_command', 'handle_batch_input']
