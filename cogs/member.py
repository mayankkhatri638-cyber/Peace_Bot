from discord.ext import commands

from .member_group import member_group

# Import these so their commands are registered
from . import member_add
from . import member_info
from . import member_edit
from . import member_remove


class MemberCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(MemberCommands(bot))

    bot.tree.add_command(member_group)