import discord
from discord import app_commands

from database import (
    CLAN_RANKS,
    DIVISION_RANKS,
    DIVISIONS,
    add_member,
    is_pfp_member,
)
from permissions import is_pfp_owner

from .member_group import member_group


ROSTER_CHOICES = [
    app_commands.Choice(name="Discord", value="discord"),
    app_commands.Choice(name="Non-Discord", value="non_discord"),
]

RANK_CHOICES = [
    app_commands.Choice(name="Peace Leader", value="Peace Leader"),
    app_commands.Choice(name="Co-Leader", value="Co-Leader"),
    app_commands.Choice(name="Captain", value="Captain"),
    app_commands.Choice(name="Peace Chief", value="Peace Chief"),
    app_commands.Choice(name="Squad Leader", value="Squad Leader"),
    app_commands.Choice(name="Vice Leader", value="Vice Leader"),
    app_commands.Choice(name="Member", value="Member"),
]

DIVISION_CHOICES = [
    app_commands.Choice(name="Peacekeepers", value="Peacekeepers"),
    app_commands.Choice(name="Harmony", value="Harmony"),
    app_commands.Choice(name="Serenity", value="Serenity"),
    app_commands.Choice(
        name="Silent Diplomats",
        value="Silent Diplomats",
    ),
    app_commands.Choice(name="Zenith", value="Zenith"),
]

CLAN_RANK_NAMES = {
    "Peace Leader",
    "Co-Leader",
    "Captain",
    "Peace Chief",
}

DIVISION_RANK_NAMES = {
    "Squad Leader",
    "Vice Leader",
    "Member",
}


@member_group.command(
    name="add",
    description="Add a member to the PFP roster.",
)
@app_commands.describe(
    roster_type="Choose Discord or Non-Discord.",
    rank="PFP rank. Only required for Discord members.",
    division="Division. Required for division-level Discord members.",
    user="Discord user. Required for Discord members.",
    roblox_username="Roblox username.",
    roblox_ign="Roblox in-game name (IGN).",
)
@app_commands.choices(
    roster_type=ROSTER_CHOICES,
    rank=RANK_CHOICES,
    division=DIVISION_CHOICES,
)
async def add(
    interaction: discord.Interaction,
    roster_type: app_commands.Choice[str],
    roblox_username: str,
    roblox_ign: str,
    rank: app_commands.Choice[str] | None = None,
    division: app_commands.Choice[str] | None = None,
    user: discord.Member | None = None,
):

    if not is_pfp_owner(interaction.user.id):
        await interaction.response.send_message(
            "❌ You don't have permission to manage PFP members.",
            ephemeral=True,
        )
        return

    roster = roster_type.value

    rank_value = rank.value if rank else None
    division_value = division.value if division else None

    # ============================================================
    # NON-DISCORD
    # ============================================================

    if roster == "non_discord":

        if rank_value is not None and rank_value != "Member":
            await interaction.response.send_message(
                "❌ Non-Discord members can only have the `Member` rank.",
                ephemeral=True,
            )
            return

        if division_value is not None:
            await interaction.response.send_message(
                "❌ Non-Discord members cannot have a division.",
                ephemeral=True,
            )
            return

        try:
            member_id = add_member(
                roster_type="non_discord",
                roblox_username=roblox_username,
                roblox_ign=roblox_ign,
                rank="Member",
                division=None,
            )

        except ValueError as error:
            await interaction.response.send_message(
                f"❌ {error}",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "✅ **Non-Discord member added.**\n\n"
            f"**Rank:** `Member`\n"
            f"**Roblox Username:** `{roblox_username}`\n"
            f"**Roblox IGN:** `{roblox_ign}`"
        )
        return

    # ============================================================
    # DISCORD
    # ============================================================

    if roster == "discord":

        if user is None:
            await interaction.response.send_message(
                "❌ You must select a Discord user.",
                ephemeral=True,
            )
            return

        if rank_value is None:
            await interaction.response.send_message(
                "❌ You must select a PFP rank.",
                ephemeral=True,
            )
            return

        if rank_value in CLAN_RANK_NAMES:

            if division_value is not None:
                await interaction.response.send_message(
                    f"❌ **{rank_value}** is a clan-level rank "
                    "and cannot have a division.",
                    ephemeral=True,
                )
                return

        elif rank_value in DIVISION_RANK_NAMES:

            if division_value is None:
                await interaction.response.send_message(
                    f"❌ **{rank_value}** requires a division.",
                    ephemeral=True,
                )
                return

        else:
            await interaction.response.send_message(
                "❌ Invalid PFP rank.",
                ephemeral=True,
            )
            return

        if is_pfp_member(user.id):
            await interaction.response.send_message(
                f"❌ {user.mention} is already registered "
                "as a PFP member.",
                ephemeral=True,
            )
            return

        try:
            add_member(
                roster_type="discord",
                discord_id=user.id,
                discord_username=str(user),
                discord_nickname=user.display_name,
                roblox_username=roblox_username,
                roblox_ign=roblox_ign,
                rank=rank_value,
                division=division_value,
            )

        except ValueError as error:
            await interaction.response.send_message(
                f"❌ {error}",
                ephemeral=True,
            )
            return

        message = (
            "✅ **Discord PFP member added.**\n\n"
            f"**Discord:** {user.mention}\n"
            f"**Rank:** `{rank_value}`\n"
            f"**Roblox Username:** `{roblox_username}`\n"
            f"**Roblox IGN:** `{roblox_ign}`"
        )

        if division_value:
            message += f"\n**Division:** `{division_value}`"

        await interaction.response.send_message(message)