import json


def getConfig():
    with open("utils/config.json", "r") as f:
        return json.load(f)


def setConfig(new):
    with open("utils/config.json", "w") as f:
        json.dump(new, f)


def getGuildSettings(ctx):
    data = getConfig()
    return data[str(ctx.guild.id)]["settings"]


def setGuildSettings(ctx, new):
    data = getConfig()
    data[str(ctx.guild.id)]["settings"] = new
    setConfig(data)


def getUsersSettings(ctx):
    data = getConfig()
    return data[str(ctx.guild.id)]["users"]


def setUsersSettings(ctx, new):
    data = getConfig()
    data[str(ctx.guild.id)]["users"] = new
    setConfig(data)
