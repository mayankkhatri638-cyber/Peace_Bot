import discord
from discord.ext import commands

from config import WELCOME_CHANNEL_ID, WOLFEN_ID, WELCOME_IMAGE


class MemberJoins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        # Find the welcome channel
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)

        if channel is None:
            print(
                f"❌ Welcome channel with ID "
                f"{WELCOME_CHANNEL_ID} was not found!"
            )
            return

        # Wolfen mention
        wolfen_mention = f"<@{WOLFEN_ID}>"

        # Load welcome image
        try:
            file = discord.File(
                WELCOME_IMAGE,
                filename=WELCOME_IMAGE
            )
        except FileNotFoundError:
            print(f"❌ Could not find {WELCOME_IMAGE}")
            file = None

        # Welcome embed
        embed = discord.Embed(
            title="🌙 Welcome to PFP!",
            description=(
                f"Welcome {member.mention} to "
                f"**PFP**! 👋\n\n"
                f"We're glad to have you here! 🫶"
            ),
            color=discord.Color.dark_purple()
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

        # Server member count
        embed.add_field(
            name="👥 Members",
            value=f"**{member.guild.member_count}**",
            inline=True
        )

        # Welcome image
        if file is not None:
            embed.set_image(
                url=f"attachment://{WELCOME_IMAGE}"
            )

        # Footer
        embed.set_footer(
            text="PFP • PEACE_Bot"
        )

        # Send welcome message
        if file is not None:
            await channel.send(
                content=f"@everyone {wolfen_mention}",
                embed=embed,
                file=file,
                allowed_mentions=discord.AllowedMentions(
                    everyone=True,
                    users=True
                )
            )
        else:
            await channel.send(
                content=f"@everyone {wolfen_mention}",
                embed=embed,
                allowed_mentions=discord.AllowedMentions(
                    everyone=True,
                    users=True
                )
            )

        print(
            f"🟢 {member.name} joined {member.guild.name}!"
        )


async def setup(bot):
    await bot.add_cog(MemberJoins(bot))