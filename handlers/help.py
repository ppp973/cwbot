from pyrogram.types import Message
from config import COLORS

async def help_command(client, message: Message):
    """Handle /help command"""
    
    text = f"""
{COLORS['info']} **CareerWill Bot Help Guide** {COLORS['info']}

━━━━━━━━━━━━━━━━━━━━━━
**📥 /cwextractfree**

Step-by-Step:
1️⃣ Send `/cwextractfree`
2️⃣ Enter Batch ID (e.g., `1377`)
3️⃣ Watch extraction progress
4️⃣ Receive .txt file

━━━━━━━━━━━━━━━━━━━━━━
**📚 /allbatches**

Features:
├ Complete batch list
├ Click to copy IDs
├ Paginated view
└ Search option

━━━━━━━━━━━━━━━━━━━━━━
**💡 Tips:**

{COLORS['success']} Multiple IDs: `1377 1840 2034`
{COLORS['drm']} DRM videos are marked
{COLORS['time']} 20 parallel workers

━━━━━━━━━━━━━━━━━━━━━━
**⚡ @sdfvghhghhbnm_bot**
"""
    
    await message.reply_text(text)
