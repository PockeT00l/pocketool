import discord, datetime, traceback
from discord.ext import commands
from random import randint

class Ihaveears(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.dtf = "%I:%M %p @ %d/%m/%Y %Z"
        self.count = 0

    @commands.Cog.listener()
    async def on_guild_add(self, guild):
        to = self.bot.get_channel(543496620743065620)
        bots = 0
        members = 0
        e = discord.Embed(title="I joined a server!", description=datetime.datetime.utcnow().strftime(self.dtf),
                          timestamp=datetime.datetime.utcnow(), color=guild.owner.color)
        m = await to.send(embed=e)
        t = discord.Embed(title="I joined a server!", description=datetime.datetime.utcnow().strftime(self.dtf),
                          timestamp=datetime.datetime.utcnow(), color=guild.owner.color)
        for m in guild.members:
            if m.bot:
                bots += 1
            else:
                members += 1
        total = bots + members
        t.add_field(name="Member Count:", value="Bots: {}\nHumans: {}\nTotal: {}".format(bots, members, total))
        t.add_field(name="Owner:", value=guild.owner.name)
        await m.edit(embed=e)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(f"Error: missing permissions\n`{error}`")
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"Command is on a cooldown! try again in `{round(error.retry_after, 2)}`s.")
        else:
            with open("log.txt", 'a+') as log:
                log.write(f"[ERROR] | {ctx.author} ran {ctx.command.name} in {ctx.guild.id} at "
                        f"{datetime.datetime.utcnow().strftime('%d/%m/%Y %I:%M%p%z')}\n")
                log.write(traceback.format_exc())
                log.close()
            await ctx.send(ctx.author.mention + " an unexpected error has occurred and has been logged. please report"
                                                " the below error to my developer:")
            await ctx.send(f"```py\n{error}\n```")
            if ctx.command.is_on_cooldown:
                cmd = ctx.command
                cmd.reset_cooldown(ctx)
            else:
                pass
            await ctx.send("Your error num: {}".format(randint(len(ctx.author.name), 999)))
            print("__________________________________________")
            raise error

    @commands.Cog.listener()
    async def on_command(self, ctx):
        with open("log.txt", 'a+') as l:
            l.write(f"[INFO] | {ctx.author} ran {ctx.command.name} in {ctx.guild.id} at "
                    f"{datetime.datetime.utcnow().strftime('%d/%m/%Y %I:%M%p%z')}\n")
            l.close()
        self.count += 1

    @commands.Cog.listener()
    async def on_error(self, error):
        raise error


def totalcommands(self, bot):
    bot.totalcommands = self.count

def setup(bot):
    bot.add_cog(Ihaveears(bot))
