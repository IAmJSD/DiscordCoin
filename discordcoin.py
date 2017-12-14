print("""
 ____ ____ ____ ____ ____ ____ ____ ____ ____ ____ ____ 
||D |||i |||s |||c |||o |||r |||d |||C |||o |||i |||n ||
||__|||__|||__|||__|||__|||__|||__|||__|||__|||__|||__||
|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|

Created by JakeMakesStuff (Jake#0009) And licensed under the GNU license. I refuse to provide any GitHub support if you modify the code. Sorry, I cannot support 10,000 different versions.
""")
# ASCII AND LICENSING!!!!!1111

import discord, json, logging, asyncio
from pymongo import MongoClient
from decimal import *
from random import randint
# Imports go here.

mclient = MongoClient()
dclient = discord.Client()
# Defines the clients.

commands = dict()
# A dict of commands.

def command(desc):
    def deco(func):
        commands[func.__name__] = [func, desc]
    return deco
# The command decorator.

with open("config.json", "r") as config:
    config = json.load(config)
# Loads the conifg.

dcoin = mclient.dcoin
# Defines the database.

wallets = dcoin.wallets
# Defines the wallet collection.

logging.basicConfig(level=logging.INFO)
# Sets the logging level.

logger = logging.getLogger("DiscordCoin")
# Sets the bots logger.

free_coins = True
# Toggles the free coin command.

already_redeemed_hourly = []
# If the free coin command is on, this list will be occupied by people that have already redeemed their hourly free coins.

def rand_decimal(divide_by, start, end):
    return Decimal(randint(start, end)) / Decimal(divide_by)
# Creates a random decimal.

def create_embed(title = None, desc = None, colour = None):
    if colour == None:
        embed=discord.Embed(title=title, description=desc)
    else:
        embed=discord.Embed(title=title, description=desc, colour=colour)
    embed.set_footer(text=dclient.user.name + " " + config["version"])
    return embed
# Creates a embed.

def pass_user(string : str, server):
    return server.get_member(string.rstrip(' ').lstrip('<@').lstrip('!').rstrip('>'))
# Converts str to discord.user.

@command("Gets help for the bot.")
async def help(message):
    string = ""
    for cmd in commands:
        string = string + config["prefix"] + commands[cmd][0].__name__ + " - " + commands[cmd][1] + "\n"
    if string == "":
        string = "No commands found."
    string = "```" + string + "```"
    try:
        await dclient.send_message(message.author, embed=create_embed(dclient.user.name + " Help:", string))
        await dclient.send_message(message.channel, embed=create_embed(":postbox: Check your DM's.", colour=0x00ff40))
    except:
        pass
# Sends help to a user.

@command("Creates a wallet for you if you do not have one already.")
async def create(message):
    if wallets.find_one({"user_id" : message.author.id}) == None:
        wallets.insert_one({"user_id" : message.author.id, "balance" : "0"})
        try:
            await dclient.send_message(message.channel, embed=create_embed(":white_check_mark: Wallet created.", colour=0x00ff40))
        except:
            pass
    else:
        try:
            await dclient.send_message(message.channel, embed=create_embed(":triangular_flag_on_post: A wallet was already found for you.", colour=0xff0000))
        except:
            pass
# Creates a wallet for a user.

@command("Allows you to check the amount in your wallet.")
async def balance(message):
    if wallets.find_one({"user_id" : message.author.id}) == None:
        try:
            await dclient.send_message(message.channel, embed=create_embed(":triangular_flag_on_post: A wallet was not found for you. Please use " + config["prefix"] + "create to create one.", colour=0xff0000))
        except:
            pass
    else:
        w = wallets.find_one({"user_id" : message.author.id})
        desc = "Your balance is " + w["balance"] + " coins."
        try:
            await dclient.send_message(message.channel, embed=create_embed("Balance", desc))
        except:
            pass
# Checks the users balance.

