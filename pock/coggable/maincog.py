import time
import datetime
import psutil
import os
from .listeners import totalcommands

from discord.ext import commands
import traceback
import discord
import textwrap
from contextlib import redirect_stdout
import io


class Smthn(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # stats
        self.commands = totalcommands
        # else
        self.process = psutil.Process()
        self.toload = bot.cogss
        self._last_result = None
        self.dtf = "%I:%M %p @ %d/%m/%Y %Z"
    blankeval = '```\nprint("dude you need to tell me something to eval lul")\n```'

    @staticmethod
    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```py' or '```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content.strip('` \n')

    @commands.command(aliases=['ui', 'u', 'user'])
    @commands.bot_has_permissions(embed_links=True)
    async def userinfo(self, ctx, user: discord.Member = None):
        """| Get @user/userID's info. kinda works cross-server."""
        dtformat = "%I:%M %p @ %d/%m/%Y %Z"
        if user is None:
            user = ctx.author
        u = user
        tmg = await ctx.send("Gathering info...", delete_after=5)
        msgs = "Idfk do `cmd + f` and `from: {}`".format(user)
        if u in ctx.guild.members:
            e = discord.Embed(title="{}'s info".format(u.name),
                              timestamp=datetime.datetime.utcnow(), color=ctx.author.color)
            e.add_field(name="Top Role:", value=u.top_role.name)
            e.add_field(name="Total Roles:", value=len(u.roles), inline=True)
            e.add_field(name="Created at:", value=u.created_at.strftime(dtformat), inline=False)
            e.add_field(name="Joined at:", value=u.joined_at.strftime(dtformat), inline=True)
            e.add_field(name="Total messages:", value=msgs)
            e.set_thumbnail(url=u.avatar_url)

            await ctx.send(embed=e)
        else:
            u = await self.bot.get_user_info(user.id)
            e = discord.Embed(title="{}'s info".format(u.name),
                              timestamp=datetime.datetime.utcnow(), color=ctx.author.color)
            e.add_field(name="Created at:", value=u.created_at.strftime(dtformat), inline=False)
            await ctx.send(embed=e)

    @commands.command()
    async def invite(self,ctx, dm: str = None):
        """Invite me"""
        if dm is None:
            mode = ctx
        elif dm == 'dm':
            mode = ctx.author
        elif dm == 'here':
            mode = ctx
        else:
            mode = ctx
        discgg = 'https://discord.gg/bwmVbdc'
        invlink = 'https://discordapp.com/oauth2/authorize?client_id=553622350952923146&permissions=0&scope=bot'
        e = discord.Embed(title=None, description="[Add the bot]({}) or, [join the server!]({})".format(invlink, discgg))
        try:
            await mode.send(embed=e)
        except discord.Forbidden:
            await mode.send(embed=e)

    @commands.command(name='perms', aliases=['perms_for', 'permissions'])
    @commands.guild_only()
    async def check_permissions(self, ctx, *, member: discord.Member=None):
        """A simple command which checks a members Guild Permissions.
        If member is not provided, the author will be checked."""

        if not member:
            member = ctx.author

        # Here we check if the value of each permission is True.
        perms = '\n'.join(perm for perm, value in member.guild_permissions if value)

        # And to make it look nice, we wrap it in an Embed.
        embed = discord.Embed(title='Permissions for:', description=ctx.guild.name, colour=member.colour)
        embed.set_author(icon_url=member.avatar_url, name=str(member))

        # \uFEFF is a Zero-Width Space, which basically allows us to have an empty field name.
        embed.add_field(name=None, value=perms)
        await ctx.send(content=None, embed=embed)

    @commands.group()
    @commands.is_owner()
    async def console(self, ctx):
        pass
    @console.command()
    @commands.is_owner()
    async def clear(self, ctx):
        """Clears console"""
        nl = '\n'
        print(nl*999)
        print(f"Console cleared by {ctx.author}.\n__________________________________________")
    @console.command(name='log')
    @commands.is_owner()
    async def ulog(self, ctx):
        """Upload the log file."""
        await ctx.trigger_typing()
        await ctx.send(file=discord.File('log.txt'))
    @console.command()
    @commands.is_owner()
    async def status(self, ctx):
        """Reset the status"""
        await self.bot.change_presence(activity=discord.Game(name='with {} servers'.format(len(self.bot.guilds))))
        await ctx.send("Success.")
    @console.command()
    @commands.is_owner()
    async def debug(self, ctx):
        """get usage stats"""
        embed=discord.Embed(title="sys stats", color=discord.Color.blurple())
        memory_usage = self.process.memory_full_info().uss / 1024**2
        corenum = 0
        forefmt = ""
        cpu_usage = psutil.cpu_percent(interval=None, percpu=True)
        for corepercent in cpu_usage:
            corenum += 1
            forefmt += f"Core {corenum}: {corepercent}%\n"
        embed.add_field(name='Process', value=f'{memory_usage:.2f} MiB\nCPU: {forefmt}')
        embed.add_field(name="Total mem", value=psutil.virtual_memory().percent)
        await ctx.send(embed=embed)
    @console.group()
    @commands.is_owner()
    async def cmd(self, ctx):
        """IDFK"""
    @cmd.command()
    @commands.is_owner()
    async def remcd(self, ctx, commandname: str):
        """Remove the cooldown on a command."""
        cmd = self.bot.get_command(commandname)
        if not cmd:
            return ctx.send("i can't insta-cool a command that doesn't exist!")
        else:
            try:
                cmd.reset_cooldown(ctx)
                return ctx.send("Reset {}'s cooldown.".format(commandname))
            except Exception as e:
                return ctx.send(e)
    @console.command()
    @commands.is_owner()
    async def eval(self, ctx, body: str = f'{blankeval}'):
        """Eval code"""
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }
        env.update(globals())
        body = self.cleanup_code(self, content=body)
        stdout = io.StringIO()
        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'
        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass
            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @console.command()
    @commands.is_owner()
    async def servers(self, ctx):
        """List servers"""
        servers = "```\n"
        for c, s in enumerate(self.bot.guilds):
            c = c + 1
            servers += f"{c} {s.name} | {s.id}\n"
        servers += f"Total: {len(self.bot.guilds)}\n"
        servers += "```"
        print(servers)
        await ctx.send(servers)

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def purge(self, ctx, amount: int = 100):
        """Get them messages outta here!"""
        try:
            await ctx.message.delete()
            d = await ctx.channel.purge(limit=amount, bulk=True)
            await ctx.send("{}, i successfully purged {} messages.".format(ctx.author.mention, len(d)))
        except:
            try:
                d = await ctx.channel.purge(limit=amount, bulk=False)
                await ctx.send("{}, i successfully purged {} messages.".format(ctx.author.mention, len(d)))
            except:
                return ctx.send("Error: i need `manage_messages`. not sure how you ran the cmd without giving me it, "
                                "but ok.")

    @commands.command()
    @commands.bot_has_permissions(read_message_history=True)
    @commands.bot_has_permissions(attach_files=True)
    @commands.has_permissions(manage_messages=True)
    async def chatlog(self, ctx, limit: int = 1000):
        """Get [limit] amount of messages and output in a nice text file.

        the limit is capped at 999k, but the larger said limit is, the longer it will take to make and upload."""
        tm = await ctx.send("logging...")
        if limit >= 999999:
            limit = 999999
        async with ctx.channel.typing():
            amount = 0
            start = time.time()
            with open(f"{ctx.guild.name}-{ctx.channel.name}.txt", "a+") as l:
                async for m in ctx.channel.history(limit=limit, before=ctx.message.created_at, reverse=True):
                    amount += 1
                    l.write(f"{m.author} at {m.created_at.strftime('%d/%m/%Y %I:%M%p %z')}:\n{m.content}\n")
            l.close()
            end = time.time()
        await tm.edit(content="Logged {} messages in {} seconds\nFile:".format(
            amount, round(end - start, 2)))
        await ctx.send(file=discord.File(f"{ctx.guild.name}-{ctx.channel.name}.txt"))
        os.remove(f"{ctx.guild.name}-{ctx.channel.name}.txt")

    @commands.command(aliases=['announce', 'sendembed'])
    @commands.has_permissions(embed_links=True)
    @commands.bot_has_permissions(embed_links=True)
    async def embed(self, ctx):
        """Embed a message!
        DO NOT PASS ANY ARGS WHEN EXECUTING"""
        a = ctx.author.mention
        m = await ctx.send(f"{a}, this command is WIP. sorry")

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def stats(self, ctx, brief: bool = True):
        """Get bot stats.

        say `//stats False` to get lengthy, more in-depth info"""
        o = await self.bot.get_user_info(421698654189912064)
        url = 'http://discord.gg/mNV6azN'
        if brief:
            e = discord.Embed(title="My info!", color=self.bot.user.color, timestamp=datetime.datetime.utcnow())
            e.url = url
            e.add_field(name="Users:", value=len(self.bot.users))
            cc = 0
            for s in self.bot.guilds:
                cc += len(s.channels)
            e.add_field(name="Channels:", value=cc)
            e.add_field(name="Guilds:", value=len(self.bot.guilds))
            e.add_field(name="Total executed commands:", value="Null")
            e.add_field(name="Owner:", value=o)
            await ctx.send(embed=e)
        else:
            loaded = 0
            cogs = 4
            loadedcogs = 0
            musage = psutil.virtual_memory().percent
            corenum = 0
            forefmt = ""
            cpu_usage = psutil.cpu_percent(interval=None, percpu=True)
            for corepercent in cpu_usage:
                corenum += 1
                forefmt += f"Core {corenum}: {corepercent}%\n"
            e = discord.Embed(title="My info!", color=self.bot.user.color, timestamp=datetime.datetime.utcnow())
            e.url = url
            e.add_field(name="Users:", value=len(self.bot.users))
            cc = 0
            files = 0
            for s in self.bot.guilds:
                cc += len(s.channels)
            for d in os.listdir():
                files += 1
            e.add_field(name="Channels:", value=cc)
            e.add_field(name="Guilds:", value=len(self.bot.guilds))
            e.add_field(name="Total executed commands:", value="Null")
            e.add_field(name="Owner:", value=o)
            e.add_field(name="Memory usage:", value=f"{musage}%")
            e.add_field(name="CPU usage:", value=forefmt)
            e.add_field(name="Total files:", value=files)
            for c in self.toload:
                try:
                    self.bot.load_extention(c)
                    loadedcogs += 1
                except:
                    loadedcogs += 1
            e.add_field(name="Cogs:", value=f"{loadedcogs}/{cogs}")
            await ctx.send(embed=e)

    @commands.command()
    @commands.bot_has_permissions(create_instant_invite=True)
    async def geninv(self, ctx, channel: discord.TextChannel = None):
        """Generate an invite. mention a channel to remote create """
        if not channel:
            channel = ctx.channel
        if ctx.author.id == 421698654189912064:
            t = await channel.create_invite(reason="Invoked by owner.")
            await ctx.send(t.url)
        else:
            t = channel.create_invite(max_age=604800, reason="Invoked by {}".format(ctx.author.name))
            await ctx.send(t.url)

    @commands.command()
    @commands.bot_has_permissions(embed_links = True)
    async def serverinfo(self, ctx, id: int = None):
        """Get server infos. supply an id for another server

        note for id the bot must be *in* the server."""
        async with ctx.typing():
            invites = ""
            bots = 0
            humans = 0
            if id is None:
                server = ctx.guild
            else:
                server = self.bot.get_server(id)
            try:
                invs = await server.invites()
                for s in invs:
                    if s.max_age and s.max_uses == 0:
                        invites += s.url
                        break
            except Exception as e:
                invites += "https://www.daimto.com/wp-content/uploads/2014/08/errorstop.png"
                print(e)
            e = discord.Embed(title=f"{server.name}'s info!", timestamp=datetime.datetime.utcnow(), color=server.owner.color,
                              description=f"Owner: {server.owner} ({server.owner.mention})")
            e.url=invites
            for u in server.members:
                if u.bot:
                    bots += 1
                else:
                    humans += 1
            total = bots + humans
            e.add_field(name="Members:", value=f"`{bots}` bots\n{humans} humans\n{total} total")
            e.add_field(name="Roles:", value=str(len(server.roles)))
            # the str(len()) is so pep8 doesnt yell at me
            e.add_field(name="Channels:", value=str(len(server.channels)))
            e.add_field(name="Emoji(s):", value=str(len(server.emojis)))
            e.add_field(name="Created at:", value=server.created_at.strftime(self.dtf))
            e.set_thumbnail(url=server.icon_url)
        await ctx.send(embed=e)
def setup(bot):
    bot.add_cog(Smthn(bot))
