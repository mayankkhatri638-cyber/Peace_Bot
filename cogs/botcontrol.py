import discord
from discord import app_commands
from discord.ext import commands

from permissions import is_pfp_owner


class BotControl(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================================================
    # /off
    # =========================================================

    @app_commands.command(
        name="off",
        description="Turn PFP_Bot into maintenance mode."
    )
    async def off(
        self,
        interaction: discord.Interaction
    ):

        # Only Wolfen and Losty
        if not is_pfp_owner(interaction.user.id):

            await interaction.response.send_message(
                "❌ You don't have permission to turn off PFP_Bot.",
                ephemeral=True
            )

            return

        # Already off
        if self.bot.maintenance_mode:

            await interaction.response.send_message(
                "🔴 PFP_Bot is already turned OFF.",
                ephemeral=True
            )

            return

        self.bot.maintenance_mode = True

        await interaction.response.send_message(
            "🔴 **PFP_Bot has been turned OFF.**\n"
            "Bot commands are now disabled."
        )

        print(
            f"🔴 PFP_Bot turned OFF by "
            f"{interaction.user} ({interaction.user.id})"
        )

    # =========================================================
    # /on
    # =========================================================

    @app_commands.command(
        name="on",
        description="Turn PFP_Bot back on."
    )
    async def on(
        self,
        interaction: discord.Interaction
    ):

        # Only Wolfen and Losty
        if not is_pfp_owner(interaction.user.id):

            await interaction.response.send_message(
                "❌ You don't have permission to turn on PFP_Bot.",
                ephemeral=True
            )

            return

        # Already on
        if not self.bot.maintenance_mode:

            await interaction.response.send_message(
                "🟢 PFP_Bot is already turned ON.",
                ephemeral=True
            )

            return

        self.bot.maintenance_mode = False

        await interaction.response.send_message(
            "🟢 **PFP_Bot has been turned ON.**\n"
            "All bot commands are active again."
        )

        print(
            f"🟢 PFP_Bot turned ON by "
            f"{interaction.user} ({interaction.user.id})"
        )


async def setup(bot):
    await bot.add_cog(
        BotControl(bot)
    )