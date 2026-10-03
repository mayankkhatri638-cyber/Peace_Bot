import discord
from discord import app_commands

from database import (
    get_member_by_discord_id,
    get_member_by_roblox_username,
)

from .member_group import member_group


def member_embed(member):

    embed = discord.Embed(
        title="PFP Member",
        color=discord.Color.blurple(),
    )

    embed.add_field(
        name="Roster",
        value=(
            "Discord"
            if member["roster_type"] == "discord"
            else "Non-Discord"
        ),
        inline=True,
    )

    if member["roster_type"] == "discord":

        embed.add_field(
            name="Discord Username",
            value=member["discord_username"] or "Unknown",
            inline=False,
        )

        embed.add_field(
            name="Server Nickname",
            value=member["discord_nickname"] or "None",
            inline=False,
        )

    embed.add_field(
        name="Roblox Username",
        value=member["roblox_username"],
        inline=True,
    )

    embed.add_field(
        name="Roblox IGN",
        value=member["roblox_ign"],
        inline=True,
    )

    embed.add_field(
        name="PFP Rank",
        value=member["rank"],
        inline=True,
    )

    embed.add_field(
        name="Division",
        value=member.get("division") or "None",
        inline=True,
    )

    return embed


@member_group.command(
    name="info",
    description="View a PFP member's information.",
)
@app_commands.describe(
    user="Discord user to look up.",
    roblox_username="Roblox username for a Non-Discord member.",
)
async def info(
    interaction: discord.Interaction,
    user: discord.Member | None = None,
    roblox_username: str | None = None,
):

    if user is not None and roblox_username is not None:
        await interaction.response.send_message(
            "❌ Use either a Discord user OR a Roblox username, not both.",
            ephemeral=True,
        )
        return

    if user is None and roblox_username is None:
        await interaction.response.send_message(
            "❌ Select a Discord user or enter a Roblox username.",
            ephemeral=True,
        )
        return

    if user is not None:
        member = get_member_by_discord_id(user.id)

        if not member:
            await interaction.response.send_message(
                "❌ This Discord user is not registered as a PFP member.",
                ephemeral=True,
            )
            return

    else:
        member = get_member_by_roblox_username(
            roblox_username
        )

        if not member:
            await interaction.response.send_message(
                "❌ No Non-Discord member was found with that Roblox username.",
                ephemeral=True,
            )
            return

    await interaction.response.send_message(
        embed=member_embed(member)
    )