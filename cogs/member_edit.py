import discord
from discord import app_commands

from database import (
    get_member_by_discord_id,
    get_member_by_roblox_username,
    update_member,
)

from permissions import is_pfp_owner

from .member_group import member_group


RANK_CHOICES = [
    app_commands.Choice(
        name="Peace Leader",
        value="Peace Leader"
    ),
    app_commands.Choice(
        name="Co-Leader",
        value="Co-Leader"
    ),
    app_commands.Choice(
        name="Captain",
        value="Captain"
    ),
    app_commands.Choice(
        name="Peace Chief",
        value="Peace Chief"
    ),
    app_commands.Choice(
        name="Squad Leader",
        value="Squad Leader"
    ),
    app_commands.Choice(
        name="Vice Leader",
        value="Vice Leader"
    ),
    app_commands.Choice(
        name="Member",
        value="Member"
    ),
]


DIVISION_CHOICES = [
    app_commands.Choice(
        name="Peacekeepers",
        value="Peacekeepers"
    ),
    app_commands.Choice(
        name="Harmony",
        value="Harmony"
    ),
    app_commands.Choice(
        name="Serenity",
        value="Serenity"
    ),
    app_commands.Choice(
        name="Silent Diplomats",
        value="Silent Diplomats"
    ),
    app_commands.Choice(
        name="Zenith",
        value="Zenith"
    ),
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
    name="edit",
    description="Edit a PFP member.",
)
@app_commands.describe(
    member="Discord username/mention OR Roblox username.",
    new_roblox_username="New Roblox username.",
    roblox_ign="New Roblox IGN.",
    rank="New PFP rank. Discord members only.",
    division="New division. Discord members only.",
)
@app_commands.choices(
    rank=RANK_CHOICES,
    division=DIVISION_CHOICES,
)
async def edit(
    interaction: discord.Interaction,
    member: str,
    new_roblox_username: str | None = None,
    roblox_ign: str | None = None,
    rank: app_commands.Choice[str] | None = None,
    division: app_commands.Choice[str] | None = None,
):

    # ============================================================
    # PERMISSION CHECK
    # ============================================================

    if not is_pfp_owner(interaction.user.id):

        await interaction.response.send_message(
            "❌ You don't have permission to manage PFP members.",
            ephemeral=True,
        )

        return

    # ============================================================
    # BASIC VALIDATION
    # ============================================================

    member = member.strip()

    if not member:

        await interaction.response.send_message(
            "❌ Enter a Discord username/mention or Roblox username.",
            ephemeral=True,
        )

        return

    if (
        new_roblox_username is None
        and roblox_ign is None
        and rank is None
        and division is None
    ):

        await interaction.response.send_message(
            "❌ You didn't provide anything to change.",
            ephemeral=True,
        )

        return

    # ============================================================
    # FIND MEMBER
    # ============================================================

    database_member = None

    # ------------------------------------------------------------
    # FIRST: TRY DISCORD USER
    # ------------------------------------------------------------

    discord_member = None

    # Mention format:
    # <@123456789>
    # <@!123456789>

    if member.startswith("<@") and member.endswith(">"):

        cleaned_id = (
            member
            .replace("<@", "")
            .replace("<@!", "")
            .replace(">", "")
        )

        if cleaned_id.isdigit():

            discord_id = int(cleaned_id)

            discord_member = interaction.guild.get_member(
                discord_id
            )

            if discord_member is None:

                try:

                    discord_member = await interaction.guild.fetch_member(
                        discord_id
                    )

                except discord.NotFound:

                    discord_member = None

                except discord.HTTPException:

                    discord_member = None

            if discord_member is not None:

                database_member = get_member_by_discord_id(
                    discord_member.id
                )

    # ------------------------------------------------------------
    # TRY DISCORD ID
    # ------------------------------------------------------------

    elif member.isdigit():

        discord_id = int(member)

        database_member = get_member_by_discord_id(
            discord_id
        )

        if database_member is not None:

            discord_member = interaction.guild.get_member(
                discord_id
            )

    # ------------------------------------------------------------
    # TRY DISCORD USERNAME
    # ------------------------------------------------------------

    if database_member is None:

        if interaction.guild is not None:

            search_name = member.lower()

            for guild_member in interaction.guild.members:

                if (
                    guild_member.name.lower()
                    == search_name
                    or guild_member.display_name.lower()
                    == search_name
                    or (
                        guild_member.global_name
                        and guild_member.global_name.lower()
                        == search_name
                    )
                ):

                    database_member = (
                        get_member_by_discord_id(
                            guild_member.id
                        )
                    )

                    if database_member is not None:

                        discord_member = guild_member

                        break

    # ------------------------------------------------------------
    # TRY ROBLOX USERNAME
    # ------------------------------------------------------------

    if database_member is None:

        database_member = get_member_by_roblox_username(
            member
        )

    # ============================================================
    # MEMBER NOT FOUND
    # ============================================================

    if database_member is None:

        await interaction.response.send_message(
            "❌ No PFP member was found with:\n"
            f"`{member}`\n\n"
            "Use their Discord username/mention or their "
            "Roblox username.",
            ephemeral=True,
        )

        return

    # ============================================================
    # NON-DISCORD MEMBER
    # ============================================================

    if database_member["roster_type"] == "non_discord":

        # Non-Discord members cannot have a rank change
        # through the Discord-member system.

        if rank is not None:

            await interaction.response.send_message(
                "❌ Non-Discord members cannot change their rank.",
                ephemeral=True,
            )

            return

        if division is not None:

            await interaction.response.send_message(
                "❌ Non-Discord members cannot have a division.",
                ephemeral=True,
            )

            return

        # --------------------------------------------------------
        # Require something to edit
        # --------------------------------------------------------

        if (
            new_roblox_username is None
            and roblox_ign is None
        ):

            await interaction.response.send_message(
                "❌ For a Non-Discord member, provide a new "
                "Roblox username or Roblox IGN.",
                ephemeral=True,
            )

            return

        # --------------------------------------------------------
        # Update Non-Discord member
        # --------------------------------------------------------

        try:

            update_member(
                member_id=database_member["id"],
                roblox_username=new_roblox_username,
                roblox_ign=roblox_ign,
                rank=None,
                division=None,
            )

        except ValueError as error:

            await interaction.response.send_message(
                f"❌ {error}",
                ephemeral=True,
            )

            return

        await interaction.response.send_message(
            "✅ Updated Non-Discord member "
            f"**{database_member['roblox_username']}**."
        )

        return

    # ============================================================
    # DISCORD MEMBER
    # ============================================================

    final_rank = (
        rank.value
        if rank is not None
        else database_member["rank"]
    )

    final_division = (
        division.value
        if division is not None
        else database_member.get("division")
    )

    # ============================================================
    # CLAN-LEVEL RANK
    # ============================================================

    if final_rank in CLAN_RANK_NAMES:

        if final_division is not None:

            await interaction.response.send_message(
                f"❌ **{final_rank}** cannot have a division.",
                ephemeral=True,
            )

            return

    # ============================================================
    # DIVISION-LEVEL RANK
    # ============================================================

    elif final_rank in DIVISION_RANK_NAMES:

        if final_division is None:

            await interaction.response.send_message(
                f"❌ **{final_rank}** requires a division.",
                ephemeral=True,
            )

            return

    # ============================================================
    # UPDATE DISCORD MEMBER
    # ============================================================

    try:

        update_member(
            member_id=database_member["id"],
            roblox_username=new_roblox_username,
            roblox_ign=roblox_ign,
            rank=rank.value if rank else None,
            division=division.value if division else None,
        )

    except ValueError as error:

        await interaction.response.send_message(
            f"❌ {error}",
            ephemeral=True,
        )

        return

    # ============================================================
    # SUCCESS
    # ============================================================

    display_name = (
        discord_member.display_name
        if discord_member is not None
        else database_member.get(
            "discord_username",
            member
        )
    )

    await interaction.response.send_message(
        f"✅ Updated **{display_name}**'s "
        "PFP member information."
    )