import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ALLOWED_GROUP_ID = int(os.getenv('ALLOWED_GROUP_ID', '0'))

# In-memory storage for member targets
member_targets = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    if update.effective_chat.id != ALLOWED_GROUP_ID:
        await update.message.reply_text("❌ This bot only works in the authorized group.")
        return
    
    await update.message.reply_text(
        "👋 Welcome to Member Target Bot!\n\n"
        "Commands:\n"
        "/addtarget <username> <target> - Add a target for a member\n"
        "/viewtarget <username> - View target for a member\n"
        "/listtargets - List all member targets\n"
        "/removetarget <username> - Remove a member's target\n"
        "/help - Show this help message"
    )

async def add_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a target for a member"""
    if update.effective_chat.id != ALLOWED_GROUP_ID:
        await update.message.reply_text("❌ This bot only works in the authorized group.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Usage: /addtarget <username> <target>\n"
            "Example: /addtarget @john 50 messages per day"
        )
        return
    
    username = context.args[0]
    if not username.startswith('@'):
        username = '@' + username
    
    target = ' '.join(context.args[1:])
    member_targets[username] = target
    
    await update.message.reply_text(
        f"✅ Target added for {username}:\n{target}"
    )
    logger.info(f"Target added for {username}: {target}")

async def view_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View target for a specific member"""
    if update.effective_chat.id != ALLOWED_GROUP_ID:
        await update.message.reply_text("❌ This bot only works in the authorized group.")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text(
            "❌ Usage: /viewtarget <username>\n"
            "Example: /viewtarget @john"
        )
        return
    
    username = context.args[0]
    if not username.startswith('@'):
        username = '@' + username
    
    if username in member_targets:
        await update.message.reply_text(
            f"🎯 Target for {username}:\n{member_targets[username]}"
        )
    else:
        await update.message.reply_text(f"❌ No target found for {username}")

async def list_targets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all member targets"""
    if update.effective_chat.id != ALLOWED_GROUP_ID:
        await update.message.reply_text("❌ This bot only works in the authorized group.")
        return
    
    if not member_targets:
        await update.message.reply_text("📋 No targets have been set yet.")
        return
    
    message = "📋 *Member Targets:*\n\n"
    for username, target in member_targets.items():
        message += f"👤 {username}\n🎯 {target}\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def remove_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a member's target"""
    if update.effective_chat.id != ALLOWED_GROUP_ID:
        await update.message.reply_text("❌ This bot only works in the authorized group.")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text(
            "❌ Usage: /removetarget <username>\n"
            "Example: /removetarget @john"
        )
        return
    
    username = context.args[0]
    if not username.startswith('@'):
        username = '@' + username
    
    if username in member_targets:
        del member_targets[username]
        await update.message.reply_text(f"✅ Target removed for {username}")
        logger.info(f"Target removed for {username}")
    else:
        await update.message.reply_text(f"❌ No target found for {username}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    if update.effective_chat.id != ALLOWED_GROUP_ID:
        await update.message.reply_text("❌ This bot only works in the authorized group.")
        return
    
    await update.message.reply_text(
        "📖 *Available Commands:*\n\n"
        "/start - Start the bot\n"
        "/addtarget <username> <target> - Add a target for a member\n"
        "/viewtarget <username> - View target for a member\n"
        "/listtargets - List all member targets\n"
        "/removetarget <username> - Remove a member's target\n"
        "/help - Show this help message\n\n"
        "ℹ️ This bot only works in the authorized group.",
        parse_mode='Markdown'
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        return
    
    if ALLOWED_GROUP_ID == 0:
        logger.warning("ALLOWED_GROUP_ID not set! Bot will reject all messages.")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addtarget", add_target))
    application.add_handler(CommandHandler("viewtarget", view_target))
    application.add_handler(CommandHandler("listtargets", list_targets))
    application.add_handler(CommandHandler("removetarget", remove_target))
    application.add_handler(CommandHandler("help", help_command))
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
