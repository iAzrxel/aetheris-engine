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


def create_warn(user_id: int, guild_id: int, moderator_id: int, reason: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO warns (user_id, guild_id, moderator_id, reason)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, guild_id, moderator_id, reason)
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
        WHERE user_id = %s AND guild_id = %s AND revoked_at IS NULL
        """,
        (user_id, guild_id)
    )

    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total

def count_warns_since_last_punishment(user_id: int, guild_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM warns
        WHERE user_id = %s
        AND guild_id = %s
        AND created_at > COALESCE(
            (
                SELECT MAX(created_at)
                FROM punishments
                WHERE user_id = %s
                AND guild_id = %s
            ),
            '1970-01-01'
        )
        """,
        (user_id, guild_id, user_id, guild_id)
    )

    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total

def count_mutes(user_id: int, guild_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM punishments
        WHERE user_id = %s
        AND guild_id = %s
        AND type = 'mute'
        """,
        (user_id, guild_id)
    )

    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total

def create_punishment(user_id: int, guild_id: int, punishment_type: str, reason: str, duration_minutes=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO punishments (user_id, guild_id, type, duration_minutes, reason)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, guild_id, punishment_type, duration_minutes, reason)
    )

    conn.commit()

    cursor.close()
    conn.close()

def clear_warns(user_id: int, guild_id: int, moderator_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE warns
        SET revoked_at = NOW(),
            revoked_by = %s
        WHERE user_id = %s
        AND guild_id = %s
        AND revoked_at IS NULL
        """,
        (moderator_id, user_id, guild_id)
    )

    conn.commit()
    affected = cursor.rowcount

    cursor.close()
    conn.close()

    return affected