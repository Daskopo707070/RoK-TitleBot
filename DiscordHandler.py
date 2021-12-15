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
            await message.channel.send('Error! The inputed title does not exist {1}'.format(message.author.mention))
            return
        
        # Status 1: Request for a title
        if status == 1:
            # Check if the user has a opened request. This is to prevent same user requesting multiple time in a row
            isUserOnQueue = titleQueue.isUserOnQueue(order)
            if isUserOnQueue:
                await message.channel.send('Sorry {0}, you have already a request pending for {1}'.format(message.author.mention, order.title))

            elif titleQueue.put(order):
                await message.channel.send('Roger! The title of: {0} has been reserved for {1}'.format(order.title, message.author.mention))

        # Status 2: Release of a title
        elif status == 2:
            if titleQueue.done(message.author):
                await message.channel.send('Roger! Title {0} has been released. Thanks {1}'.format(order.title, message.author.mention))

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