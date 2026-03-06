from pyrogram.types import Message
from config import COLORS

async def about_command(client, message: Message):
    """Handle /about command"""
    
    text = f"""
{COLORS['primary']} **About CareerWill Bot** {COLORS['primary']}

━━━━━━━━━━━━━━━━━━━━━━
**📊 Statistics:**

├ **Version:** `4.0.0`
├ **Language:** Python 3.10
├ **Framework:** Pyrogram
├ **Developer:** @Ayushxsdy
└ **Released:** March 2026

━━━━━━━━━━━━━━━━━━━━━━
**✨ Premium Features:**

{COLORS['success']} **Ultra-Fast**
├ 20 parallel workers
├ 3 retry mechanism
└ 30s timeout

{COLORS['stats']} **Live Progress**
├ Real-time updates
├ ETA calculation
└ File statistics

━━━━━━━━━━━━━━━━━━━━━━
**⚡ Made with ❤️ for students**
"""
    
    await message.reply_text(text)
