import discord
from discord.ext import commands
from discord import app_commands


class Ping(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # =========================
    # /ping
    # =========================

    @app_commands.command(
        name="ping",
        description="Check if PFP_Bot is online."
    )
    async def ping(
        self,
        interaction: discord.Interaction
    ):

        latency = round(self.bot.latency * 1000)

        await interaction.response.send_message(
            f"🏓 Pong! `{latency}ms`"
        )


    # =========================
    # !ping
    # @PFP_Bot /ping
    # =========================

    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message
    ):

        if message.author.bot:
            return

        if self.bot.user is None:
            return

        content = message.content.strip()


        # -------------------------
        # !ping
        # -------------------------

        if content.lower() == "!ping":

            latency = round(self.bot.latency * 1000)

            await message.reply(
                f"🏓 Pong! `{latency}ms`"
            )

            return


        # -------------------------
        # @PFP_Bot /ping
        # -------------------------

        if self.bot.user in message.mentions:

            content = content.replace(
                f"<@{self.bot.user.id}>",
                ""
            )

            content = content.replace(
                f"<@!{self.bot.user.id}>",
                ""
            )

            content = content.strip()


            if content.lower() == "/ping":

                latency = round(
                    self.bot.latency * 1000
                )

                await message.reply(
                    f"🏓 Pong! `{latency}ms`"
                )


# =========================
# SETUP
# =========================

async def setup(bot):
    await bot.add_cog(Ping(bot))