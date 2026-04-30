import discord
import datetime
from services.moderation_service import (
    ensure_user,
    ensure_guild,
    create_warn,
    count_warns,
    count_warns_since_last_punishment,
    count_mutes,
    create_punishment,
    clear_warns
)

async def handle_warn(message: discord.Message, args: list[str], client: discord.Client):
    if not message.author.guild_permissions.manage_messages:
        await message.channel.send("Você não tem permissão para usar esse comando.")
        return

    if len(message.mentions) == 0:
        await message.channel.send("Use: `.warn @user <motivo>`")
        return

    target = message.mentions[0]

    if target == message.author:
        await message.channel.send("Você não pode se avisar.")
        return

    if target == client.user:
        await message.channel.send("Você está tentando me avisar? 😱")
        return

    reason = " ".join(args[2:]) if len(args) > 2 else "Sem motivo informado"

    ensure_user(target.id, target.name)
    ensure_guild(message.guild.id, message.guild.name)

    current_cycle_warns = count_warns_since_last_punishment(target.id, message.guild.id)
    mute_count = count_mutes(target.id, message.guild.id)

    if current_cycle_warns >= 3:
        if mute_count >= 3:
            await target.kick(reason=reason)

            create_punishment(
                target.id,
                message.guild.id,
                "kick",
                reason
            )

            await message.channel.send(f'{target.mention} atingiu o limite disciplinar e foi kickado do servidor ⚠️')
            return
        
        mute_minutes = 60 * (2 ** mute_count)

        await target.timeout_for(
            datetime.timedelta(minutes=mute_minutes),
            reason=reason
        )

        create_punishment(
            target.id,
            message.guild.id,
            "mute",
            reason,
            mute_minutes
        )

        await message.channel.send(f'{target.mention} foi mutado por **{mute_minutes} minutos.**')
        return

    warn_id = create_warn(target.id, message.guild.id, message.author.id, reason)
    total_warns = count_warns(target.id, message.guild.id)
    cycle_warns = count_warns_since_last_punishment(target.id, message.guild.id)

    try:
        await target.send(
            f"⚠️ Você recebeu um aviso no servidor **{message.guild.name}**.\n"
            f"Motivo: {reason}\n"
            f"Total de avisos: {total_warns}"
        )
    except discord.Forbidden:
        await message.channel.send("Não foi possível enviar DM para o usuário.")

    await message.channel.send(
        f"{target.mention} recebeu um alerta da moderação ⚠️\n"
        f"Motivo: {reason}\n"
        f"Total de warns: **{total_warns}**"
    )

async def handle_warnings(message):
    if len(message.mentions) == 0:
        await message.channel.send('Use: `.warnings @user`')
        return
    
    target = message.mentions[0]

    total_warns = count_warns(target.id, message.guild.id)

    if total_warns == 0:
        await message.channel.send(f'{target.mention} **não possui** nenhum warn ✅')
        return

    await message.channel.send(f'{target.mention} possui **{total_warns}** warn(s) ⚠️')

async def handleclear_warns(message):
    if not message.author.guild_permissions.manage_guild:
        await message.channel.send('Você não tem permissão para usar esse comando.')
        return
    
    if len(message.mentions) == 0:
        await message.channel.send('Use: `.clearwarns @user`')
        return
    
    target = message.mentions[0]

    deleted_count = clear_warns(target.id, message.guild.id, message.author.id)

    if deleted_count == 0:
        await message.channel.send(f'{target.mention} não tinha warnings para limpar ✅')
        return

    await message.channel.send(f'{target.mention} teve **{deleted_count}** warning(s) revogado(s) por {message.author.mention} 🧹')

async def handle_mute(message, args):
    moderator = message.author
    guild = message.guild

    if not moderator.guild_permissions.moderate_members:
        await message.channel.send("❌ Você não tem permissão para mutar membros.")
        return
    if len(message.mentions) == 0 or len(args < 3):
        await message.channel.send("Use: `.mute <@user> <minutos> <motivo>`")
        return
    target = message.mentions[0]

    try:
        minutes = int(args[2])
    except ValueError:
        await message.channel.send("❌ Duração inválida.")
        return

    if minutes <= 0:
        await message.channel.send("❌ A duração precisa ser maior que 0.")
        return

    reason = " ".join(args[3:] if len(args) > 3 else "Sem motivo informado")

    ensure_user(target.id, target.name)
    ensure_guild(guild.id, guild.name)

    until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=minutes)

    await target.timeout(until, reason=reason)

    punishment_id = create_punishment(
        target.id,
        guild.id,
        "mute",
        reason,
        minutes
    )

    embed = discord.Embed(
        description=f"✅ {target.mention} foi mutado por {minutes} minutos.",
        color=0x00FF00
    )
    embed.add_field(name="Motivo", value=reason, inline=False)
    embed.add_field(name="Case", value=f"#{punishment_id}", inline=True)
    embed.set_author(
        name=moderator.name,
        icon_url=moderator.display_avatar.url
    )

    await message.channel.send(embed=embed)