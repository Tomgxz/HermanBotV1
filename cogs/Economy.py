import discord, random, json, sys, re
from discord.ext import commands
from utils import config as cfg
from utils import defaultReplies as replies
from utils import chatFormatting as humanize
from utils.embedCreator import createEmbed, embedType


def defaultSettings():
    return {
        "cooldowns": {
            "work": 14400,
            "crime": 14400,
            "rob": 86400,
            "withdraw": 1,
            "deposit": 1,
        },
        "reply": True,
        "payouts": {
            "crime": {
                "max": 300,
                "min": 10
            },
            "work": {
                "max": 250,
                "min": 10
            },
            "slut": {
                "max": 350,
                "min": 100
            }
        },
        "failrates": {
            "crime": 50,
            "rob": 70,
            "slut": 40
        },
        "fines": {
            "max": 250,
            "min": 10,
        },
        "interest": 5,
        "roulette_toggle": True,
        "roulette_time": 60,
        "roulette_payouts": {
            "zero": 36,
            "single": 17,
            "color": 1,
            "dozen": 2,
            "odd_or_even": 1,
            "halfs": 1,
            "column": 2,
        },
        "betting": {
            "max": 10000,
            "min": 100,
        },
        "wallet_max": 50000,
        "shop": {
            "chicken": {
                "price": 250,
                "maxperperson": 1
            }
        }
    }


def defaultMemberSettings():
    return {
        "cooldowns": {
            "work": None,
            "send": None,
            "crime": None,
            "rob": None,
            "deposit": None,
            "withdraw": None,
        },
        "items": {
            "chicken": []
        },
        "wallet": 0,
        "bank": 0,
        "winnings": 0,
        "losses": 0,
    }


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coinname = "shmeckles"
        self.reportTo = self.bot.get_user(523209585700372490)

        self.defaults = defaultSettings()
        self.defaults_member = defaultMemberSettings()
        self.roulettegames = {}

    async def newWalletBalance(self, ctx):
        await ctx.send(embed=createEmbed(
            ctx=ctx,
            type=embedType.blue,
            message=
            f"Your new wallet balance is {humanize.humanizeNumber(await get_bank_balance(ctx, ctx.author,mode='wallet'))} {self.coinname}"
        ))

    async def newBankBalance(self, ctx):
        await ctx.send(embed=createEmbed(
            ctx=ctx,
            type=embedType.blue,
            message=
            f"Your new bank balance is {humanize.humanizeNumber(await get_bank_balance(ctx, ctx.author,mode='bank'))} {self.coinname}"
        ))

