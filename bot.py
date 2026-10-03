import discord
from discord.ext import commands

from config import DISCORD_TOKEN, GUILD_ID
from database import initialize_database


class PFPBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()

        # Member-related features
        intents.members = True

        # Required for prefix commands such as !ping
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        # ========================================
        # MODERATION MESSAGE TRACKING
        # ========================================
        #
        # Stores message IDs that were automatically
        # deleted by the moderation system.
        #
        # message_delete.py uses this to prevent
        # moderation deletions from appearing in
        # the normal Deleted Messages log.
        #

        self.moderated_message_ids = set()

        # ========================================
        # BOT MAINTENANCE MODE
        # ========================================
        #
        # False = Bot is ON
        # True  = Bot is OFF
        #
        # /on and /off are always allowed.
        #

        self.maintenance_mode = False


    async def setup_hook(self):

        # ========================================
        # DATABASE
        # ========================================

        initialize_database()

        # ========================================
        # LOAD COGS
        # ========================================

        await self.load_extension("cogs.ping")
        await self.load_extension("cogs.member")
        await self.load_extension("cogs.memberlist")
        await self.load_extension("cogs.translate")
        await self.load_extension("cogs.whoisme")
        await self.load_extension("cogs.memberjoins")
        await self.load_extension("cogs.memberleaves")
        await self.load_extension("cogs.roster")
        await self.load_extension("cogs.message_delete")
        await self.load_extension("cogs.moderation")
        await self.load_extension("cogs.botcontrol")

        # ========================================
        # PFP SERVER
        # ========================================

        guild = discord.Object(id=GUILD_ID)

        # ----------------------------------------
        # CLEAR OLD / STALE COMMANDS
        # ----------------------------------------

        self.tree.clear_commands(guild=guild)

        # ----------------------------------------
        # COPY CURRENT COMMANDS
        # ----------------------------------------

        self.tree.copy_global_to(guild=guild)

        # ----------------------------------------
        # SYNC COMMANDS
        # ----------------------------------------

        synced = await self.tree.sync(guild=guild)

        print("----------------------------------------")
        print(
            f"Synced {len(synced)} command(s) "
            f"to PFP server ({GUILD_ID})"
        )
        print("----------------------------------------")

        for command in synced:
            print(f"/{command.name}")

        print("----------------------------------------")


    # ========================================
    # MAINTENANCE MODE CHECK
    # ========================================

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ):

        # ----------------------------------------
        # ALWAYS ALLOW /ON AND /OFF
        # ----------------------------------------

        if interaction.command:

            if interaction.command.name in {
                "on",
                "off"
            }:
                return True

        # ----------------------------------------
        # BOT IS OFF
        # ----------------------------------------

        if self.maintenance_mode:

            await interaction.response.send_message(
                "🔴 **PFP_Bot is currently OFF.**\n"
                "Please wait until it is turned back on.",
                ephemeral=True
            )

            return False

        # ----------------------------------------
        # BOT IS ON
        # ----------------------------------------

        return True


    async def on_ready(self):

        print("----------------------------------------")
        print(f"Logged in as: {self.user}")
        print(f"Bot ID: {self.user.id}")
        print(f"Connected to {len(self.guilds)} server(s)")
        print(
            f"Maintenance Mode: "
            f"{'ON' if self.maintenance_mode else 'OFF'}"
        )
        print("----------------------------------------")


# ========================================
# CREATE BOT
# ========================================

bot = PFPBot()


# ========================================
# PREFIX COMMAND ERROR HANDLER
# ========================================

@bot.event
async def on_command_error(
    ctx: commands.Context,
    error: commands.CommandError
):

    # Unknown command
    if isinstance(error, commands.CommandNotFound):
        return

    # User doesn't have permission
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ You don't have permission to use this command."
        )
        return

    # Bot doesn't have permission
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send(
            "❌ I don't have the permissions required for this command."
        )
        return

    # Missing argument
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"❌ Missing argument: `{error.param.name}`"
        )
        return

    # Other errors
    print(f"Command error: {error}")


# ========================================
# START BOT
# ========================================

bot.run(DISCORD_TOKEN)