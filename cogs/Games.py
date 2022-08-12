import discord, random, sys, re
from discord.ext import commands
from utils import chatFormatting as humanize
from utils.embedCreator import createEmbed, embedType, getColor
from cogs.GameFiles.BlackJack import startGame as startBlackJack
from cogs.GameFiles.CockFight import startGame as startCockFight
from cogs.Economy import open_account,update_bank_balance,get_bank_balance,getEconomyClass


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.coinname=getEconomyClass(self.bot).coinname
        self.reportTo = self.bot.get_user(523209585700372490)

# GAMES


    @commands.command(aliases=["cf"])
    async def cockfight(self,ctx,bet = None):
        async with ctx.typing():
            user=ctx.author
            await open_account(ctx,user)
            if bet == None:  
                await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.red,message=f"You did not specify an amount"))
                return 
            bal = await get_bank_balance(ctx, user,mode="wallet")

            bet=int(bet)

            if bet > bal:
                await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.red,message=f"You do not have sufficient money in your wallet"))
                return
            if bet < 100:
                await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.red,message=f"Minimum betting amount is 100 {self.coinname}"))
                return
            
            error,embed = await startCockFight(ctx,user,bet)

        await ctx.send(embed=embed)
        if not(error):
            await self.newWalletBalance(ctx)



    @commands.command(aliases=["bj"])
    async def blackjack(self,ctx,amount = None):
        async with ctx.typing():
            user=ctx.author
            await open_account(ctx,user)
            if amount == None:  
                await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.red,message=f"You did not specify an amount"))
                return 
            bal = await get_bank_balance(ctx,user,mode="wallet")

            amount=int(amount)

            if amount > bal:
                await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.red,message=f"You do not have sufficient money in your wallet"))
                return
            if amount < 100:
                await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.red,message=f"Minimum betting amount is 100 {self.coinname}"))
                return
            
            embed,result = await startBlackJack(ctx)
            
            await ctx.send(embed=embed)

            if result == "loss":
                await update_bank_balance(ctx,user,-1*amount)
                await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.red,message=f"You lost the game of blackjack and lost {humanize.humanizeNumber(amount)} {self.coinname}"))
                await self.newWalletBalance(ctx)
                return
            if result == "draw":
                await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.gray,message=f"You drew the game of blackjack and didn't get any {self.coinname}"))
                return

            await update_bank_balance(ctx,user,amount)
        await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.green,message=f"You won the game of blackjack and recieved {humanize.humanizeNumber(amount)} {self.coinname} in return"))
        await self.newWalletBalance(ctx)

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command()
    async def slots(self,ctx,amount = None):
        async with ctx.typing():
            user=ctx.author
            await open_account(ctx,user)
            if amount == None:
                await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.red,message=f"You did not specify an amount"))
                return

            bal = await get_bank_balance(ctx, user,mode="wallet")

            amount = int(amount)

            if amount > bal:
                await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.red,message=f"You do not have sufficient money in your wallet"))
                return
            if amount <= 0:
                await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.red,message=f"Amount must be positive and not zero"))
                return

            final = []
            for i in range(3):
                a = random.choice([':star:',':star:',':apple:',':apple:',':banana:',':banana:',':tangerine:',':tangerine:',':skull:'])
                final.append(a)

            f=[]
            f.append([final[0],"Slot1"])
            f.append([final[1],"Slot2"])
            f.append([final[2],"Slot3"])
            
            if final[0] == final[1] or final[1] == final[2] or final[0] == final[2]:
                if final.count(":skull:") > 1:
                    if final[0] == final[1] == final[2]:
                        await update_bank_balance(ctx, user,amount*-4)
                        await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.red,message=f"You rolled three skulls and lost {humanize.humanizeNumber(amount*4)} {self.coinname}",fields=f,inline=True))
                    else:
                        await update_bank_balance(ctx, user,amount*-2)
                        await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.red,message=f"You rolled two skulls and lost {humanize.humanizeNumber(amount*2)} {self.coinname}",fields=f,inline=True))
                elif ":star:" in final:
                    if final[0] == final[1] == final[2]:
                        await update_bank_balance(ctx, user,amount*4)
                        await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.green,message=f"You rolled three stars and gained {humanize.humanizeNumber(amount*4)} {self.coinname}",fields=f,inline=True))
                elif final[0] == final[1] == final[2]:
                    await update_bank_balance(ctx, user,amount*3)
                    await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.green,message=f"You rolled three identical items and gained {humanize.humanizeNumber(amount*3)} {self.coinname}",fields=f,inline=True))
                else:
                    await update_bank_balance(ctx, user,amount*2)
                    await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.green,message=f"You rolled two identical items and gained {humanize.humanizeNumber(amount*2)} {self.coinname}",fields=f,inline=True))
            else:
                await update_bank_balance(ctx, user,amount*-1)
                await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.red,message=f"You didn't role anything good and lost {humanize.humanizeNumber(amount)} {self.coinname}",fields=f,inline=True))

# ERROR CATCHERS

    @blackjack.error
    @slots.error
    async def errorMessage(self,ctx,error,job=None):
        exty, exob, extr = sys.exc_info()

        if isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
            await self.cooldown_error(ctx,error,exob,job=job)
            return

        await ctx.send(f"errorcatch ```Location:{extr.tb_frame.f_code.co_filename} at line {extr.tb_lineno}\n\n{error}```\nPlease report me to {self.bot.get_user(523209585700372490).mention}")

# ERRORS

    async def cooldown_error(self,ctx,error,output,job=None):
        output=str(output)
        cooldown = float(re.findall(r"[-+]?\d*\.?\d+|\d+",output)[0])
        cooldownHumanized=humanize.humanizeSeconds(int(cooldown))
        response = {
                "work": f"You cannot work for another {cooldownHumanized}.",
                "crime": f"You cannot commit a crime for another {cooldownHumanized}.",
                "slut": f"You cannot be a slut for another {cooldownHumanized}.",
                "rob": f"You cannot rob anyone for another {cooldownHumanized}.",
                "withdraw": f"You cannot withdraw any more {self.coinname} for another {cooldownHumanized}.",
                "deposit": f"You cannot deposit any more {self.coinname} for another {cooldownHumanized}.",
                "send": f"You cannot give anyone any more {self.coinname} for another {cooldownHumanized}.",
            }
        if job not in response.keys():
            await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.red,message=f"You cannot use that command for another {cooldownHumanized}"))
            return
        await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.red,message=response[job]))

# UTILS

    async def newWalletBalance(self,ctx):
        await ctx.send(embed=createEmbed(ctx=ctx,type=embedType.blue,message=f"Your new wallet balance is {humanize.humanizeNumber(await get_bank_balance(ctx, ctx.author,mode='wallet'))} {self.coinname}"))



def setup(bot):
    bot.add_cog(Games(bot))