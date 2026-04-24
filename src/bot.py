import discord
from config import Config

intents = discord.Intents.default()
intents.message_content = True
AETHERIS_CHANNEL_NAME = 'aetheris-bot'

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Aetheris online como {client.user}!')
    global channel
    for guild in client.guilds:
        existing_channel = discord.utils.get(
            guild.text_channels,
            name=AETHERIS_CHANNEL_NAME
        )

        if existing_channel is None:
            channel = await guild.create_text_channel(AETHERIS_CHANNEL_NAME)
            print(f'canal criado em {guild.name}: #{channel.name}')
        else:
            print(f'canal já existe em {guild.name}: #{existing_channel}')

@client.event
async def on_guild_join(guild):
    existing_channel = discord.utils.get(
        guild.text_channels,
        name=AETHERIS_CHANNEL_NAME
    )

    if existing_channel is None:
        channel = await guild.create_text_channel(AETHERIS_CHANNEL_NAME)
        print(f"Canal criado ao entrar em {guild.name}: #{channel.name}")

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    
    if message.guild is None:
        return
    
    if message.channel.name != AETHERIS_CHANNEL_NAME:
        return
    
    if message.content.lower().strip() == 'ping':
        await message.channel.send(f'Pong {message.author.mention} ! me chamou?')

client.run(Config.DISCORD_TOKEN)