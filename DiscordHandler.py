import discord
import sys
from Command_handler import *
from Title_Order import TitleOrder

title1 = "duke" 
title2 = "architect"
title3 = "justice"
title4 = "scientist"

class DiscordHandler(discord.Client):
    def init(self, titlesQueue):
        print(f'Save Queue objects in Discord Bot')
        self.dukeQueue = titlesQueue["dukeQueue"]
        self.architectQueue = titlesQueue["architectQueue"]
        self.justiceQueue = titlesQueue["justiceQueue"]
        self.scientistQueue = titlesQueue["scientistQueue"]
        
    async def on_ready(self):
        print('We have logged in as {0}'.format(self.user))

    async def on_message(self, message):
        if message.author == self.user: #checks if the msg came from the bot itself
            return

        if message.content.startswith('$'): #Looks for a msg that starts with '$' char
            await self.processMessage(message)

        else:
            await message.channel.send('Command not valid {0}'.format(message.author.mention))
    
    async def processMessage(self, message):
        temp = message.system_content  #Stores the content of the message

        if temp == "$die":
            await message.channel.send('shutting down')
            print("bot down")
            await self.close()
        
        status, title, X, Y = Command_handler(message.system_content)
        order = TitleOrder(title, X, Y, message.author)

        await self.processRequest(status, order, message)

    async def processRequest(self, status, order, message):
        titleQueue = self.getQueueTitle(order.title)
        if titleQueue is None:
            await message.channel.send('Error! The title of: {1} does not exist {0}'.format(message.author.mention, order.title))
            return
        
        # Status 1: Request for a title
        # Status 2: Release of a title
        if status == 1:
            await message.channel.send('Roger! The title of: {1} has been reserved for {0}'.format(message.author.mention, order.title))
            titleQueue.put(order)

        elif status == 2:
            await message.channel.send('Roger! Title {0} has been released. Thanks {1}'.format(order.title, message.author.mention))
            titleQueue.done(message.author)

        else:
            print()
    
    def getQueueTitle(self, title):
        queueDic = {
            "duke": self.dukeQueue,
            "architect": self.architectQueue,
            "justice": self.justiceQueue,
            "scientist": self.scientistQueue
        }
        return queueDic.get(title)