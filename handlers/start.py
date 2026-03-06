from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import COLORS

async def start_command(client, message: Message):
    """Handle /start command"""
    
    text = f"""
{COLORS['primary']} **Welcome to CareerWill Premium Bot** {COLORS['primary']}

━━━━━━━━━━━━━━━━━━━━━━
**✨ Features:**

{COLORS['batch']} **Batch Extraction**
├ Extract any CareerWill batch
├ Videos + PDFs support
└ DRM detection

{COLORS['stats']} **Live Progress**
├ Real-time tracking
├ Time estimation
└ Detailed stats

━━━━━━━━━━━━━━━━━━━━━━
**📋 Commands:**

{COLORS['primary']} **/start** - This message
{COLORS['info']} **/help** - Help guide
{COLORS['video']} **/cwextractfree** - Extract batch
{COLORS['batch']} **/allbatches** - View batches

━━━━━━━━━━━━━━━━━━━━━━
**⚡ Made with ❤️**
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📥 Extract", callback_data="extract"),
            InlineKeyboardButton("📚 Batches", callback_data="batches")
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ]
    ])
    
    await message.reply_text(text, reply_markup=keyboard)
