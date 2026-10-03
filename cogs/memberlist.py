import discord
from discord.ext import commands

from database import (
    get_discord_members,
    get_non_discord_members,
)


# ============================================================
# MEMBER LIST COG
# ============================================================

class MemberList(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # DISCORD MEMBER LIST
    # ========================================================

    async def show_discord_members(
        self,
        destination,
    ):

        members = get_discord_members()

        if not members:
            await destination.send(
                "📋 **Discord PFP Members**\n\n"
                "No Discord members have been added yet."
            )
            return

        embed = discord.Embed(
            title="📋 PFP Discord Members",
            description=(
                f"Total Discord Members: **{len(members)}**"
            ),
            color=discord.Color.blurple(),
        )

        for member in members:

            name = (
                member.get("discord_nickname")
                or member.get("discord_username")
                or "Unknown"
            )

            roblox_username = (
                member.get("roblox_username")
                or "Unknown"
            )

            roblox_ign = (
                member.get("roblox_ign")
                or "Unknown"
            )

            rank = (
                member.get("rank")
                or "Unknown"
            )

            division = member.get("division")

            if division:
                rank_text = (
                    f"**Rank:** {rank}\n"
                    f"**Division:** {division}"
                )
            else:
                rank_text = (
                    f"**Rank:** {rank}\n"
                    f"**Division:** None"
                )

            embed.add_field(
                name=name,
                value=(
                    f"{rank_text}\n"
                    f"**Roblox:** {roblox_username}\n"
                    f"**IGN:** {roblox_ign}"
                ),
                inline=False,
            )

        await destination.send(embed=embed)

    # ========================================================
    # NON-DISCORD MEMBER LIST
    # ========================================================

    async def show_non_discord_members(
        self,
        destination,
    ):

        members = get_non_discord_members()

        if not members:
            await destination.send(
                "📋 **Non-Discord PFP Members**\n\n"
                "No non-Discord members have been added yet."
            )
            return

        embed = discord.Embed(
            title="📋 PFP Non-Discord Members",
            description=(
                f"Total Non-Discord Members: **{len(members)}**"
            ),
            color=discord.Color.dark_grey(),
        )

        for member in members:

            roblox_username = (
                member.get("roblox_username")
                or "Unknown"
            )

            roblox_ign = (
                member.get("roblox_ign")
                or "Unknown"
            )

            # Non-Discord members are ALWAYS Member
            rank = "Member"

            embed.add_field(
                name=f"#{member['id']}",
                value=(
                    f"**Rank:** {rank}\n"
                    f"**Roblox:** {roblox_username}\n"
                    f"**IGN:** {roblox_ign}"
                ),
                inline=False,
            )

        await destination.send(embed=embed)

    # ========================================================
    # SLASH COMMAND
    #
    # /memberlist discord
    # /memberlist non-discord
    # ========================================================

    @discord.app_commands.command(
        name="memberlist",
        description="View the PFP member roster.",
    )
    @discord.app_commands.describe(
        roster="Choose which PFP roster to view.",
    )
    @discord.app_commands.choices(
        roster=[
            discord.app_commands.Choice(
                name="Discord",
                value="discord",
            ),
            discord.app_commands.Choice(
                name="Non-Discord",
                value="non_discord",
            ),
        ]
    )
    async def memberlist_slash(
        self,
        interaction: discord.Interaction,
        roster: discord.app_commands.Choice[str],
    ):

        await interaction.response.defer()

        if roster.value == "discord":

            await self.show_discord_members(
                interaction.followup
            )

        else:

            await self.show_non_discord_members(
                interaction.followup
            )

    # ========================================================
    # PREFIX COMMAND
    #
    # !memberlist discord
    # !memberlist non-discord
    # ========================================================

    @commands.command(
        name="memberlist",
        aliases=["mlist"],
    )
    async def memberlist_prefix(
        self,
        ctx,
        roster: str | None = None,
    ):

        if roster is None:

            await ctx.send(
                "❌ Please specify a roster.\n\n"
                "Use:\n"
                "`!memberlist discord`\n"
                "`!memberlist non-discord`"
            )

            return

        roster = roster.lower()

        if roster == "discord":

            await self.show_discord_members(
                ctx
            )

        elif roster in {
            "non-discord",
            "non_discord",
            "nondiscord",
        }:

            await self.show_non_discord_members(
                ctx
            )

        else:

            await ctx.send(
                "❌ Invalid roster.\n\n"
                "Use:\n"
                "`!memberlist discord`\n"
                "`!memberlist non-discord`"
            )

    # ========================================================
    # MENTION COMMAND
    #
    # @PFP_Bot /memberlist discord
    # @PFP_Bot /memberlist non-discord
    # ========================================================

    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message,
    ):

        if message.author.bot:
            return

        if self.bot.user is None:
            return

        if not self.bot.user.mentioned_in(message):
            return

        content = message.content

        # Remove bot mention
        content = content.replace(
            self.bot.user.mention,
            "",
        ).strip()

        # Remove possible slash
        if content.startswith("/"):
            content = content[1:]

        parts = content.split()

        if not parts:
            return

        if parts[0].lower() != "memberlist":
            return

        if len(parts) < 2:

            await message.channel.send(
                "❌ Please specify a roster.\n\n"
                "Use:\n"
                "`@PFP_Bot /memberlist discord`\n"
                "`@PFP_Bot /memberlist non-discord`"
            )

            return

        roster = parts[1].lower()

        if roster == "discord":

            await self.show_discord_members(
                message.channel
            )

        elif roster in {
            "non-discord",
            "non_discord",
            "nondiscord",
        }:

            await self.show_non_discord_members(
                message.channel
            )

        else:

            await message.channel.send(
                "❌ Invalid roster.\n\n"
                "Use:\n"
                "`@PFP_Bot /memberlist discord`\n"
                "`@PFP_Bot /memberlist non-discord`"
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        MemberList(bot)
    )