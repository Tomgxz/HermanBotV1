import discord
from discord.ext import commands

async def check_permissions(ctx, perms, *, check=all):
    if ctx.author.id == ctx.guild.owner.id:
        return True

    resolved=ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved,name,None)==value for name,value in perms.items())

def hasPermissions(*,check=all,**perms):
    async def pred(ctx):
        return await check_permissions(ctx, perms, check=check)
    return commands.check(pred)

def canSend(ctx):
    return (
        isinstance(ctx.channel, discord.DMChannel)
        or ctx.channel.permissions_for(ctx.guild.me).send_messages
    )
def canEmbed(ctx):
    return (
        isinstance(ctx.channel, discord.DMChannel)
        or ctx.channel.permissions_for(ctx.guild.me).embed_links
    )
def canUpload(ctx):
    return (
        isinstance(ctx.channel, discord.DMChannel)
        or ctx.channel.permissions_for(ctx.guild.me).attach_filesz
    )
def canReact(ctx):
    return (
        isinstance(ctx.channel, discord.DMChannel)
        or ctx.channel.permissions_for(ctx.guild.me).add_reactions
    )