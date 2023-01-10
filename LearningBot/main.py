import os
import discord
import json
from queue import PriorityQueue
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
INTENTS = discord.Intents.default()
INTENTS.message_content = True

client = discord.Client(intents=INTENTS)


@client.event
async def on_ready():
    await client.login(TOKEN)
    print(f'{client.user} has successfully logged in')


@client.event
async def on_message(message):

    ##if we sent the message ignore
    if message.author.name == client.user.name:
        return

    ##returns top 10
    if message.content.startswith("$leaderboard"):
        list = createLeaderboard(message)
        count = 1
        for person in list:
            await message.channel.send('{}. {} has said N**** {} times'.format(count, person["name"],str(person["wordcount"])))
            count += 1
        return

    ##returns personal count
    if message.content.startswith("$mycount"):
        await message.channel.send('You have said PLEASE {} times'.format(obtainCount(message)))

    #Determine amount of instances of word in message context
    temp = 0
    msg = message.content.split(" ")
    for words in msg:
        if words == "please" or words == "Please" or words == "PLEASE":
            temp += 1
            ##We need to figure out how to make this not send after every message

    if temp >= 1:
        await message.channel.send("You said PLEASE {} times".format(temp))

    ##vars for json insertion and updates
    jDict = loadJSON()
    found = False

    ##search until found and when found ret to exit on_message with update JSON
    while not found:
        for key in jDict["members"]:
            for subkey in key:
                if subkey == "name" and key[subkey] == message.author.name:
                    found = True
                    ##now need to jump to word count while within list meaning same key
                    key["wordcount"] += temp
                    dumpJSON(jDict)
                    return
            found = True

    ##here if not found in JSON so need to update
    temp = {"name": message.author.name, "wordcount": temp}
    jDict["members"].append(temp)
    dumpJSON(jDict)

    ##dump updated JSON & reset temp
    temp = 0
    found = False


def loadJSON():
    with open('counters.json', 'r') as f:
        counters = json.load(f)
    return counters


def dumpJSON(counters):
    with open('counters.json', 'w') as g:
        json.dump(counters, g)

def createLeaderboard(message):
    ##use prio que with vals wrapped in a tupple with the wordcount in front
    jDict = loadJSON()
    pque = PriorityQueue()
    list = []

    for key in jDict["members"]:
        for subkey in key:
            if subkey == "name":
                pque.put((-key["wordcount"], key["name"]))

    count = 0
    while count <= 10 and not pque.empty():
        tempTup = pque.get()
        temp = {"name": tempTup[1], "wordcount": -tempTup[0]}
        list.append(temp)

    return list

def obtainCount(message):
    dict = loadJSON()
    for key in dict["members"]:
        for subkey in key:
            if subkey == "name" and key[subkey] == message.author.name:
                print (key["name"])
                return key["wordcount"]
    return None


client.run(TOKEN)
