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

    warn_id = create_warn(target.id, message.guild.id, reason)
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

    deleted_count = clear_warns(target.id, message.guild.id)

    if deleted_count == 0:
        await message.channel.send(f'{target.mention} não tinha warnings para limpar ✅')
        return

    await message.channel.send(f'Foram removidos **{deleted_count}** warning(s) de {target.mention} ✅')