@command("Allows you to give money to another user. (The usage is " + config["prefix"] + "pay amount user)")
async def pay(message):
    args = message.content.split(' ')
    del args[0]
    if len(args) < 2:
        try:
            await dclient.send_message(message.channel, embed=create_embed(":triangular_flag_on_post: Incorrect usage of this command.", colour=0xff0000))
        except:
            pass
    else:
        try:
            amount = Decimal(args[0])
            user = pass_user(args[1], message.server)
            if args[0].startswith("-"):
                try:
                    await dclient.send_message(message.channel, embed=create_embed(":triangular_flag_on_post: You cannot send negative values.", colour=0xff0000))
                except:
                    pass
            else:
                if user == None:
                    try:
                        await dclient.send_message(message.channel, embed=create_embed(":triangular_flag_on_post: The user you gave could not be found on this servers' user cache.", colour=0xff0000))
                    except:
                        pass
                else:
                    if wallets.find_one({"user_id" : message.author.id}) == None:
                        try:
                            await dclient.send_message(message.channel, embed=create_embed(":triangular_flag_on_post: A wallet was not found for you. Please use " + config["prefix"] + "create to create one.", colour=0xff0000))
                        except:
                            pass
                    else:
                        w = wallets.find_one({"user_id" : message.author.id})
                        if amount > Decimal(w["balance"]):
                            try:
                                await dclient.send_message(message.channel, embed=create_embed(":triangular_flag_on_post: You are trying to withdraw more than you have.", colour=0xff0000))
                            except:
                                pass
                        else:
                            w2 = wallets.find_one({"user_id" : user.id})
                            if w2 == None:
                                try:
                                    await dclient.send_message(message.channel, embed=create_embed(":triangular_flag_on_post: Your friend you tagged does not have a wallet. Please tell them to use " + config["prefix"] + "create to create one.", colour=0xff0000))
                                except:
                                    pass
                            else:
                                wallets.delete_one(w)
                                wallets.delete_one(w2)
                                w["balance"] = str(Decimal(w["balance"]) - amount)
                                wallets.insert_one(w)
                                w2["balance"] = str(Decimal(w2["balance"]) + amount)
                                wallets.insert_one(w2)
                                try:
                                    await dclient.send_message(message.channel, embed=create_embed(":white_check_mark: User paid.", colour=0x00ff40))
                                except:
                                    pass
        except:
            try:
                await dclient.send_message(message.channel, embed=create_embed(":triangular_flag_on_post: The first argument could not be converted to a decimal number.", colour=0xff0000))
            except:
                pass
# Allows you to pay another user.

async def time_reset_loop():
    while True:
        await asyncio.sleep(3600)
        already_redeemed_hourly = []
# A loop to reset the list "already_redeemed_hourly" hourly.

if free_coins:
    @command("Gives you part of a coin for free every hour.")
    async def free(message):
        if wallets.find_one({"user_id" : message.author.id}) == None:
            try:
                await dclient.send_message(message.channel, embed=create_embed(":triangular_flag_on_post: A wallet was not found for you. Please use " + config["prefix"] + "create to create one.", colour=0xff0000))
            except:
                pass
        elif message.author in already_redeemed_hourly:
            try:
                await dclient.send_message(message.channel, embed=create_embed(":triangular_flag_on_post: Try again in an hour.", colour=0xff0000))
            except:
                pass
        else:
            w = wallets.find_one({"user_id" : message.author.id})
            d = rand_decimal(1000, 1, 100)
            wallets.delete_one(w)
            w["balance"] = str(Decimal(w["balance"]) + d)
            wallets.insert_one(w)
            already_redeemed_hourly.append(message.author)
            try:
                await dclient.send_message(message.channel, embed=create_embed(":white_check_mark: " + str(d) + " coin(s) were given to you.", colour=0x00ff40))
            except:
                 pass
# Gives you free coins.

@dclient.event
async def on_message(message):
    if message.content.startswith(config["prefix"]):
        cmd = message.content.lstrip(config["prefix"]).split(' ')[0].lower()
        if cmd in commands:
            await commands[cmd][0](message)
# Defines on_message.

@dclient.event
async def on_ready():
    logger.info("Logged in as " + dclient.user.name)
    dclient.loop.create_task(time_reset_loop())
    await dclient.change_presence(game=discord.Game(name=config["game"].replace("[p]", config["prefix"])))
# Defines on_ready.

dclient.run(config["token"])
# Starts the Discord client.
