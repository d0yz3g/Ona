-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица профилей пользователей
CREATE TABLE IF NOT EXISTS profiles (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(telegram_id),
    -- Натальные данные
    birth_date TEXT,
    birth_time TEXT,
    birth_place TEXT,
    age INTEGER,
    -- Метаданные
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Таблица истории диалогов
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(telegram_id),
    message_text TEXT NOT NULL,
    is_user BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создаем индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);

-- Установка политик RLS для таблицы пользователей
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY users_policy ON users 
    USING (TRUE)  -- Все могут просматривать
    WITH CHECK (FALSE);  -- Никто не может изменять

-- Установка политик RLS для таблицы профилей
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY profiles_policy ON profiles 
    USING (TRUE)  -- Все могут просматривать
    WITH CHECK (FALSE);  -- Никто не может изменять

-- Установка политик RLS для таблицы истории диалогов
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
CREATE POLICY conversations_policy ON conversations 
    USING (TRUE)  -- Все могут просматривать
    WITH CHECK (FALSE);  -- Никто не может изменять 