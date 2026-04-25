import discord
from services.moderation_service import (
    ensure_user,
    ensure_guild,
    create_warn,
    count_warns
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

    warn_id = create_warn(target.id, message.guild.id, reason)
    total_warns = count_warns(target.id, message.guild.id)

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