import threading, queue
from RokBot import RokBot
from DiscordHandler import DiscordHandler
from TitleQueue import TitleQueue
from TitleType import TitleType
from helpers import initWorker
import os
from dotenv import load_dotenv

# Load local Environment Variables
load_dotenv()

# Create Rok Bot
rokBot = RokBot()

# Run the rok worker. This worker is reponsible to process run the request in ROK
threading.Thread(target=initWorker, args=[rokBot], daemon=True).start()

# Creating one queue for each title
titlesQueues = {
  'dukeQueue': TitleQueue(TitleType.DUKE, rokBot.queue),
  'architectQueue': TitleQueue(TitleType.ARCHITECT, rokBot.queue),
  'justiceQueue': TitleQueue(TitleType.JUSTICE, rokBot.queue),
  'scientistQueue': TitleQueue(TitleType.SCIENTIST, rokBot.queue)
}

# Run all Title queues in seprated thread. Each Thread will receive an order from discord bot. Each request will be added to
# rokQueue and waited for x minutes. 
for key, value in titlesQueues.items():
  threading.Thread(target=initWorker, args=[value], daemon=True).start()

# Start discord bot
discordHandler = DiscordHandler()

# Pass the Queue object so the discord bot can add tasks to the Queue
discordHandler.init(titlesQueues)
discordHandler.run((os.environ['DISCORD_BOT'])) #The mumbo jumbo as the parameter is the "key" for the discord bot

print('Application finished')