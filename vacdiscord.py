import discord
import config
import time

class VaccineNotification:
    def __init__(self):
        pass
        self.client = discord.Client()
        
    def sendNotification(self,link):
        @self.client.event
        async def on_ready():
            print('ran')
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="vaccine appointments"))
            await self.client.guilds[0].channels[2].send(f"**Vaccine Found!**\n{link}")
            await self.client.close()
            time.sleep(0.1)
        self.client.run(config.discordbotapikey)
        time.sleep(0.1)

    def testNotification(self,link):
        @self.client.event
        async def on_ready():
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="vaccine appointments"))
            await self.client.guilds[0].channels[4].send(f"**Vaccine Not Found!**\n{link}")
            print('ran test notification')
            await self.client.close()
            time.sleep(0.1)
        self.client.run(config.discordbotapikey)
        time.sleep(0.1)