# BASIC COMMANDS

    @commands.command(aliases=["reg"])
    async def registerServer(self, ctx):
        async with ctx.typing():
            guild = ctx.guild
            guildid = guild.id
            c = cfg.getConfig()
            if not (f"{guildid}" in c):
                c[f"{guildid}"] = {"settings": self.defaults, "users": {}}
                cfg.setConfig(c)
                await ctx.send(embed=createEmbed(
                    ctx=ctx,
                    type=embedType.green,
                    message=f"This server has been registered :)"))
            else:
                await ctx.send(embed=createEmbed(
                    ctx=ctx,
                    type=embedType.red,
                    message=f"This server has already been registered :)"))
            return

    @commands.command(aliases=["balance"])
    async def bal(self, ctx, user: discord.Member = None):
        async with ctx.typing():
            if user is None:
                user = ctx.author
            await open_account(ctx, user)
            users = cfg.getUsersSettings(ctx)
            wallet_amt = users[str(user.id)]["wallet"]
            bank_amt = users[str(user.id)]["bank"]

            f = [["Wallet Balance",
                  humanize.humanizeNumber(wallet_amt)],
                 ["Bank Balance",
                  humanize.humanizeNumber(bank_amt)]]
            e = createEmbed(ctx=ctx,
                            type=embedType.blue,
                            message=" ",
                            fields=f,
                            inline=True)
        await ctx.send(embed=e)

    @commands.command(aliases=["lb"])
    async def leaderboard(self, ctx, x=1):
        async with ctx.typing():
            users = cfg.getUsersSettings(ctx)
            lb = {}
            total = []
            for user in users:
                name = int(user)
                totalamt = users[user]["wallet"] + users[user]["bank"]
                lb[totalamt] = name
                total.append(totalamt)
            total = sorted(total, reverse=True)
            index = 1
            f = []
            for amt in total:
                id_ = lb[amt]
                m = self.bot.get_user(id_)
                n = f"{m.name}#{m.discriminator}"
                amtoutput = humanize.humanizeNumber(amt)
                f.append([f"{index}. {n}", f"{amtoutput}"])
                if index == x:
                    break
                else:
                    index += 1
            e = createEmbed(ctx=ctx,
                            type=embedType.blue,
                            message=f"Top {x} Richest People",
                            fields=f,
                            inline=False)

        await ctx.send(embed=e)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(aliases=["wd"])
    async def withdraw(self, ctx, amount=None):
        async with ctx.typing():
            user = ctx.author
            if amount == None:
                await ctx.send(
                    embed=createEmbed(ctx=ctx,
                                      type=embedType.red,
                                      message=f"You did not specify an amount")
                )
                return
            bal = await get_bank_balance(ctx, user, mode="bank")

            if amount.lower() == "all":
                amount = bal

            amount = int(amount)

            if amount > bal:
                await ctx.send(embed=createEmbed(
                    ctx=ctx,
                    type=embedType.red,
                    message=f"You do not have sufficient money in your bank"))
                return
            if amount <= 0:
                await ctx.send(embed=createEmbed(
                    ctx=ctx,
                    type=embedType.red,
                    message=f"Amount must be positive and not zero"))
                return

            await update_bank_balance(ctx, user, amount)
            await update_bank_balance(ctx, user, -1 * amount, "bank")
        await ctx.send(embed=createEmbed(
            ctx=ctx,
            type=embedType.green,
            message=
            f"You withdrew {humanize.humanizeNumber(amount)} {self.coinname}"))

        await self.newWalletBalance(ctx)
        await self.newBankBalance(ctx)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(aliases=["dp"])
    async def deposit(self, ctx, amount=None):
        async with ctx.typing():
            user = ctx.author
            if amount == None:
                await ctx.send(
                    embed=createEmbed(ctx=ctx,
                                      type=embedType.red,
                                      message=f"You did not specify an amount")
                )
                return

            bal = await get_bank_balance(ctx, user, mode="wallet")

            if amount.lower() == "all":
                amount = bal

            amount = int(amount)

            if amount > bal:
                await ctx.send(embed=createEmbed(
                    ctx=ctx,
                    type=embedType.red,
                    message=f"You do not have sufficient money in your wallet")
                               )
                return
            if amount <= 0:
                await ctx.send(embed=createEmbed(
                    ctx=ctx,
                    type=embedType.red,
                    message=f"Amount must be positive and not zero"))
                return

            await update_bank_balance(ctx, user, -1 * amount)
            await update_bank_balance(ctx, user, amount, "bank")
        await ctx.send(embed=createEmbed(
            ctx=ctx,
            type=embedType.green,
            message=
            f"You deposited {humanize.humanizeNumber(amount)} {self.coinname}")
                       )

        await self.newWalletBalance(ctx)
        await self.newBankBalance(ctx)

