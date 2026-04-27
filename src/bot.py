import discord
from config import Config
from cogs.moderation import (
    handle_warn,
    handle_warnings,
    handleclear_warns
) 
from cogs.economy import handle_balance, handle_work, handle_deposit, handle_withdraw, handle_rob_user, handle_fines, handle_pay_fines

intents = discord.Intents.default()
intents.message_content = True

AETHERIS_CHANNEL_NAME = "aetheris-bot"

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Aetheris online como {client.user}!")

    for guild in client.guilds:
        existing_channel = discord.utils.get(
            guild.text_channels,
            name=AETHERIS_CHANNEL_NAME
        )

        if existing_channel is None:
            channel = await guild.create_text_channel(AETHERIS_CHANNEL_NAME)
            print(f"Canal criado em {guild.name}: #{channel.name}")
        else:
            print(f"Canal já existe em {guild.name}: #{existing_channel.name}")


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
    if message.author.bot:
        return

    if message.guild is None:
        return

    if message.channel.name != AETHERIS_CHANNEL_NAME:
        return

    content = message.content.strip()

    if content.lower() == "ping":
        await message.channel.send(f"Pong {message.author.mention}! me chamou?")
        return

    if not content.startswith(Config.PREFIX):
        return

    args = content[len(Config.PREFIX):].split()

    if len(args) == 0:
        return

    command = args[0].lower()

    if command == "warn":
        await handle_warn(message, args, client)
        return

    if command == "warnings":
        await handle_warnings(message)
        return

    if command == "clearwarns":
        await handleclear_warns(message)
        return
    
    if command in ["bal", "balance"]:
        await handle_balance(message)
        return
    
    if command == 'work':
        await handle_work(message)
        return
    if command in ["dep", "deposit"]:
        await handle_deposit(message, args)
        return
    if command in ["with", "withdraw"]:
        await handle_withdraw(message, args)
        return
    if command == "rob":
        await handle_rob_user(message)
        return
    if command == "fines":
        await handle_fines(message)
    if command == "payfines":
        await handle_pay_fines(message)
    
client.run(Config.DISCORD_TOKEN)