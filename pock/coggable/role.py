import discord
from discord.ext import commands
import random, asyncio

class StatusChanger(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.a = discord.Activity
        self.cancel = 0

    @commands.command()
    @commands.is_owner()
    async def begin(self, ctx):
        while self.cancel == 0:
            types = [discord.Game(name="with my uptime"),
                     discord.Activity(type=discord.ActivityType.listening, name=f"{len(self.bot.users)} cries of help"),
                     discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.bot.guilds)} talk")]
            await self.bot.change_presence(random.choice(types))
            print("changed presence")
            await asyncio.sleep(random.choice([15, 30, 60]))


    @commands.command(name='break')
    @commands.is_owner()
    async def _break(self, ctx):
        """break the presence change and reset it

        blocker resets after 2 mins - begin must be run again."""
        self.cancel += 1
        activity = discord.Game(name='with {} servers'.format(len(self.bot.guilds)))
        await self.bot.change_presence(activity)
        m = await ctx.send("Successfully broke the chain.")
        await asyncio.sleep(120)
        await m.edit("Successfully broke the chain.\n\nReset - ready for use again.")


def setup(bot):
    bot.add_cog(StatusChanger(bot))