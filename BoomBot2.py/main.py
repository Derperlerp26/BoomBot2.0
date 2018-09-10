import discord
import discord.ext.commands
from discord.ext import commands
import sys
import os
import time
import json
import logging
from collections import namedtuple
import pickle
import threading

# Load bot settings
if not os.path.isfile('botSettings.json'):
    sys.exit("The botSettings.json file is missing. Get your shit together.")
else:
    with open('botSettings.json') as botSettings:
        jSettings = json.load(botSettings)
    settings = namedtuple("Settings", jSettings.keys())(*jSettings.values())
    botSettings.close()
    print("Settings successfully loaded.")


# Bot and client
Client = discord.Client()
bot = commands.Bot(command_prefix = settings.prefix, case_insensitive = True, description = settings.description)

# Token checker
try:
    hackerman = open('Hackerman.txt', 'r')
except:
    print("Ah ah ah! You didn\'t say the magic word!")
magicWord = str(hackerman.readlines()).translate(dict.fromkeys(map(ord, '[\']'), None))
if sys.platform != "win32":
    magicWord = magicWord[:(len(magicWord) - 2)]

# logs all debug information from discord module
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename = 'BoomBot2Debug.log', encoding = 'utf-8', mode = 'w')
handler.setFormatter(logging.Formatter('%(asctime)s :: %(levelname)s ::\t%(name)s:  %(message)s'))
logger.addHandler(handler)


class ObjStore(object):
    def __init__(self):
        self.tBanList = []
        self.tRoleList = []
        self.pRoleList = []
    def loadFile(self, loadFrom, loadTo):
        try:
            if not os.path.isfile(loadFrom):
                lFile = open(loadFrom, 'w').write('')
            elif os.path.getsize(loadFrom) > 0:
                with open(loadFrom, 'rb') as lFile:
                    self()[loadFrom] = pickle.load(lFile)
                lFile.close()
            print("{} loaded.".format(loadFrom))
            print(self()[loadFrom])
        except Exception as exce:
            print("Error when loading from {}.".format(loadFrom))
            print(exce)
    def loadTempBans(self):
        try:
            if not os.path.isfile('tempBans.txt'):
                tBans = open('tempBans.txt', 'w').write('')
            elif os.path.getsize('tempBans.txt') > 0:
                with open('tempBans.txt', 'rb') as tBans:
                    self.tBanList = pickle.load(tBans)
                tBans.close()
            print("TempBans loaded.")
            print(self.tBanList)
        except Exception as exce:
            print("Error in loadTempBans.")
            print(exce)
    def loadTempRoles(self):
        try:
            if not os.path.isfile('tempRoles.txt'):
                tRoles = open('tempRoles.txt', 'w').write('')
            elif os.path.getsize('tempRoles.txt') > 0:
                with open('tempRoles.txt', 'rb') as tRoles:
                    self.tRoleList = pickle.load(tRoles)
                tRoles.close()
            print("TempRoles loaded.")
            print(self.tRoleList)
        except Exception as exce:
            print("Error in loadTempRoles.")
            print(exce)
    def loadPersistRoles(self):
        try:
            if not os.path.isfile('persistRoles.txt'):
                pRoles = open('persistRoles.txt', 'w').write('')
            elif os.path.getsize('persistRoles.txt') > 0:
                with open('persistRoles.txt', 'rb') as pRoles:
                    self.pRoleList = pickle.load(pRoles)
                pRoles.close()
            print("PersistRoles loaded.")
            print(self.pRoleList)
        except Exception as exce:
            print("Error in loadPersistRoles.")
            print(exce)

class TempBan(object):
    def __init__(self, user, duration, reason, startTime = round(time.time()), guild):
        self.user = user
        self.duration = duration
        self.reason = reason
        self.startTime = startTime
        self.guild = guild

class TempRole(object):
    def __init__(self, userID, duration, startTime = round(time.time()), guild):
        self.userID = userID
        self.duration = duration
        self.roles = []
        self.startTime = startTime
        self.guild = guild

class PersistRole(object):
    def __init__(self, userID, guild):
        self.userID = userID
        self.duration = duration
        self.roles = []
        self.guild = guild

async def checkTime():
    """Checks all temp stuff and persist stuff."""
    while True:
        for tBan in objStore.tBanList:
            if (round(time.time()) - tBan.startTime) > (tBan.duration * 86400):
                await tBan.guild.unban(tBan.user)
        for tRole in objStore.tRoleList:
            for role in tRole.roles:
                if (round(time.time()) - tRole.startTime) > (tRole.duration * 86400):
                    await tRole.guild.get_member(tRole.userID).remove_roles(tBan.role)
        for pRole in objStore.pRoleList:
            for role in pRole.roles:
                if role not in pRole.guild.get_member(pRole.userID).roles:
                    await pRole.guild.get_member(pRole.userID).add_roles(role)
        print("Time checked.")
        time.sleep(900)

