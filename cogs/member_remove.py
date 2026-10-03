import discord
from discord import app_commands

from database import (
    get_member_by_roblox_username,
    remove_member,
)

from permissions import is_pfp_owner

from .member_group import member_group


@member_group.command(
    name="remove",
    description="Remove a PFP member using their Roblox username.",
)
@app_commands.describe(
    roblox_username="Roblox username of the PFP member to remove.",
)
async def remove(
    interaction: discord.Interaction,
    roblox_username: str,
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
    # VALIDATE USERNAME
    # ============================================================

    roblox_username = roblox_username.strip()

    if not roblox_username:

        await interaction.response.send_message(
            "❌ Enter the Roblox username of the member.",
            ephemeral=True,
        )

        return

    # ============================================================
    # FIND MEMBER
    # ============================================================

    member = get_member_by_roblox_username(
        roblox_username
    )

    if not member:

        await interaction.response.send_message(
            "❌ No PFP member was found with that Roblox username.",
            ephemeral=True,
        )

        return

    # ============================================================
    # REMOVE MEMBER
    # ============================================================

    removed = remove_member(
        member["id"]
    )

    if not removed:

        await interaction.response.send_message(
            "❌ Failed to remove the member.",
            ephemeral=True,
        )

        return

    # ============================================================
    # SUCCESS
    # ============================================================

    await interaction.response.send_message(
        f"✅ Removed **{roblox_username}** "
        "from the PFP roster."
    )


# ================================================================
# END
# ================================================================