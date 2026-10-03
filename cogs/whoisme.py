import random

import discord
from discord import app_commands
from discord.ext import commands

from config import WOLFEN_ID, LOSTY_ID


# =========================================================
# WHO IS ME REPLIES
# =========================================================

WHO_IS_ME_REPLIES = {

    # Losty
    LOSTY_ID: [
        "Identity confirmed: Ladybug, PEACE CO-LEADER ",
    ],

    # Wolfen
    WOLFEN_ID: [
        "dentity confirmed: Wolfen. PEACE LEADER.",
        
    ],
}


# =========================================================
# WHO IS ME COG
# =========================================================

class WhoIsMe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # PERMISSION CHECK
    # =====================================================

    def is_authorized(self, user_id: int) -> bool:
        return user_id in {WOLFEN_ID, LOSTY_ID}

    # =====================================================
    # /whoisme
    # =====================================================

    @app_commands.command(
        name="whoisme",
        description="Find out who you are."
    )
    async def whoisme(self, interaction: discord.Interaction):

        if not self.is_authorized(interaction.user.id):
            await interaction.response.send_message(
                ":x: You don't have permission to use this command.",
                ephemeral=True
            )
            return

        replies = WHO_IS_ME_REPLIES.get(interaction.user.id)

        if replies:
            reply = random.choice(replies)
        else:
            reply = (
                f":face_with_raised_eyebrow: "
                f"You are **{interaction.user.display_name}**."
            )

        await interaction.response.send_message(reply)

    # =====================================================
    # /whoiswolfen
    # =====================================================

    @app_commands.command(
        name="whoiswolfen",
        description="Find out who Wolfen is."
    )
    async def whoiswolfen(self, interaction: discord.Interaction):

        if not self.is_authorized(interaction.user.id):
            await interaction.response.send_message(
                ":x: You don't have permission to use this command.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            random.choice([
                ":crown: That's **Wolfen**. PEACE LEADER Has arrived.",
                ])
        )

    # =====================================================
    # /whoislosty
    # =====================================================

    @app_commands.command(
        name="whoislosty",
        description="Find out who Ladybug is."
    )
    async def whoisladybug(self, interaction: discord.Interaction):

        if not self.is_authorized(interaction.user.id):
            await interaction.response.send_message(
                ":x: You don't have permission to use this command.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            random.choice([
                "That's **Ladybug** Unfortunately, She is the PEACE CO-LEADER",
            ])
        )


# =========================================================
# SETUP
# =========================================================

async def setup(bot):
    await bot.add_cog(WhoIsMe(bot))