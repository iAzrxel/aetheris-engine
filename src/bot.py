import discord
from config import Config

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Aetheris online como {client.user}!')

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    if message.content.lower().strip() == 'ping':
        await message.channel.send(f'Pong {message.author.mention}! me chamou?')

client.run(Config.DISCORD_TOKEN)