# EARNING MONEY

    @commands.cooldown(1, 600, commands.BucketType.user)
    @commands.command(aliases=["w"])
    async def work(self, ctx):
        async with ctx.typing():
            user = ctx.author
            await open_account(ctx, user)

            pb = self.getPayout(ctx, "work")
            earning = random.randint(pb["min"], pb["max"])

            work = random.choice(replies.getWorkReplies()).replace(
                "{amount}",
                f"{humanize.humanizeNumber(earning)} {self.coinname}")

            await update_bank_balance(ctx, user, earning)

        await ctx.send(
            embed=createEmbed(ctx=ctx, type=embedType.green, message=work))
        await self.newWalletBalance(ctx)

    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command(aliases=["gift"])
    async def send(self, ctx, member: discord.Member, amount=None):
        async with ctx.typing():
            user = ctx.author

            await open_account(ctx, user)
            await open_account(ctx, member)

            if amount == None:
                await ctx.send(
                    embed=createEmbed(ctx=ctx,
                                      type=embedType.red,
                                      message=f"You did not specify an amount")
                )
                return

            bal = await get_bank_balance(ctx, user, mode="bank")
            if amount == "all":
                amount = await self.get_wallet_balance(user, mode="wallet")

            amount = int(amount)

            if amount > bal:
                await ctx.send(embed=createEmbed(
                    ctx=ctx,
                    type=embedType.red,
                    message=f"You do not have sufficient money in your bank"))
                return
            if amount <= 0:
                await ctx.send(embed=createEmbed(
                    ctx=ctx,
                    type=embedType.red,
                    message=f"Amount must be positive and not zero"))
                return

            await update_bank_balance(ctx, user, -1 * amount, "bank")
            await update_bank_balance(ctx, member, amount, "bank")
        await ctx.send(embed=createEmbed(
            ctx=ctx,
            type=embedType.green,
            message=
            f"You gave {member.name}#{member.discriminator} {humanize.humanizeNumber(amount)} {self.coinname}"
        ))

        await self.newBankBalance(ctx)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command()
    async def beg(self, ctx):
        async with ctx.typing():
            user = ctx.author
            await open_account(ctx, user)

            p_earnings = []
            for i in range(100):
                p_earnings.append(i)
            weights = []
            j = 10
            for i in range(20):
                for l in range(5):
                    weights.append(j)
                j -= 1

            earning = random.choices(p_earnings, weights=tuple(weights),
                                     k=1)[0]

            await update_bank_balance(ctx, user, earning)

        await ctx.send(embed=createEmbed(
            ctx=ctx,
            type=embedType.green,
            message=
            f"You gained {humanize.humanizeNumber(earning)} {self.coinname} from begging"
        ))

    #@commands.cooldown(1, 1800, commands.BucketType.user)
    @commands.command(aliases=["rb"])
    async def rob(self, ctx, member: discord.Member):
        async with ctx.typing():
            user = ctx.author
            await open_account(ctx, user)

            await open_account(ctx, member)
            bal = await get_bank_balance(ctx, member, mode="wallet")
            if bal <= 0:
                await ctx.send(embed=createEmbed(
                    ctx=ctx,
                    type=embedType.red,
                    message=f"{member.name} does not have any money on them"))
                return

            earning = random.randint(bal // 2, bal)

            caught = random.randint(1, 100)
            failrate = await self.getFailRate(ctx, "rob")
            if caught > failrate:
                caught = True
            else:
                caught = False

            if caught == True:
                finebounds = cfg.getGuildSettings(ctx)["fines"]
                fine = random.randint(finebounds["min"], finebounds["max"])
                await update_bank_balance(ctx, user, -1 * fine)
                await ctx.send(embed=createEmbed(
                    ctx=ctx,
                    type=embedType.red,
                    message=
                    f"You were caught by the police while robbing {member.name} and were fined {humanize.humanizeNumber(fine)} {self.coinname}"
                ))
                await self.newWalletBalance(ctx)
                return

            await update_bank_balance(ctx, user, earning)
            await update_bank_balance(ctx, member, -1 * earning)
        await ctx.send(embed=createEmbed(
            ctx=ctx,
            type=embedType.green,
            message=
            f"You robbed {humanize.humanizeNumber(earning)} {self.coinname} from {member.name} and got away with it."
        ))
        await self.newWalletBalance(ctx)

    @commands.cooldown(1, 2700, commands.BucketType.user)
    @commands.command()
    async def crime(self, ctx):
        async with ctx.typing():
            user = ctx.author
            await open_account(ctx, user)

            caught = random.randint(1, 100)
            failrate = await self.getFailRate(ctx, "crime")
            if caught > failrate:
                caught = True
            else:
                caught = False

            if caught == True:
                finebounds = cfg.getGuildSettings(ctx)["fines"]
                fine = random.randint(finebounds["min"], finebounds["max"])
                await update_bank_balance(ctx, user, -1 * fine)
                await ctx.send(embed=createEmbed(
                    ctx=ctx,
                    type=embedType.red,
                    message=
                    f"You were caught by the police while committing a crime and were fined {humanize.humanizeNumber(fine)} {self.coinname}"
                ))
                await self.newWalletBalance(ctx)
                return

            pb = self.getPayout(ctx, "crime")
            earning = random.randint(pb["min"], pb["max"])

            crime = random.choice(replies.getCrimeReplies()).replace(
                "{amount}",
                f"{humanize.humanizeNumber(earning)} {self.coinname}")

            await update_bank_balance(ctx, user, earning)

        await ctx.send(
            embed=createEmbed(ctx=ctx, type=embedType.green, message=crime))
        await self.newWalletBalance(ctx)

    @commands.cooldown(1, 300)
    @commands.command()
    async def slut(self, ctx):
        async with ctx.typing():
            user = ctx.author
            await open_account(ctx, user)

            caught = random.randint(1, 100)
            failrate = await self.getFailRate(ctx, "slut")
            if caught > failrate:
                caught = True
            else:
                caught = False

            if caught == True:
                finebounds = cfg.getGuildSettings(ctx)["fines"]
                fine = random.randint(finebounds["min"], finebounds["max"])
                await update_bank_balance(ctx, user, -1 * fine)
                slutFail = random.choice(replies.getSlutFailReplies()).replace(
                    "{amount}",
                    f"{humanize.humanizeNumber(fine)} {self.coinname}")
                await ctx.send(embed=createEmbed(
                    ctx=ctx, type=embedType.red, message=slutFail))
                await self.newWalletBalance(ctx)
                return

            pb = self.getPayout(ctx, "slut")
            earning = random.randint(pb["min"], pb["max"])

            slutSucceed = random.choice(
                replies.getSlutSucceedReplies()).replace(
                    "{amount}",
                    f"{humanize.humanizeNumber(earning)} {self.coinname}")

            await update_bank_balance(ctx, user, earning)

        await ctx.send(embed=createEmbed(
            ctx=ctx, type=embedType.green, message=slutSucceed))
        await self.newWalletBalance(ctx)

# ERROR CATCHERS

#@bal.error

    @beg.error
    @leaderboard.error
    @withdraw.error
    @deposit.error
    @work.error
    @crime.error
    @slut.error
    async def errorMessage(self, ctx, error, job=None):
        exty, exob, extr = sys.exc_info()

        if isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
            await self.cooldown_error(ctx, error, exob, job=job)
            return

        await ctx.send(
            f"errorcatch ```Location:{extr.tb_frame.f_code.co_filename} at line {extr.tb_lineno}\n\n{error}```\nPlease report me to {self.bot.get_user(523209585700372490).mention}"
        )

    @send.error
    async def send_error(self, ctx, error):
        if isinstance(error,
                      discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send(embed=createEmbed(
                ctx=ctx,
                type=embedType.red,
                message=f"You did not specify a user to send money to"))
            return
        await self.errorMessage(ctx, error, job="send")
        print(error)

    #@rob.error
    async def rob_error(self, ctx, error):
        if isinstance(error,
                      discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send(
                embed=createEmbed(ctx=ctx,
                                  type=embedType.red,
                                  message=f"You did not specify a user to rob")
            )
            return
        await self.errorMessage(ctx, error, job="rob")

    async def cooldown_error(self, ctx, error, output, job=None):
        output = str(output)
        cooldown = float(re.findall(r"[-+]?\d*\.?\d+|\d+", output)[0])
        cooldownHumanized = humanize.humanizeSeconds(int(cooldown))
        response = {
            "work":
            f"You cannot work for another {cooldownHumanized}.",
            "crime":
            f"You cannot commit a crime for another {cooldownHumanized}.",
            "slut":
            f"You cannot be a slut for another {cooldownHumanized}.",
            "rob":
            f"You cannot rob anyone for another {cooldownHumanized}.",
            "withdraw":
            f"You cannot withdraw any more {self.coinname} for another {cooldownHumanized}.",
            "deposit":
            f"You cannot deposit any more {self.coinname} for another {cooldownHumanized}.",
            "send":
            f"You cannot give anyone any more {self.coinname} for another {cooldownHumanized}.",
        }
        if job not in response.keys():
            await ctx.send(embed=createEmbed(
                ctx=ctx,
                type=embedType.red,
                message=
                f"You cannot use that command for another {cooldownHumanized}")
                           )
            return
        await ctx.send(embed=createEmbed(
            ctx=ctx, type=embedType.red, message=response[job]))

    async def getFailRate(self, ctx, job):
        return cfg.getGuildSettings(ctx)["failrates"][job]

    def getPayout(self, ctx, job):
        return cfg.getGuildSettings(ctx)["payouts"][job]


# UTILS


async def open_account(ctx, user):
    users = cfg.getUsersSettings(ctx)
    if str(user.id) in users:
        return False
    users[str(user.id)] = defaultMemberSettings()
    cfg.setUsersSettings(ctx, users)

    with open("utils/mainbank.json", "w") as f:
        json.dump(users, f)
    return True


async def update_bank_balance(ctx, user, change=0, mode="wallet"):
    users = cfg.getUsersSettings(ctx)
    users[str(user.id)][mode] += change
    cfg.setUsersSettings(ctx, users)


async def get_bank_balance(ctx, user, mode="wallet"):
    users = cfg.getUsersSettings(ctx)
    return users[str(user.id)][mode]


def getEconomyClass(bot):
    return Economy(bot)


def setup(bot):
    bot.add_cog(Economy(bot))
