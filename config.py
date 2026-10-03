import os

from dotenv import load_dotenv

load_dotenv()


# ========================================
# DISCORD BOT
# ========================================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN is missing from .env")


# ========================================
# PFP SERVER
# ========================================

GUILD_ID = int(os.getenv("GUILD_ID", "0"))

if GUILD_ID == 0:
    raise ValueError("GUILD_ID is missing from .env")


# ========================================
# PFP OWNERS
# ========================================

WOLFEN_ID = int(os.getenv("WOLFEN_ID", "0"))
LOSTY_ID = int(os.getenv("LOSTY_ID", "0"))

# ========================================
# welcome/leave members
# ========================================

WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", "0"))
WELCOME_IMAGE = os.getenv("WELCOME_IMAGE", "welcome.png")
LEAVE_CHANNEL_ID = int(os.getenv("LEAVE_CHANNEL_ID", "0"))

# ========================================
# roster image
# ========================================

ROSTER_DISCORD_CHANNEL_ID = int(
    os.getenv("ROSTER_DISCORD_CHANNEL_ID", "0")
)

ROSTER_NON_DISCORD_CHANNEL_ID = int(
    os.getenv("ROSTER_NON_DISCORD_CHANNEL_ID", "0")
)

# ========================================
# rMessage Delete
# ========================================

MESSAGE_DELETE_CHANNEL_ID = int(
    os.getenv("MESSAGE_DELETE_CHANNEL_ID", "0")
)

# ========================================
# Moderation
# ========================================

MODERATION_LOG_CHANNEL_ID = int(
    os.getenv("MODERATION_LOG_CHANNEL_ID", "0")
)

if MODERATION_LOG_CHANNEL_ID == 0:
    raise ValueError(
        "MODERATION_LOG_CHANNEL_ID is missing from .env"
    )