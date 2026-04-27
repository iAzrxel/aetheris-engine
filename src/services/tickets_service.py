from database.session import get_connection

def create_ticket(user_id: int, guild_id: int, channel_id: int, reason: str | None = None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        insert into tickets (user_id, guild_id, channel_id, reason)
        values (%s, %s, %s, %s)
        """, (user_id, guild_id, channel_id, reason)
    )

    conn.commit()
    ticket_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return ticket_id

def get_open_ticket_by_user(user_id: int, guild_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        select id, channel_id, reason, created_at
        from tickets
        where user_id = %s
        and guild_id = %s
        and status = "open"
        limit 1
        """, (user_id, guild_id)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result