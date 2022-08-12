import os, discord, random, humanize, datetime
from itertools import cycle
from discord.ext import commands, tasks
from cogs import Music, ReactionRoles, Economy, Games, Shop
from utils import keep_alive
from utils.emojiData import getEmoji
from discord_slash import SlashCommand, SlashContext

class Context(commands.Context):
    async def tick(self, v):
        emoji = '\N{WHITE HEAVY CHECK MARK}' if v else '\N{CROSS MARK}'
        #try:
        await self.message.add_reaction(emoji)
        #except discord.HTTPException:
        #    pass

# role_id = self.emoji_to_role[payload.emoji]
# TypeError: 'method' object is not subscriptable

'''class Bot(commands.Bot):    
    def role_message_id(self):
        return 845950963596787752
    
    def emoji_to_role(self):
        return {
            discord.PartialEmoji(name='🔴'): 838541162188111922,
        }

    async def get_context(self,message, *, cls=Context):
        return await super().get_context(message,cls=cls)
    
    async def on_member_join(self,member):
        guild = member.guild
        if guild.system_channel is not None:
            to_send = 'Welcome {0.mention} to {1.name}!'.format(member, guild)
            await self.get_channel(838288816867508224).send(to_send)'''


#bot = Bot(command_prefix=".", description="Hello There")
bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@slash.slash()
async def roll(ctx:SlashContext, dice:str):
    try: rolls, limit= map(int, dice.split("d"))
    except Exception:
        await ctx.send("Format has to be NdN!")
        return
    result=", ".join(str(random.randint(1,limit)) for r in range(rolls))
    await ctx.tick(True)
    await ctx.send(result)

@bot.command(description="For when you want to settle the score some other way")
async def choose(ctx,*choices:str):
    await ctx.send(random.choice(choices))

status = cycle(
    ['Hello There'])

@tasks.loop(seconds=5)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))

@bot.command()
async def humanizeSeconds(ctx, n):
    await ctx.send(humanize.precisedelta(datetime.timedelta(seconds=float(n)),minimum_unit="seconds"))

@bot.command()
async def help_economy(ctx):
    embed=discord.Embed(title="**Herman the Worman - All Economy Commands** as of 25/5/2021", description="<inp> means that the input is required, [inp] means that the input is optional,  opt1 | opt2 means that you can do option 1 or option 2", color=discord.Color.red())
    embed.add_field(name=".balance [@user] | .bal [@user]", value="Shows the bank and wallet values of a user. If left blank, it will show your own.", inline=False)
    embed.add_field(name=".leaderboard [10] | .lb [10]", value="Shows the top X most wealthy people on the server. If no number is given, It will show the wealthiest person on the server", inline=False)
    embed.add_field(name=".withdraw <1 | all> | .wd <1 | all>", value="Withdraws X amount of money from your bank account. If you input 'all', it will withdraw everything. *THIS COMMAND HAS A TWO MINUTE COOLDOWN.*", inline=False)
    embed.add_field(name=".deposit <1 | all> | .dp <1 | all>", value="Deposits X amount of money from your wallet into your bank account. If you input 'all', it will deposit everything. *THIS COMMAND HAS A TWO MINUTE COOLDOWN.*", inline=False)
    embed.add_field(name=".send <@user> <1> | .gift <@user> <1>", value="Sends X amount of money from your bank account into the specified user's bank account. *THIS COMMAND HAS A FIVE MINUTE COOLDOWN.*", inline=False)
    embed.add_field(name=".beg", value="This will get you a small amount of money every time you beg. *THIS COMMAND HAS A TEN SECOND COOLDOWN.*", inline=False)
    embed.add_field(name=".rob <@user>", value="This will steal half to all of the money in the specified user's wallet. There is a 30% chance you will get caught, and fined, if you do this. *THIS COMMAND HAS A THIRTY MINUTE COOLDOWN.*", inline=False)
    embed.add_field(name=".crime", value="This will make you commit a crime, and recieve credits for it. There is a 50% chance you will get caught, and fined, if you do this. *THIS COMMAND HAS A FORTY-FIVE MINUTE COOLDOWN.*", inline=False)
    embed.add_field(name=".slots <1>", value="Bet X amount of money on a slots game. Rewards are such: Two identical = double your bet. Three Identical = Triple your bet. Triple Star = Four times your bet. Two Skulls = Lose double your bet. Triple Skulls = Lose four times your bet. No identical items = lose your betting money. *THIS COMMAND HAS A THIRTY SECOND COOLDOWN.*", inline=False)
    embed.set_footer(text="If a command has a cooldown, it will be activated even if the inputs are invalid, so make sure you know what you are doing.")
    await ctx.send(embed=embed)

@bot.command()
async def announcement(ctx):
    pass

@bot.command()
async def emoji(ctx,emoji=None):
    if emoji==None:
        await ctx.send("No emoji name given")
    em = getEmoji(emoji)
    if em==None:
        await ctx.send("Unrecognised emoji")
    await ctx.send(em)

@bot.command()
async def kms(ctx):
    await ctx.send("Father benjamin is bad")


@slash.slash(name="test")
async def _test(ctx: SlashContext):
    embed = discord.Embed(title="embed test")
    await ctx.send(content="test", embeds=[embed])



keep_alive.keep_alive() 
token = os.environ.get("TOKEN") 
Economy.setup(bot)
Games.setup(bot)
Music.setup(bot)
ReactionRoles.setup(bot)
Shop.setup(bot)
bot.run(token)

# discord.com/api/oauth2/authorize?client_id=845598635252383816&permissions=8&scope=bot%20applications.commands