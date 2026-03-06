from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters
from utils.api import get_all_batches
from config import COLORS
import logging

logger = logging.getLogger(__name__)

# Store user sessions
user_sessions = {}

async def batches_command(client, message: Message):
    """Handle /allbatches command"""
    
    status = await message.reply_text(f"{COLORS['info']} Fetching batches...")
    
    batches = get_all_batches()
    if not batches:
        await status.edit(f"{COLORS['error']} Failed to fetch batches")
        return
    
    # Sort by ID
    sorted_batches = dict(sorted(
        batches.items(),
        key=lambda x: int(x[0]) if x[0].isdigit() else x[0]
    ))
    
    user_id = message.from_user.id
    user_sessions[user_id] = {
        "batches": sorted_batches,
        "ids": list(sorted_batches.keys()),
        "page": 1,
        "per_page": 10
    }
    
    await show_page(message, status, user_id, 1)

async def show_page(client, msg, user_id, page):
    """Show paginated batches"""
    
    session = user_sessions.get(user_id)
    if not session:
        return
    
    batches = session["batches"]
    ids = session["ids"]
    per_page = session["per_page"]
    
    total = len(ids)
    pages = (total + per_page - 1) // per_page
    page = max(1, min(page, pages))
    session["page"] = page
    
    start = (page - 1) * per_page
    end = min(start + per_page, total)
    
    text = f"""
{COLORS['batch']} **Available Batches** {COLORS['batch']}
━━━━━━━━━━━━━━━━━━━━━━
Page {page}/{pages} • Total: {total}
━━━━━━━━━━━━━━━━━━━━━━

"""
    
    for i in range(start, end):
        bid = ids[i]
        name = batches[bid]
        if len(name) > 40:
            name = name[:37] + "..."
        text += f"`{bid}` ─ **{name}**\n"
    
    text += f"\n━━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"{COLORS['info']} Click IDs below to copy"
    
    # Create buttons
    buttons = []
    
    # ID buttons
    row = []
    for i in range(start, min(start + 5, end)):
        row.append(InlineKeyboardButton(
            ids[i],
            callback_data=f"copy_{ids[i]}"
        ))
    if row:
        buttons.append(row)
    
    # Navigation
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"page_{page-1}"))
    nav.append(InlineKeyboardButton(f"{page}/{pages}", callback_data="current"))
    if page < pages:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"page_{page+1}"))
    buttons.append(nav)
    
    # Actions
    buttons.append([
        InlineKeyboardButton("📥 Extract", callback_data="extract"),
        InlineKeyboardButton("🔄 Refresh", callback_data="refresh")
    ])
    
    await msg.edit(text, reply_markup=InlineKeyboardMarkup(buttons))

async def batches_callback(client, cb):
    """Handle batch callbacks"""
    data = cb.data
    user_id = cb.from_user.id
    
    await cb.answer()
    
    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await show_page(client, cb.message, user_id, page)
        
    elif data.startswith("copy_"):
        batch_id = data.split("_")[1]
        await cb.answer(f"✅ Copied: {batch_id}", show_alert=True)
        
    elif data == "extract":
        await cb.message.delete()
        from .extract import extract_command
        await extract_command(client, cb.message)
        
    elif data == "refresh":
        await cb.message.edit(f"{COLORS['info']} Refreshing...")
        await batches_command(client, cb.message)
        
    elif data == "help":
        await cb.message.delete()
        from .help import help_command
        await help_command(client, cb.message)
        
    elif data == "about":
        await cb.message.delete()
        from .about import about_command
        await about_command(client, cb.message)
