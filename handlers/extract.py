import asyncio
import time
from pyrogram.types import Message
from utils.api import extract_batch, validate_batch
from utils.file import save_to_file, cleanup_file
from config import COLORS, CHANNEL_ID
import logging

logger = logging.getLogger(__name__)

async def handle_batch_input(client, message: Message, state):
    """Handle batch ID input"""
    user_id = message.from_user.id
    batch_input = message.text.strip()
    
    try:
        await message.delete()
        status = await client.get_messages(message.chat.id, state["msg_id"])
        await status.delete()
    except:
        pass
    
    # Parse batch IDs
    if " " in batch_input:
        batch_ids = batch_input.split()
    else:
        batch_ids = [batch_input]
    
    for idx, batch_id in enumerate(batch_ids, 1):
        batch_id = batch_id.strip()
        if not batch_id:
            continue
        
        # Validate
        if not validate_batch(batch_id):
            await message.reply_text(f"{COLORS['error']} Invalid ID: `{batch_id}`")
            continue
        
        # Progress message
        progress = await message.reply_text(
            f"{COLORS['processing']} Processing {idx}/{len(batch_ids)}: `{batch_id}`"
        )
        
        def update(text):
            asyncio.create_task(progress.edit(text))
        
        # Extract
        stats = extract_batch(batch_id, update)
        
        if not stats:
            await progress.edit(f"{COLORS['error']} Extraction failed")
            continue
        
        # Save file
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
        
        # Log to channel
        if CHANNEL_ID:
            try:
                await client.send_document(
                    CHANNEL_ID,
                    filename,
                    caption=f"New: {stats['name'][:50]}"
                )
            except:
                pass
        
        # Cleanup
        await cleanup_file(filename)
        await progress.edit(f"{COLORS['success']} Batch {batch_id} completed!")
