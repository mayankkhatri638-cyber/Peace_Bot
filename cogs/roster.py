import os
import traceback

import discord
from discord import app_commands
from discord.ext import commands

from config import (
    ROSTER_DISCORD_CHANNEL_ID,
    ROSTER_NON_DISCORD_CHANNEL_ID
)


class Roster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.discord_image = "discord.png"
        self.non_discord_image = "non-discord.png"

    # =========================================================
    # /rosterd
    # =========================================================

    @app_commands.command(
        name="rosterd",
        description="Upload the Discord member roster."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def rosterd(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        try:
            # Check image
            if not os.path.isfile(self.discord_image):
                await interaction.followup.send(
                    "❌ `discord.png` could not be found.",
                    ephemeral=True
                )
                return

            # Check guild
            if interaction.guild is None:
                await interaction.followup.send(
                    "❌ This command can only be used inside a server.",
                    ephemeral=True
                )
                return

            # Get channel
            channel = interaction.guild.get_channel(
                ROSTER_DISCORD_CHANNEL_ID
            )

            if channel is None:
                await interaction.followup.send(
                    "❌ Discord roster channel was not found.\n"
                    f"Channel ID: `{ROSTER_DISCORD_CHANNEL_ID}`",
                    ephemeral=True
                )
                return

            # Make sure it is a text channel
            if not isinstance(channel, discord.TextChannel):
                await interaction.followup.send(
                    "❌ The Discord roster channel is not a text channel.",
                    ephemeral=True
                )
                return

            # Send @everyone + image
            await channel.send(
                content="@everyone",
                file=discord.File(
                    self.discord_image,
                    filename="discord.png"
                ),
                allowed_mentions=discord.AllowedMentions(
                    everyone=True
                )
            )

            await interaction.followup.send(
                f"✅ Discord roster uploaded to {channel.mention}.",
                ephemeral=True
            )

        except Exception as error:
            print("\n========================================")
            print("❌ /rosterd ERROR")
            print("========================================")
            print(f"Error type: {type(error).__name__}")
            print(f"Error: {error}")
            traceback.print_exc()
            print("========================================\n")

            await interaction.followup.send(
                "❌ Something went wrong while uploading the roster.\n"
                "Check the bot console for the exact error.",
                ephemeral=True
            )

    # =========================================================
    # /rosternd
    # =========================================================

    @app_commands.command(
        name="rosternd",
        description="Upload the Non-Discord member roster."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def rosternd(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        try:
            # Check image
            if not os.path.isfile(self.non_discord_image):
                await interaction.followup.send(
                    "❌ `non-discord.png` could not be found.",
                    ephemeral=True
                )
                return

            # Check guild
            if interaction.guild is None:
                await interaction.followup.send(
                    "❌ This command can only be used inside a server.",
                    ephemeral=True
                )
                return

            # Get channel
            channel = interaction.guild.get_channel(
                ROSTER_NON_DISCORD_CHANNEL_ID
            )

            if channel is None:
                await interaction.followup.send(
                    "❌ Non-Discord roster channel was not found.\n"
                    f"Channel ID: `{ROSTER_NON_DISCORD_CHANNEL_ID}`",
                    ephemeral=True
                )
                return

            # Make sure it is a text channel
            if not isinstance(channel, discord.TextChannel):
                await interaction.followup.send(
                    "❌ The Non-Discord roster channel is not a text channel.",
                    ephemeral=True
                )
                return

            # Send @everyone + image
            await channel.send(
                content="@everyone",
                file=discord.File(
                    self.non_discord_image,
                    filename="non-discord.png"
                ),
                allowed_mentions=discord.AllowedMentions(
                    everyone=True
                )
            )

            await interaction.followup.send(
                f"✅ Non-Discord roster uploaded to {channel.mention}.",
                ephemeral=True
            )

        except Exception as error:
            print("\n========================================")
            print("❌ /rosternd ERROR")
            print("========================================")
            print(f"Error type: {type(error).__name__}")
            print(f"Error: {error}")
            traceback.print_exc()
            print("========================================\n")

            await interaction.followup.send(
                "❌ Something went wrong while uploading the roster.\n"
                "Check the bot console for the exact error.",
                ephemeral=True
            )

    # =========================================================
    # PERMISSION ERROR
    # =========================================================

    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            if interaction.response.is_done():
                await interaction.followup.send(
                    "❌ You need **Administrator** permission "
                    "to use this command.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ You need **Administrator** permission "
                    "to use this command.",
                    ephemeral=True
                )

            return

        print("\n========================================")
        print("❌ ROSTER APP COMMAND ERROR")
        print("========================================")
        print(f"Error type: {type(error).__name__}")
        print(f"Error: {error}")
        traceback.print_exc()
        print("========================================\n")

        if interaction.response.is_done():
            await interaction.followup.send(
                "❌ Something went wrong. Check the bot console.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Something went wrong. Check the bot console.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Roster(bot))