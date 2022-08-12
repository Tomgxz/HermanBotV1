import enum, discord

class embedType(enum.Enum):
    green=0
    red=1
    blue=2
    other=3
    announcement=4
    gray=5

def getColor(type:embedType):
    if type == embedType.green:
        return 0x66bb6a
    if type == embedType.red:
        return 0xEF5350
    if type == embedType.announcement:
        return 0x17d1af
    if type == embedType.gray:
        return 0xa3a3a3
    return 0x03a9f4

def createEmbed(ctx=None,type:embedType=embedType.blue,title="TITLE",message="MESSAGE",fields=[[]],inline=False,footer=" "):
    return embed(ctx=ctx,type=type,message=message,fields=fields,inline=inline,footer=footer)


def embed(ctx=None,type:embedType=embedType.blue,title=" ",message="MESSAGE",fields=[[]],inline=False,footer=None):
    embed=discord.Embed(title=" ", description=message, color=getColor(type))
    if fields != [[]]:
        for i in range(len(fields)):
            embed.add_field(name=fields[i][0],value=fields[i][1],inline=inline)
    embed.set_author(name='{0.name}#{0.discriminator}'.format(ctx.author), icon_url=ctx.author.avatar_url)
    if footer == None:
        embed.set_footer(text=f"Original command: {ctx.message.content}")
    else:
        embed.set_footer(text=f"{footer}\nOriginal command: {ctx.message.content}")
    return embed
