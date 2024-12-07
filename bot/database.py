import asyncpg
import asyncio
import logging
from datetime import datetime
from aiogram import Bot


class Database:
    def __init__(self, host, port, dbname, user, password, bot: Bot):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.bot = bot
        self.pool = None

    async def init(self):
        retries = 5
        for i in range(retries):
            try:
                self.pool = await asyncpg.create_pool(
                    user=self.user,
                    password=self.password,
                    database=self.dbname,
                    host='db',
                    port=self.port,
                )
                await self.create_tables()  # Создание таблиц при инициализации
                await self.update_user_id_column()  # Обновление типа user_id
                break
            except Exception as e:
                logging.error(f"Ошибка подключения к базе данных: {e}")
                if i < retries - 1:
                    await asyncio.sleep(5)  # Подождать 5 секунд перед повторной попыткой
                else:
                    raise Exception("Не удалось подключиться к базе данных после нескольких попыток.")

    
    async def create_tables(self):
        """Создаем таблицы, если их нет в базе данных."""
        try:
            async with self.pool.acquire() as connection:
                # Создание таблицы "orders", если она не существует
                await connection.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
                        order_id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        order_date TIMESTAMP NOT NULL,
                        status VARCHAR(50) NOT NULL
                    );
                ''')
                
                # Создание таблицы "order_items", если она не существует
                await connection.execute('''
                    CREATE TABLE IF NOT EXISTS order_items (
                        item_id SERIAL PRIMARY KEY,
                        order_id INT REFERENCES orders(order_id),
                        product_id INT NOT NULL,
                        quantity INT NOT NULL
                    );
                ''')

                # Создание таблицы "delivery_data", если она не существует
                await connection.execute('''
                    CREATE TABLE IF NOT EXISTS delivery_data (
                        user_id BIGINT PRIMARY KEY,
                        delivery_data TEXT NOT NULL
                    );
                ''')
        except Exception as e:
            logging.error(f"Ошибка при создании таблиц: {e}")

    async def update_user_id_column(self):
        try:
            async with self.pool.acquire() as connection:
                await connection.execute('''
                    ALTER TABLE orders
                    ALTER COLUMN user_id TYPE BIGINT;
                ''')
        except Exception as e:
            logging.error(f"Ошибка при изменении типа поля 'user_id': {e}")


    async def add_user(self, user_id: int):
        try:
            async with self.pool.acquire() as connection:
                await connection.execute('''
                    INSERT INTO users(user_id) 
                    VALUES($1)
                    ON CONFLICT (user_id) DO NOTHING;
                ''', user_id)
                logging.error("добавлен юзер")
        except Exception as e:
            logging.error(f"Ошибка при добавлении пользователя с id {user_id}: {e}")

    async def save_order(self, user_id, cart):
        try:
            order_date = datetime.now()  # Исправлено: передаем datetime объект, а не строку
            
            async with self.pool.acquire() as connection:
                # Вставляем заказ в таблицу заказов
                order_id = await connection.fetchval("""
                    INSERT INTO orders (user_id, order_date, status)
                    VALUES ($1, $2, $3) RETURNING order_id;
                """, user_id, order_date, 'new')
                
                # Вставляем каждый товар из корзины в таблицу order_items
                for item in cart:
                    await connection.execute("""
                        INSERT INTO order_items (order_id, product_id, quantity)
                        VALUES ($1, $2, $3);
                    """, order_id, item['product_id'], item['quantity'])
  
        except Exception as e:
            logging.error(f"Ошибка при сохранении заказа для пользователя {user_id}: {e}")

    async def save_delivery_data(self, user_id, delivery_data):
        try:
            async with self.pool.acquire() as connection:
                # Проверка, существует ли уже запись
                existing_data = await connection.fetchrow("""
                    SELECT * FROM delivery_data WHERE user_id = $1;
                """, user_id)
                if existing_data:
                    # Если запись существует, обновляем ее
                    await connection.execute("""
                        UPDATE delivery_data SET delivery_data = $2 WHERE user_id = $1;
                    """, user_id, delivery_data)
                else:
                    # Если записи нет, вставляем новую
                    await connection.execute("""
                        INSERT INTO delivery_data (user_id, delivery_data)
                        VALUES ($1, $2);
                    """, user_id, delivery_data)
        except Exception as e:
            logging.error(f"Ошибка при сохранении данных доставки для пользователя {user_id}: {e}")