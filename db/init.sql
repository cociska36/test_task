-- Создаем базу данных, если она отсутствует
DO $$ BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_database
      WHERE datname = 'telegram_bot_db'
   ) THEN
      CREATE DATABASE telegram_bot_db;
   END IF;
END $$;

-- Подключаемся к базе данных
\connect telegram_bot_db;

-- Создаем таблицы
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL
);
