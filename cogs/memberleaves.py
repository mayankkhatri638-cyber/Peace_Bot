import discord
from discord.ext import commands

from config import LEAVE_CHANNEL_ID, WOLFEN_ID


class MemberLeaves(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):

        # Find the leave channel
        channel = member.guild.get_channel(LEAVE_CHANNEL_ID)

        if channel is None:
            print(
                f"❌ Leave channel with ID "
                f"{LEAVE_CHANNEL_ID} was not found!"
            )
            return

        # Wolfen mention
        wolfen_mention = f"<@{WOLFEN_ID}>"

        # Leave embed
        embed = discord.Embed(
            title="🔴 Member Left",
            description=(
                f"**{member.name}** has left "
                f"**PFP**."
            ),
            color=discord.Color.red()
        )

        # Member profile picture
        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        # Member name
        embed.add_field(
            name="👤 Member",
            value=f"**{member.name}**",
            inline=True
        )

        # Members remaining
        embed.add_field(
            name="👥 Members Remaining",
            value=f"**{member.guild.member_count}**",
            inline=True
        )

        # Footer
        embed.set_footer(
            text="PFP • PEACE_Bot"
        )

        # Send leave message + tag Wolfen
        await channel.send(
            content=wolfen_mention,
            embed=embed,
            allowed_mentions=discord.AllowedMentions(
                users=True
            )
        )

        print(
            f"🔴 {member.name} left {member.guild.name}!"
        )


async def setup(bot):
    await bot.add_cog(MemberLeaves(bot))