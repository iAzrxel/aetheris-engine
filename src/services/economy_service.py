from database.session import get_connection
from datetime import datetime, timedelta

def ensure_account(user_id: int, guild_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        insert into economy (user_id, guild_id) values (%s, %s) on duplicate key update user_id = user_id""",
        (user_id, guild_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

def get_balance(user_id: int, guild_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        select balance, bank from economy where user_id = %s and guild_id = %s""",
        (user_id, guild_id)
    )

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result is None:
        return 0, 0

    return result[0], result[1]

def get_last_work(user_id: int, guild_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        select last_work from economy where user_id = %s and guild_id = %s
        """, (user_id, guild_id)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result[0] if result else None

def update_work(user_id: int, guild_id: int, amount:int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        update economy set balance = balance + %s,
            last_work = now()
        where user_id = %s and guild_id = %s
        """,
        (amount, user_id, guild_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

def deposit_money(user_id: int, guild_id: int, amount: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        update economy set balance = balance - %s,
            bank = bank + %s
            where user_id = %s
            and guild_id = %s
            and balance >= %s
        """,(amount, amount, user_id, guild_id, amount)
    )

    conn.commit()
    affected = cursor.rowcount

    cursor.close()
    conn.close()

    return affected > 0

def withdraw_money(user_id: int, guild_id: int, amount: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        update economy set bank = bank - %s,
        balance = balance + %s
        where user_id = %s
        and guild_id = %s
        and bank >= %s
        """, (amount, amount, user_id, guild_id, amount)
    )

    conn.commit()
    affected = cursor.rowcount

    cursor.close()
    conn.close()

    return affected > 0

def rob_user(user_id: int, target_id: int, guild_id: int, amount: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        update economy
        set balance = balance - %s
        where user_id = %s
        and guild_id = %s
        and balance >= %s
        """, (amount, target_id, guild_id, amount)
    )

    if cursor.rowcount == 0:
        conn.rollback()
        cursor.close()
        conn.close()
        return False
    
    cursor.execute(
        """
        update economy 
        set balance = balance + %s
        where user_id = %s
        and guild_id = %s
        """, (amount, user_id, guild_id)
    )

    conn.commit()
    affected = cursor.rowcount

    cursor.close()
    conn.close()

    return affected > 0