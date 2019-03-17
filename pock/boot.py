import discord, time, datetime, os, traceback
from discord.ext import commands
start = time.time()
bot = commands.AutoShardedBot(command_prefix=commands.when_mentioned_or('//'), description=None, max_messages=9999,
                              case_insensitive=True, activity=discord.Game(name="Booting..."),
                              status=discord.Status.do_not_disturb)

token = 'PUT_YOUR_TOKEN_HERE'
toload = ["coggable.listeners",
                       "coggable.maincog",
                       "coggable.help",
                       "coggable.role"]
bot.cogss = toload
bot.boot_time = 0
bot.loadedcogs = 0
@bot.event
async def on_ready():
    success = 0
    for c in toload:
        try:
            bot.load_extension(c)
            bot.loadedcogs += 1
            success += 1
        except:
            pass
    done = time.time()
    bt = round(done - start)
    bot.boot_time += bt
    print("__________________________________________")
    print("Logged in as: {}".format(bot.user.name))
    print("Total guilds: {}".format(len(bot.guilds)))
    print("Total users : {}".format(len(bot.users)))
    print("Boot time   : {}s".format(bt))
    print("Total loaded: {}".format(success))
    print("__________________________________________")
    await bot.change_presence(activity=discord.Game(name='with {} servers'.format(len(bot.guilds))))

@bot.command()
async def test(ctx):
    """| test smthn"""
    await ctx.send("Hello {}! todays date is {}, and the UTC time is {}! i have received `{}` "
                   "messages since "
                   "boot.".format(ctx.author.mention, datetime.datetime.utcnow().strftime('%d/%m/%Y'),
                                  datetime.datetime.utcnow().strftime('%I:%M %p'), len(ctx.bot.messages)))


@bot.command()
@commands.is_owner()
async def reboot(ctx):
    """ | Reboot me"""
    try:
        await ctx.message.add_reaction("success:522078924432343040")
        await bot.close()
    except:
        pass
    finally:
        os.system("python3 boot.py")


@bot.command(aliases=['reload'])
@commands.is_owner()
async def r(ctx, cog: str):
    """| re/load a cog"""
    try:
        if cog == 'all':
            successful = ""
            for c in toload:
                try:
                    bot.unload_extension(c)
                    bot.load_extension(c)
                    successful += "Reloaded {} <:success:522078924432343040>\n".format(c)
                except:
                    print(f'{traceback.format_exc()}__________________________________________')
                    successful += "couldn't reload {} <:fail:522076877075251201>\n".format(c)
                    continue
            await ctx.send(successful)
        else:
            bot.unload_extension(cog)
            bot.load_extension(cog)
            await ctx.send("Reloaded {} <:success:522078924432343040>\n".format(cog), delete_after=10)
        await ctx.message.add_reaction("success:522078924432343040")
    except Exception as e:
        await ctx.message.add_reaction('fail:522076877075251201')
        print(f'{traceback.format_exc()}__________________________________________')
        await ctx.send(f'```py\n{e}\n```Full error in console')


@bot.command(aliases = ['ping', 'uptime'])
async def shard(ctx):
    """Get your shard, ping and uptime."""
    current_time = time.time()
    difference = int(round(current_time - start, 2))

    seconds = difference % 60
    minutes = round(difference / 60)
    hours = round(difference / 3600)
    days = 0

    while minutes > 59:
        minutes -= 60
        hours += 1
    while hours >= 23:
        days += 1
        hours -= 24
    utfmt = f"{days}d, {hours}h, {minutes}m, {seconds}s"
    m = await ctx.send("Getting info...")
    async with ctx.channel.typing():
        pang = f'{ctx.bot.latency * 1000:.0f}'
        shardid = ctx.guild.shard_id + 1
        e = discord.Embed(title="Total shards: {}".format(bot.shard_count),
                          description="**Your shard: {}**\n**Ping: {}ms**"
                                      "\n**Boot time: {}s**\nUptime: **{}**".format(shardid, pang, bot.boot_time, utfmt),
                          color=ctx.author.color, timestamp=datetime.datetime.utcnow())
    await ctx.send(embed=e)
    await m.delete()

bot.run(token)
