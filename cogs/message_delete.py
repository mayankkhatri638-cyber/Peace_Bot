import asyncio

import discord
from discord.ext import commands

from config import MESSAGE_DELETE_CHANNEL_ID


class MessageDelete(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # Keep track of audit-log entries we already used.
        # This prevents the same deletion entry from being
        # assigned to multiple deleted messages.
        self.used_audit_entries = set()

    # =========================================================
    # FIND WHO DELETED THE MESSAGE
    # =========================================================

    async def find_deleter(
        self,
        message: discord.Message
    ):

        if message.guild is None:
            return None

        # Discord may take a moment to create the audit entry.
        # Retry several times.
        for attempt in range(6):

            try:

                # Wait for Discord to create/update the
                # audit-log entry.
                await asyncio.sleep(1)

                async for entry in message.guild.audit_logs(
                    limit=50,
                    action=discord.AuditLogAction.message_delete
                ):

                    # Don't reuse an audit-log entry.
                    if entry.id in self.used_audit_entries:
                        continue

                    # Must have a target.
                    if entry.target is None:
                        continue

                    # The audit-log target is normally the
                    # author of the deleted message.
                    target_id = getattr(
                        entry.target,
                        "id",
                        None
                    )

                    if target_id != message.author.id:
                        continue

                    # Check the channel when Discord provides it.
                    try:

                        audit_channel = entry.extra.channel

                        if audit_channel is not None:

                            if audit_channel.id != message.channel.id:
                                continue

                    except (
                        AttributeError,
                        TypeError
                    ):

                        pass

                    # Check how old the audit-log entry is.
                    age = (
                        discord.utils.utcnow()
                        - entry.created_at
                    ).total_seconds()

                    # Ignore future entries.
                    if age < 0:
                        continue

                    # Ignore old entries.
                    if age > 15:
                        continue

                    # We found the deletion entry.
                    self.used_audit_entries.add(
                        entry.id
                    )

                    # Prevent this set from growing forever.
                    if len(self.used_audit_entries) > 500:

                        self.used_audit_entries = set(
                            list(
                                self.used_audit_entries
                            )[-250:]
                        )

                    return entry.user

            except discord.Forbidden:

                print(
                    "❌ PFP_Bot cannot view the Audit Log."
                )

                return None

            except Exception as error:

                print(
                    f"⚠️ Audit-log attempt "
                    f"{attempt + 1}/6 failed: {error}"
                )

        # No matching audit-log entry was found.
        return None

    # =========================================================
    # MESSAGE DELETE
    # =========================================================

    @commands.Cog.listener()
    async def on_message_delete(
        self,
        message: discord.Message
    ):

        # Ignore bot messages.
        if message.author.bot:
            return

        # Ignore DMs.
        if message.guild is None:
            return

        # =====================================================
        # IGNORE MODERATION DELETIONS
        # =====================================================
        #
        # Messages automatically deleted by moderation.py
        # are logged by the moderation system instead.
        #
        # This prevents them from appearing in the normal
        # Deleted Messages channel.
        #

        if message.id in getattr(
            self.bot,
            "moderated_message_ids",
            set()
        ):

            self.bot.moderated_message_ids.discard(
                message.id
            )

            return

        # =====================================================
        # FIND DELETE-LOG CHANNEL
        # =====================================================

        channel = message.guild.get_channel(
            MESSAGE_DELETE_CHANNEL_ID
        )

        if channel is None:

            print(
                f"❌ Deleted-message channel with ID "
                f"{MESSAGE_DELETE_CHANNEL_ID} was not found!"
            )

            return

        # =====================================================
        # FIND DELETER
        # =====================================================

        deleter = await self.find_deleter(
            message
        )

        # =====================================================
        # FALLBACK
        # =====================================================

        # If Discord did not provide a matching audit-log
        # entry, assume the message author deleted their
        # own message.
        #
        # This matches the behavior of your old logger.

        if deleter is None:

            deleter = message.author

        # =====================================================
        # CREATE EMBED
        # =====================================================

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red()
        )

        # =====================================================
        # AUTHOR
        # =====================================================

        embed.set_author(
            name=message.author.display_name,
            icon_url=message.author.display_avatar.url
        )

        embed.add_field(
            name="👤 Message Author",
            value=message.author.mention,
            inline=True
        )

        # =====================================================
        # DELETED BY
        # =====================================================

        embed.add_field(
            name="🗑️ Deleted By",
            value=deleter.mention,
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
        # DELETED MESSAGE
        # =====================================================

        if message.content:

            content = message.content

            # Discord embed field limit.
            if len(content) > 1024:
                content = content[:1021] + "..."

            embed.add_field(
                name="💬 Deleted Message",
                value=content,
                inline=False
            )

        else:

            embed.add_field(
                name="💬 Deleted Message",
                value="*No text content*",
                inline=False
            )

        # =====================================================
        # ATTACHMENTS
        # =====================================================

        if message.attachments:

            attachments = []

            for attachment in message.attachments:

                attachments.append(
                    attachment.url
                )

            attachment_text = "\n".join(
                attachments
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
            text="PFP • Message Delete Log"
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
                "in the delete-log channel."
            )

        except Exception as error:

            print(
                f"❌ Failed to send delete log: {error}"
            )


# =============================================================
# SETUP
# =============================================================

async def setup(bot):

    await bot.add_cog(
        MessageDelete(bot)
    )