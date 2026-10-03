import re
from pathlib import Path

import discord
from discord.ext import commands

from config import MODERATION_LOG_CHANNEL_ID


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # =====================================================
        # MODERATION FILE
        # =====================================================

        self.moderation_file = (
            Path(__file__).resolve().parent.parent
            / "moderation.txt"
        )

        self.prohibited_terms = []
        self.prohibited_phrases = []

        self.load_words()

    # =========================================================
    # LOAD MODERATION WORDS
    # =========================================================

    def load_words(self):

        self.prohibited_terms = []
        self.prohibited_phrases = []

        if not self.moderation_file.exists():

            print(
                "❌ moderation.txt was not found at:"
                f"\n{self.moderation_file}"
            )

            return

        try:

            with open(
                self.moderation_file,
                "r",
                encoding="utf-8"
            ) as file:

                for raw_line in file:

                    line = raw_line.strip()

                    # -------------------------------------------------
                    # Ignore empty lines
                    # -------------------------------------------------

                    if not line:
                        continue

                    # -------------------------------------------------
                    # Ignore comments
                    # -------------------------------------------------

                    if line.startswith("#"):
                        continue

                    # -------------------------------------------------
                    # Ignore category headings
                    # Example:
                    # [PROFANITY]
                    # [SEXUAL]
                    # -------------------------------------------------

                    if (
                        line.startswith("[")
                        and line.endswith("]")
                    ):
                        continue

                    # -------------------------------------------------
                    # Split the line into individual entries
                    #
                    # Your file has lines containing many terms.
                    # -------------------------------------------------

                    entries = line.split()

                    for entry in entries:

                        entry = entry.strip().lower()

                        if not entry:
                            continue

                        self.prohibited_terms.append(
                            entry
                        )

            # =====================================================
            # REMOVE DUPLICATES
            # =====================================================

            self.prohibited_terms = list(
                dict.fromkeys(
                    self.prohibited_terms
                )
            )

            # =====================================================
            # LONGEST FIRST
            # =====================================================

            self.prohibited_terms.sort(
                key=len,
                reverse=True
            )

            print(
                "========================================"
            )

            print(
                "✅ Moderation word list loaded."
            )

            print(
                f"   Terms loaded: "
                f"{len(self.prohibited_terms)}"
            )

            print(
                "========================================"
            )

        except Exception as error:

            print(
                "❌ Failed to load moderation.txt:"
                f"\n{error}"
            )

    # =========================================================
    # NORMALIZE TEXT
    # =========================================================

    def normalize_text(
        self,
        text: str
    ) -> str:

        text = text.lower()

        # Replace repeated whitespace with one space
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # =========================================================
    # FIND PROHIBITED TERM
    # =========================================================

    def find_prohibited_term(
        self,
        content: str
    ):

        if not content:
            return None

        # =====================================================
        # NORMAL TEXT
        # =====================================================

        text = self.normalize_text(
            content
        )

        # =====================================================
        # CHECK EVERY LOADED TERM
        # =====================================================

        for term in self.prohibited_terms:

            if not term:
                continue

            # -------------------------------------------------
            # Escape regex characters
            # -------------------------------------------------

            escaped_term = re.escape(
                term
            )

            # -------------------------------------------------
            # Word/phrase boundary
            # -------------------------------------------------

            pattern = (
                r"(?<!\w)"
                + escaped_term
                + r"(?!\w)"
            )

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            if match:

                return term

        return None

    # =========================================================
    # GET MODERATION LOG CHANNEL
    # =========================================================

    def get_log_channel(
        self,
        guild: discord.Guild
    ):

        channel = guild.get_channel(
            MODERATION_LOG_CHANNEL_ID
        )

        if channel is None:

            print(
                "❌ Moderation log channel was not found."
                f" ID: {MODERATION_LOG_CHANNEL_ID}"
            )

            return None

        if not isinstance(
            channel,
            discord.TextChannel
        ):

            print(
                "❌ Moderation log channel "
                "is not a text channel."
            )

            return None

        return channel

    # =========================================================
    # CREATE MODERATION LOG
    # =========================================================

    async def log_moderation(
        self,
        message: discord.Message,
        detected_term: str
    ):

        if message.guild is None:
            return

        channel = self.get_log_channel(
            message.guild
        )

        if channel is None:
            return

        # =====================================================
        # EMBED
        # =====================================================

        embed = discord.Embed(
            title="🚫 Automatic Moderation Action",
            description=(
                "A message was automatically audited "
                "and removed because it contained "
                "prohibited language."
            ),
            color=discord.Color.red()
        )

        # =====================================================
        # USER
        # =====================================================

        embed.add_field(
            name="👤 User",
            value=(
                f"{message.author.mention}\n"
                f"`{message.author}`"
            ),
            inline=True
        )

        # =====================================================
        # CHANNEL
        # =====================================================

        embed.add_field(
            name="📍 Channel",
            value=message.channel.mention,
            inline=True
        )

        # =====================================================
        # DETECTED TERM
        # =====================================================

        embed.add_field(
            name="🔎 Detected Term",
            value=f"`{detected_term}`",
            inline=True
        )

        # =====================================================
        # REMOVED MESSAGE
        # =====================================================

        content = (
            message.content
            if message.content
            else "*No text content*"
        )

        if len(content) > 1024:

            content = (
                content[:1021]
                + "..."
            )

        embed.add_field(
            name="💬 Removed Message",
            value=content,
            inline=False
        )

        # =====================================================
        # ATTACHMENTS
        # =====================================================

        if message.attachments:

            attachment_text = "\n".join(
                attachment.url
                for attachment in message.attachments
            )

            if len(attachment_text) > 1024:

                attachment_text = (
                    attachment_text[:1021]
                    + "..."
                )

            embed.add_field(
                name="📎 Attachments",
                value=attachment_text,
                inline=False
            )

        # =====================================================
        # FOOTER
        # =====================================================

        embed.set_footer(
            text=(
                f"User ID: {message.author.id} • "
                "PFP • Automatic Moderation"
            )
        )

        # =====================================================
        # SEND LOG
        # =====================================================

        try:

            await channel.send(
                embed=embed
            )

        except discord.Forbidden:

            print(
                "❌ PFP_Bot cannot send messages "
                "to the moderation log channel."
            )

        except discord.HTTPException as error:

            print(
                "❌ Failed to send moderation log:"
                f"\n{error}"
            )

    # =========================================================
    # MESSAGE CHECK
    # =========================================================

    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message
    ):

        # =====================================================
        # IGNORE BOT MESSAGES
        # =====================================================

        if message.author.bot:
            return

        # =====================================================
        # IGNORE DMS
        # =====================================================

        if message.guild is None:
            return

        # =====================================================
        # IGNORE EMPTY MESSAGES
        # =====================================================

        if not message.content:
            return

        # =====================================================
        # FIND PROHIBITED TERM
        # =====================================================

        detected_term = (
            self.find_prohibited_term(
                message.content
            )
        )

        # =====================================================
        # NOTHING DETECTED
        # =====================================================

        if detected_term is None:
            return

        # =====================================================
        # MARK AS MODERATION DELETION
        # =====================================================
        #
        # IMPORTANT:
        # This MUST happen before message.delete().
        #
        # message_delete.py checks this set and will
        # ignore this deletion.
        #

        self.bot.moderated_message_ids.add(
            message.id
        )

        # =====================================================
        # DELETE MESSAGE
        # =====================================================

        try:

            await message.delete()

        except discord.NotFound:

            # Message was already deleted.
            self.bot.moderated_message_ids.discard(
                message.id
            )

            return

        except discord.Forbidden:

            # Bot does not have permission to delete it.
            self.bot.moderated_message_ids.discard(
                message.id
            )

            print(
                "❌ PFP_Bot does not have permission "
                "to delete messages in "
                f"#{message.channel.name}."
            )

            return

        except discord.HTTPException as error:

            # Something went wrong while deleting.
            self.bot.moderated_message_ids.discard(
                message.id
            )

            print(
                "❌ Failed to delete moderated message:"
                f"\n{error}"
            )

            return

        # =====================================================
        # LOG MODERATION ACTION
        # =====================================================

        await self.log_moderation(
            message,
            detected_term
        )


# =============================================================
# SETUP
# =============================================================

async def setup(bot):

    await bot.add_cog(
        Moderation(bot)
    )