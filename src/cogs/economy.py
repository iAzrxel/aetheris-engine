from services.economy_service import ensure_account, get_balance, get_last_work, update_work, deposit_money, withdraw_money
from services.moderation_service import ensure_user, ensure_guild
import discord
import datetime

async def handle_balance(message):
    if len(message.mentions) > 0:
        target = message.mentions[0]
    else:
        target = message.author

    ensure_user(target.id, target.name)
    ensure_guild(message.guild.id, message.guild.name)
    ensure_account(target.id, message.guild.id)

    balance, bank = get_balance(target.id, message.guild.id)
    total = balance + bank

    embed = discord.Embed(description = "Saldo Bancario", color=0x6A0DAD)

    embed.set_author(
        name=target.name,
        icon_url=target.display_avatar.url
    )

    embed.add_field(
        name="Carteira",
        value=f'${balance:,}',
        inline=True
    )

    embed.add_field(
        name="Banco",
        value=f'${bank:,}',
        inline=True
    )

    embed.add_field(
        name="Total",
        value=f'${total:,}',
        inline=True
    )
    await message.channel.send(embed=embed)

async def handle_work(message):
    user = message.author

    ensure_user(user.id, user.name)
    ensure_guild(message.guild.id, message.guild.name)
    ensure_account(user.id, message.guild.id)

    last_work = get_last_work(user.id, message.guild.id)

    if last_work:
        now = datetime.datetime.now()
        diff = now - last_work

        if diff < datetime.timedelta(minutes=3):
            remaining = 180 - int(diff.total_seconds())
            minutes = remaining // 60
            seconds = remaining % 60

            time_str = f'{minutes}m {seconds}s'

            embed = discord.Embed(description=f'Você precisa descansar mais **{time_str}** antes de trabalhar novamente.', color=0xFFFF00)
            embed.set_author(
                name=user.name,
                icon_url=user.display_avatar.url
            )
            await message.channel.send(embed=embed)
            return
    salary = 1800

    update_work(user.id, message.guild.id, salary)

    embed = discord.Embed(description=f'Você trabalhou e recebeu **${salary:,}**', color=0x88E788)
    embed.set_author(
        name=user.name,
        icon_url=user.display_avatar.url
    )
    await message.channel.send(embed=embed)

async def handle_deposit(message, args):
        user = message.author

        ensure_user(user.id, user.name)
        ensure_guild(message.guild.id, message.guild.name)
        ensure_account(user.id, message.guild.id)

        if len(args) < 2:
            await message.channel.send("Use: `.deposit <valor>`, `.deposit half` ou `.deposit all`")
            return

        balance, bank = get_balance(user.id, message.guild.id)

        if args[1].lower() == "all":
            amount = balance
        elif args[1].lower() == "half":
            amount = (balance / 2)
        else:
            if not args[1].isdigit():
                await message.channel.send('Informe um valor valido')
                return
            amount = int(args[1])
        
        if amount <= 0:
            await message.channel.send('O valor precisa ser maior que 0.')
            return
        
        if amount > balance:
            await message.channel.send('Você não tem esse valor em mãos.')
            return
        
        success = deposit_money(user.id, message.guild.id, amount)

        if not success:
            await message.channel.send('Não foi possivel depositar esse valor.')
            return
        
        await message.channel.send('Sucesso!')

async def handle_withdraw(message, args):
    user = message.author

    ensure_user(user.id, user.name)
    ensure_guild(message.guild.id, message.guild.name)
    ensure_account(user.id, message.guild.id)

    if len(args) < 2:
        await message.channel.send('Use: `.withdraw <valor>`, `.withdraw half` ou `.withdraw all`')
        return

    balance, bank = get_balance(user.id, message.guild.id)

    if args[1].lower() == 'all':
        amount = bank
    elif args[1].lower() == 'half':
        amount = (bank / 2)
    else:
        if not args[1].isdigit():
            await message.channel.send('Informe um valor valido.')
            return
        amount = int(args[1])

    if amount < 0:
        await message.channel.send('O valor precisa ser maior que 0.')
        return
    
    if amount > bank:
        await message.channel.send('Você não tem esse valor no banco.')

    success = withdraw_money(user.id, message.guild.id, amount)

    if not success:
        await message.channel.send('Não foi possivel sacar esse valor.')
        return

    await message.channel.send('Sucesso!')