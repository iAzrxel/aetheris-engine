from database.session import get_connection

def ensure_user(user_id: int, username: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users (id, username)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE username = VALUES(username)
        """,
        (user_id, username)
    )

    conn.commit()
    cursor.close()
    conn.close()


def ensure_guild(guild_id: int, name: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO guilds (id, name)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE name = VALUES(name)
        """,
        (guild_id, name)
    )

    conn.commit()
    cursor.close()
    conn.close()


def create_warn(user_id: int, guild_id: int, reason: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO warns (user_id, guild_id, reason)
        VALUES (%s, %s, %s)
        """,
        (user_id, guild_id, reason)
    )

    conn.commit()
    warn_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return warn_id


def count_warns(user_id: int, guild_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM warns
        WHERE user_id = %s AND guild_id = %s
        """,
        (user_id, guild_id)
    )

    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total