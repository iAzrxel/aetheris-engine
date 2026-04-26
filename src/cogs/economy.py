from services.economy_service import ensure_account, get_balance, get_last_work, update_work, deposit_money, withdraw_money, rob_user
from services.moderation_service import ensure_user, ensure_guild
import discord
import datetime
import random

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

    embed = discord.Embed(description=f'Você trabalhou e recebeu **${salary:,}**', color=0x00FF00 )
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
            embed = discord.Embed(description=f'❌ Comando invalido!', color=0xFF0000)
            embed.set_author(
                name=user.name,
                icon_url=user.display_avatar.url
            )
            embed.add_field(
                name='Use:',
                value='`.dep <amount, half ou all>`',
                inline=True
            )
            await message.channel.send(embed=embed)
            return

        balance, bank = get_balance(user.id, message.guild.id)

        if args[1].lower() == "all":
            amount = balance
        elif args[1].lower() == "half":
            amount = (balance // 2)
        else:
            try:
                amount = int(args[1])
            except ValueError:
                embed = discord.Embed(description=f'❌ Comando invalido!', color=0xFF0000)
                embed.set_author(
                    name=user.name,
                    icon_url=user.display_avatar.url
                )
                embed.add_field(
                    name='Use:',
                    value='`.dep <amount, half ou all>`',
                    inline=True
                )
                await message.channel.send(embed=embed)
                return
                    
        if amount <= 0:
            amount = abs(amount)
        
        if amount > balance:
              embed = discord.Embed(description=f'❌ Você não tem esse valor em mãos.', color=0xFF0000)
              embed.set_author(
              name=user.name,
              icon_url=user.display_avatar.url                
              )
              await message.channel.send(embed=embed)
              return
        
        success = deposit_money(user.id, message.guild.id, amount)

        if not success:
           embed = discord.Embed(description=f'❌ Você não pode depositar ${amount}.', color=0xFF0000)
           embed.set_author(
           name=user.name,
           icon_url=user.display_avatar.url                
          )
           await message.channel.send(embed=embed)
           return
        
        embed = discord.Embed(description=f'✅ Depositou ${amount} no seu banco!', color=0x00FF00)
        embed.set_author(
            name=user.name,
            icon_url=user.display_avatar.url
        )
        await message.channel.send(embed=embed)
        return

async def handle_withdraw(message, args):
    user = message.author

    ensure_user(user.id, user.name)
    ensure_guild(message.guild.id, message.guild.name)
    ensure_account(user.id, message.guild.id)

    if len(args) < 2:
     embed = discord.Embed(description=f'❌ Comando invalido!', color=0xFF0000)
     embed.set_author(
     name=user.name,
     icon_url=user.display_avatar.url
     )
     embed.add_field(
     name='Use:',
     value='`.with <amount, half ou all>`',
     inline=True
     )
     await message.channel.send(embed=embed)
     return

    balance, bank = get_balance(user.id, message.guild.id)

    if args[1].lower() == 'all':
        amount = bank
    elif args[1].lower() == 'half':
        amount = (bank // 2)
    else:
        try:
            amount = int(args[1])
        except ValueError:
                embed = discord.Embed(description=f'❌ Comando invalido!', color=0xFF0000)
                embed.set_author(
                    name=user.name,
                    icon_url=user.display_avatar.url
                )
                embed.add_field(
                    name='Use:',
                    value='`.with <amount, half ou all>`',
                    inline=True
                )
                await message.channel.send(embed=embed)
                return

    if amount < 0:
        amount = abs(amount)
    
    if amount > bank:
           embed = discord.Embed(description=f'❌ Você não tem esse valor em mãos.', color=0xFF0000)
           embed.set_author(
           name=user.name,  
           icon_url=user.display_avatar.url                
          )
           await message.channel.send(embed=embed)
           return

    success = withdraw_money(user.id, message.guild.id, amount)

    if not success:
       embed = discord.Embed(description=f'❌ Você não pode retirar ${amount}.', color=0xFF0000)
       embed.set_author(
       name=user.name,
       icon_url=user.display_avatar.url                
     )
       await message.channel.send(embed=embed)
       return

    embed = discord.Embed(description=f'✅ Retirou ${amount} do seu banco!', color=0x00FF00)
    embed.set_author(
    name=user.name,
    icon_url=user.display_avatar.url
  )
    await message.channel.send(embed=embed)
    return

async def handle_rob_user(message):
    user = message.author
    if len(message.mentions) > 0:
        target = message.mentions[0]
    else:
        embed = discord.Embed(description=f'❌ Comando invalido!', color=0xFF0000)
        embed.set_author(
        name=user.name,
        icon_url=user.display_avatar.url
        )
        embed.add_field(
        name='Use:',
        value='`.rob <@user>`',
                    inline=True
        )
        await message.channel.send(embed=embed)
        return
    
    ensure_user(user.id, user.name)
    ensure_guild(message.guild.id, message.guild.name)
    ensure_account(user.id, message.guild.id)

    ensure_user(target.id, user.name)
    ensure_account(user.id, message.guild.id)

    balance, bank = get_balance(target.id, message.guild.id)

    if balance < 1:
        embed = discord.Embed(description=f'❌ Você tentou roubar {target.mention} mas {target.name.lower()} não tem um centavo na carteira.', color=0xFF0000)
        embed.set_author(
        name=user.name,  
        icon_url=user.display_avatar.url                
        )
        await message.channel.send(embed=embed)
        return


    success = random.random() < 0.6
    if success:
        amount = balance * 60 // 100
        success = rob_user(user.id, target.id, message.guild.id, amount)
        if success:
            embed = discord.Embed(description=f'✅ {user.mention} roubou ${amount} de {target.mention}!', color=0x00FF00)
            embed.set_author(
            name=user.name,
            icon_url=user.display_avatar.url
        )
            await message.channel.send(embed=embed)
            return
        else:
            await message.channel.send('Erro inesperado.')
            return
    else:
        await message.channel.send('Você não conseguiu roubar e futuramente será punido!')
        return