async def converter(ctx, user):
    return await commands.MemberConverter().convert(ctx, user)


objStore = ObjStore()
timeChecker = threading.Thread(target = checkTime)

def updateSettings():
    with open('botSettings.json', 'w') as outfile:
        json.dump(settings, outfile, indent = 4)
    outfile.close()

# Run when bot starts
@bot.event
async def on_ready():
    """Where we droppin', boys?"""
    print("{} :: Booted as {} (ID - {})\n".format(time.ctime(), bot.user.name, bot.user.id))
    print("Connected servers: ")
    for guild in bot.guilds:
        print("\tID - {} : Name - {}".format(guild.id, guild.name))
    await bot.change_presence(activity = discord.Game(name = settings.currActivity))
    print("Playing: {}\n\n".format(settings.currActivity))
    objStore.loadTempBans()
    objStore.loadTempRoles()
    objStore.loadPersistRoles()
    #timeChecker.start()

#@bot.event
#async def on_member_update():


@bot.command()
async def listEmojis(ctx):
    """Displays all emotes avaiable on a Server."""
    embed = discord.Embed(title = "Command: listEmojis", description = "All the emotes availible on servers with Boom Bot 2.0:", color = 0x0000ff)
    for emoji in bot.emojis:
        output = ("```" + str(emoji.name, emoji.id, emoji.managed, emoji.server.name) + "```")
        embed.add_field(name = emoji.name, value = output, inline = False)
    await ctx.send(embed = embed)

@bot.command()
async def about(ctx):
    """Tells you 'bout shit, what else would it do?"""
    await ctx.send(content = "About is still a work in progress, so fuck off until it\'s done")

@bot.command()
@commands.has_permissions(administrator = True)
async def changeGame(ctx, *activity):
    """Changes what the bot is playing."""
    embed = discord.Embed(title = "Command: changeGame", color = 0xff0000)
    try:
        settings.currActivity = ' '.join(activity)
        updateSettings()
        await bot.change_presence(activity = discord.Game(name = settings.currActivity))
        embed.description = "Game successfully changed to *{}*".format(settings.currActivity)
        embed.color = 0x00ff00
    except:
        embed.description = "An error has occurred when trying to change the game. If you're reading this, 1) Congrats on fucking up the bot, 2) Contact Xaereus about it."

    except MissingPermissions:
        embed.description = "You do not have permission to use this command. Begone, ***thot***."
    await ctx.send(embed = embed)

@bot.command()
@commands.has_permissions(kick_members = True)
async def tempBan(ctx, user, duration, *reason):
    """Tempbans a mothafucka."""
    embed = discord.Embed(title = "Command: tempBan", color = 0xff0000)
    try:
        for tBan in objStore.tBanList:
            if tBan.user == converter(ctx, user):
                embed.description = "This user is already in the banlist. Get your shit together, kachigga."
        else:
            try:
                objStore.tBanList.append(TempBan(converter(ctx, user), duration, ' '.join(reason), round(time.time()), ctx.message.guild))
                print(objStore.tBanList)
                #await ctx.message.mentions[0].ban(reason = ' '.join(reason), delete_message_days = 0)
                try:
                    with open('tempBans.txt', 'wb') as tBans:
                        pickle.dump(objStore.tBanList, tBans)
                    tBans.close()
                except (ValueError, KeyError, TypeError) as exce:
                    print("Pickle error in tempBan:" + str(exce))
                    embed.add_field(name = "Error:", value = exce)
            except Exception as exce:
                print(exce)
        embed.description = "**{}** has been successfully banned for **{}** days.\nReason: *{}*".format(user, duration, ' '.join(reason))
        embed.color = 0x00ff00
    except Exception as exce:
        print(exce)
        embed.description = "An error has occurred when trying to ban **{}**. If you're reading this, 1) Congrats on fucking up the bot, 2) Contact Xaereus about it.".format(user)
        embed.add_field(name = "Error:", value = exce)

    except MissingPermissions:
        embed.description = "You do not have permission to use this command. Begone, ***thot***."
    await ctx.send(embed = embed)

@bot.command()
@commands.has_permissions(kick_members = True)
async def veiwTBans(ctx):
    """Displays everyone who has been tempbanned."""
    embed = discord.Embed(title = "Command: viewTBans", color = 0x0000ff)
    for tBan in objStore.tBanList:
        if tBan.guild == ctx.message.guild:
            embed.add_field(name = tBan.user.name, value = str(tBan.duration, tban.startTime), inline = False)

    except MissingPermissions:
        embed.description = "You do not have permission to use this command. Begone, ***thot***."
        embed.color = 0xff0000
    await ctx.send(embed = embed)


# Start up the bot
bot.run(magicWord)
