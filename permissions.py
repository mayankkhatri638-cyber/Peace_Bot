import os

from dotenv import load_dotenv

load_dotenv()


# ========================================
# PFP OWNER IDs
# ========================================

WOLFEN_ID = int(os.getenv("WOLFEN_ID", "0"))
LOSTY_ID = int(os.getenv("LOSTY_ID", "0"))


# ========================================
# PFP OWNER CHECK
# ========================================

def is_pfp_owner(user_id: int) -> bool:
    """
    Returns True if the Discord user is
    authorized to manage the PFP roster.
    """

    return user_id in {
        WOLFEN_ID,
        LOSTY_ID,
    }


# ========================================
# PERMISSION ERROR MESSAGE
# ========================================

def permission_denied_message() -> str:
    return "❌ You don't have permission to manage PFP members."