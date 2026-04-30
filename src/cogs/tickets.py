import discord
import asyncio

from services.tickets_service import create_ticket, get_open_ticket_by_user, close_ticket_db
from services.moderation_service import ensure_guild, ensure_user

async def ensure_support_role(message):
    role = discord.utils.get(message.guild.roles, name="Staff")

    if role is None:
        role = await message.guild.create_role(
            name="Staff",
            reason="Cargo criado automaticamente para o sistema de tickets"
        )

    return role

async def handle_create_ticket(message):
    user = message.author
    guild = message.guild

    ensure_user(user.id, user.name)
    ensure_guild(message.guild.id, message.guild.name)

    existing_ticket = get_open_ticket_by_user(user.id, guild.id)

    if existing_ticket:
        ticket_id, channel_id, reason, created_at, = existing_ticket
        ticket_channel = guild.get_channel(channel_id)

        if ticket_channel is None:
            close_ticket_db(ticket_id)
        else:
            embed = discord.Embed(
                description=f'❌ Você já possui um ticket aberto: <#{channel_id}>',
                color=0xFF0000
            )
            embed.set_author(
                name=user.name,
                icon_url=user.display_avatar.url
            )

            temp_message = await message.channel.send(embed=embed)
            await asyncio.sleep(3)
            await temp_message.delete()
            await message.delete()

            return
        
    staff_role = await ensure_support_role(guild)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True
        ),
        staff_role: discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True,
            manage_channels=True
        ),
        guild.me: discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True,
            manage_channels=True
        )
    }

    channel = await guild.create_text_channel(
        name=f'ticket-{user.name}',
        overwrites=overwrites,
        reason=f'Ticket criado por {user.name}'
    )

    ticket_id = create_ticket(user.id, guild.id, channel.id)

    embed = discord.Embed(
        description=f'✅ Ticket criado com sucesso: {channel.mention}',
        color=0x00FF00
    )
    embed.set_author(
        name=user.name,
        icon_url=user.display_avatar.url
    )

    temp_message = await message.channel.send(embed=embed)

    ticket_embed = discord.Embed(
        title=f'Ticket #{ticket_id}',
        description=f'{user.mention}, explique seu problema aqui.',
        color=0x6A0DAD
    )
    ticket_embed.set_author(
        name=user.name,
        icon_url=user.display_avatar.url
    )
    await channel.send(embed=ticket_embed, view=TicketView(ticket_id))

    await asyncio.sleep(3)
    await temp_message.delete()
    await message.delete()

class TicketView(discord.ui.View):
    def __init__(self, ticket_id: int):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id

    @discord.ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.danger,
        custom_id="close_ticket_button"
    )
    async def close_ticket_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        staff_role= discord.utils.get(interaction.guild.roles, name = "Staff")
        is_owner = interaction.user.id == interaction.guild.owner_id
        is_staff = staff_role in interaction.user.roles if staff_role else False

        if not is_owner and not is_staff:
            await interaction.respnse.send_message(
                "❌ Apenas membros da staff podem fechar esse ticket.",
                ephemeral = True
            )
        close_ticket_db(self.ticket_id)

        await interaction.response.send_message(
            "Ticket encerrado. Este canal será deletado em até 5 segundos,",
            ephemeral=True
        )

        await interaction.channel.delete(reason=f"Ticket fechado por {interaction.user.name}")