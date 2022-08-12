from discord.ext import commands
from utils import config as cfg
from utils.embedCreator import createEmbed, embedType
from cogs.Economy import open_account, update_bank_balance, get_bank_balance, getEconomyClass
from utils import Items


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coinname = getEconomyClass(self.bot).coinname
        self.reportTo = self.bot.get_user(523209585700372490)

    def getShopCFG(self, ctx):
        return cfg.getGuildSettings(ctx)["shop"]

    @commands.command()
    async def buy(self, ctx, item=None):
        async with ctx.typing():
            await ctx.send(embed=createEmbed(
                ctx=ctx,
                type=embedType.red,
                message=f"This command is temporarily disabled"))
            return

            user = ctx.author
            await returnccount(ctx, user)
            bal = await get_bank_balance(ctx, user, mode="wallet")

            if item == None:
                await ctx.send("got here")
                await ctx.send(
                    embed=createEmbed(ctx=ctx,
                                      type=embedType.red,
                                      message=f"You did not specify an item"))
                return

            if item not in list(self.getShopCFG(ctx)):
                await ctx.send(embed=createEmbed(
                    ctx=ctx,
                    type=embedType.red,
                    message=f"That item is not being sold in the shop right now"
                ))
                return

            if self.getShopCFG(ctx)[item]["price"] > bal:
                await ctx.send(embed=createEmbed(
                    ctx=ctx,
                    type=embedType.red,
                    message=f"You do not have sufficient money in your wallet")
                               )
                return

            useritems = cfg.getUsersSettings(ctx)[str(user.id)]["items"]

            if len(useritems[item]) >= self.getShopCFG(
                    ctx)[item]["maxperperson"]:
                responses = {
                    "chicken": "You already own a chicken - send it to fight!"
                }

                if item in list(responses):
                    m = responses[item]
                else:
                    m = f"You own the maximum amount of these items you can ({len(useritems[item])})"

                await ctx.send(
                    embed=createEmbed(ctx=ctx, type=embedType.red, message=m))
                return

            price = self.getShopCFG(ctx)[item]["price"]

            if item == "chicken":
                ch = Items.newChicken()
                useritems[item].append(ch)
            else:
                return

            newSettings = cfg.getUsersSettings(ctx)
            newSettings[str(user.id)]["items"] = useritems
            await ctx.send(newSettings)
            cfg.setUsersSettings(ctx, newSettings)

            await update_bank_balance(ctx, user, change=-1 * price)

            if item == "chicken":
                await ctx.send(embed=createEmbed(
                    ctx=ctx,
                    type=embedType.red,
                    message="You have bought a chicken to fight!"))
            else:
                await ctx.send(
                    embed=createEmbed(ctx=ctx,
                                      type=embedType.red,
                                      message="Purchase Successful!"))
        await self.newWalletBalance(ctx)

    async def newWalletBalance(self, ctx):
        await ctx.send(embed=createEmbed(
            ctx=ctx,
            type=embedType.blue,
            message=
            f"Your new wallet balance is {humanize.humanizeNumber(await get_bank_balance(ctx, ctx.author,mode='wallet'))} {self.coinname}"
        ))


def setup(bot):
    bot.add_cog(Shop(bot))
