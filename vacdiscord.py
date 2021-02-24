import discord
import config

class VaccineNotification:
    def __init__(self):
        pass
        self.client = discord.Client()
        
    def sendNotification(self,link):
        @self.client.event
        async def on_ready():
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="vaccine appointments"))
            await self.client.guilds[0].channels[2].send("**Vaccine Found!**")
            await self.client.guilds[0].channels[2].send(link)
            print('ran')
            await self.client.close()
        self.client.run(config.discordbotapikey)

    def testNotification(self,link):
        @self.client.event
        async def on_ready():
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="vaccine appointments"))
            await self.client.guilds[0].channels[2].send("**Vaccine Not Found!**")
            await self.client.guilds[0].channels[2].send(link)
            print('ran test notification')
            await self.client.close()
        self.client.run(config.discordbotapikey)