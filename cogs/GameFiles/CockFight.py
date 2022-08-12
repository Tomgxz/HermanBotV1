import random
from utils import config as cfg
from utils.emojiData import getEmoji
from utils.Items import newChicken
from cogs.Economy import update_bank_balance,get_bank_balance
from utils.embedCreator import createEmbed, embedType
    
def userChickens(ctx,user):
    return cfg.getUsersSettings(ctx)[str(user.id)]["items"]["chicken"]

def killChicken(ctx,user):
    cfg.setUsersSettings(ctx)[str(user.id)]["items"]["chicken"] = []

async def startGame(ctx,user,bet):
    if len(userChickens(ctx,user)) == 0:
        return True,createEmbed(ctx=ctx,type=embedType.red,message="You need to buy a chicken from the store first using the command buy chicken")

    chicken = userChickens(ctx,user)[0]
    opponent = newChicken()

    if chicken.strength >= opponent.strength:
        await update_bank_balance(ctx,user,change=bet)
        return False,createOutputEmbed(ctx,bet=bet,stre=chicken.strength)
    await update_bank_balance(ctx,user,change=-1*bet)
    return False, createOutputEmbed(ctx,bet=bet,stre=chicken.strength,type="lose",)

def createOutputEmbed(ctx,type="win",bet=0,stre=0):
    if type=="win":
        embed = createEmbed(ctx=ctx,type=type,message=f"Your lil chicken won the fight, and made you {bet} credits richer! :rooster:",footer=f"Chicken Strength (used to determine winner): {stre}")
    else:
        ripEmoji=getEmoji("rip")
        embed = createEmbed(ctx=ctx,type=type,message=f"Your chicken died {ripEmoji}",footer=f"Chicken Strength (used to determine winner): {stre}")
    return embed
