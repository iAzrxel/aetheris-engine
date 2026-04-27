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

def create_fine(user_id: int, guild_id: int, amount: int, reason: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        insert into economy_fines
        (user_id, guild_id, amount, reason, expires_at)
        values (%s, %s, %s, %s, NULL)
        """, (user_id, guild_id, amount, reason)
    )

    conn.commit()
    cursor.close()
    conn.close()

def get_active_fines(user_id: int, guild_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        select id, amount, reason, status, created_at, expires_at
        from economy_fines
        where user_id = %s
        and guild_id = %s
        and (
            status = 'unpaid'
            or (expires_at is not null and expires_at > now())
            )
        order by created_at desc
        """, (user_id, guild_id)
    )

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return results

def get_unpaid_fines_total(user_id: int, guild_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        select coalesce(sum(amount), 0)
        from economy_fines
        where user_id = %s
        and guild_id = %s
        and status = 'unpaid'
        """,
        (user_id, guild_id)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result[0]

def pay_fines(user_id: int, guild_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            select coalesce(sum(amount), 0)
            from economy_fines
            where user_id = %s
            and guild_id = %s
            and status = 'unpaid'
            """,
            (user_id, guild_id)
        )

        total = cursor.fetchone()[0]

        if total <= 0:
            return False

        cursor.execute(
            """
            update economy
            set balance = balance - %s
            where user_id = %s
            and guild_id = %s
            and balance >= %s
            """,
            (total, user_id, guild_id, total)
        )

        if cursor.rowcount == 0:
            conn.rollback()
            return False

        cursor.execute(
            """
            update economy_fines
            set status = 'paid',
                paid_at = now(),
                expires_at = date_add(now(), interval 24 hour)
            where user_id = %s
            and guild_id = %s
            and status = 'unpaid'
            """,
            (user_id, guild_id)
        )

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()