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
        
        if 'done' in temp:
            await self.processDone(message)
            return

        await self.processTitle(message)

    async def processDone(self, message):
        # Removes first char
        title = message.system_content[1:]
        # takes just the title
        title = title.split()[0]

        if title == title1:
            self.dukeQueue.done(message.author)

        elif title == title2: 
            self.architectQueue.done(message.author)

        elif title == title3:
            self.justiceQueue.done(message.author)

        elif title == title4:  
            self.scientistQueue.done(message.author)

    async def processTitle(self, message):
        status, title, X, Y = Command_handler(message.system_content)

        if status == 1:
            order = TitleOrder(title, X, Y, message.author)

            if order.title == title1:
                print(order.title)
                print(order.X)
                print(order.Y)
                await message.channel.send('Roger! The title of: {1} has been reserved for {0}'.format(message.author.mention,title))
                self.dukeQueue.put(order)

            elif order.title == title2:
                print(order.title)
                print(order.X)
                print(order.Y)
                await message.channel.send('Roger! The title of: {1} has been reserved for {0}'.format(message.author.mention,title))  
                self.architectQueue.put(order)

            elif order.title == title3:
                print(order.title)
                print(order.X)
                print(order.Y)
                await message.channel.send('Roger! The title of: {1} has been reserved for {0}'.format(message.author.mention,title))  
                self.justiceQueue.put(order)

            elif order.title == title4:
                print(order.title)
                print(order.X)
                print(order.Y)
                await message.channel.send('Roger! The title of: {1} has been reserved for {0}'.format(message.author.mention,title))   
                self.scientistQueue.put(order)

            else:
                await message.channel.send('Error! The title of: {1} does not exist {0}'.format(message.author.mention,title))   

        elif status == 2:
            print()

        else:
            print()
    