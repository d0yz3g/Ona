-- Создание таблиц

-- users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP,
    current_state TEXT DEFAULT 'new'
);

-- profiles
CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    birth_date DATE,
    birth_time TIME,
    birth_place TEXT,
    age INTEGER,
    profile_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- conversations
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    message_text TEXT,
    is_user BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- subscriptions
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    plan_type TEXT,
    status TEXT,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    payment_id TEXT
);

-- meditations
CREATE TABLE meditations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title TEXT,
    text_content TEXT,
    audio_url TEXT,
    duration INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для оптимизации запросов
CREATE INDEX idx_user_telegram_id ON users(telegram_id);
CREATE INDEX idx_profile_user_id ON profiles(user_id);
CREATE INDEX idx_conversation_user_id ON conversations(user_id);
CREATE INDEX idx_conversation_created_at ON conversations(created_at);

-- Настройка Row Level Security (RLS)
-- Сначала создадим функцию для получения ID текущего пользователя
CREATE OR REPLACE FUNCTION current_user_id() RETURNS BIGINT 
LANGUAGE SQL SECURITY DEFINER
AS $$
  SELECT NULLIF(current_setting('request.jwt.claims', TRUE)::jsonb->>'user_id', '')::BIGINT;
$$;

-- Включение RLS для таблиц
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE meditations ENABLE ROW LEVEL SECURITY;

-- Создание политик доступа
CREATE POLICY user_access ON users
    FOR ALL
    USING (telegram_id = current_user_id());

CREATE POLICY profile_access ON profiles
    FOR ALL
    USING (user_id IN (SELECT id FROM users WHERE telegram_id = current_user_id()));

CREATE POLICY conversation_access ON conversations
    FOR ALL
    USING (user_id IN (SELECT id FROM users WHERE telegram_id = current_user_id()));

CREATE POLICY subscription_access ON subscriptions
    FOR ALL
    USING (user_id IN (SELECT id FROM users WHERE telegram_id = current_user_id()));

CREATE POLICY meditation_access ON meditations
    FOR ALL
    USING (user_id IN (SELECT id FROM users WHERE telegram_id = current_user_id())); 