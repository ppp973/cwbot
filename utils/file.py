import os
import re
import aiofiles
import logging
from datetime import datetime
from config import DOWNLOAD_DIR, MAX_FILENAME_LENGTH

logger = logging.getLogger(__name__)

def ensure_directories():
    """Create required directories"""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs("/tmp/bot_sessions", exist_ok=True)
    logger.info(f"✅ Directories ready")

def sanitize_filename(name):
    """Remove invalid characters"""
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    name = name.replace(' ', '_')
    name = re.sub(r'_+', '_', name)
    return name.strip('_')[:MAX_FILENAME_LENGTH]

def generate_filename(batch_name, batch_id):
    """Generate unique filename"""
    safe = sanitize_filename(batch_name)
    time = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{safe}_{batch_id}_{time}.txt"

async def save_to_file(batch_name, batch_id, items):
    """Save items to file"""
    filename = generate_filename(batch_name, batch_id)
    path = os.path.join(DOWNLOAD_DIR, filename)
    
    async with aiofiles.open(path, 'w', encoding='utf-8') as f:
        for item in items:
            await f.write(item + '\n')
    
    logger.info(f"✅ Saved: {filename}")
    return path

async def cleanup_file(path):
    """Delete file"""
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"🗑️ Deleted: {os.path.basename(path)}")
    except:
        pass
