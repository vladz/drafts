import asyncpg


async def init_db(dsn: str) -> 'asyncpg.pool.Pool':
    return await asyncpg.create_pool(dsn)


async def get_user_id(username: str, db_pool: 'asyncpg.pool.Pool'):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow('''
            SELECT telegram_id 
            FROM u123
            WHERE username = $1
            ''', username)


async def set_user_id(user_id, username: str, db_pool: 'asyncpg.pool.Pool'):
    async with db_pool.acquire() as conn:
        return await conn.execute('''
            UPDATE u123
            SET telegram_id = $1
            WHERE username = $2
            ''', user_id, username)
