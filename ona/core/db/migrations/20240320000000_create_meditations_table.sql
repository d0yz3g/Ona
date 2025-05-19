-- Создание таблицы медитаций
CREATE TABLE IF NOT EXISTS meditations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    text TEXT NOT NULL,
    audio_filename VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Индексы
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Создание индексов
CREATE INDEX IF NOT EXISTS idx_meditations_user_id ON meditations(user_id);
CREATE INDEX IF NOT EXISTS idx_meditations_type ON meditations(type);
CREATE INDEX IF NOT EXISTS idx_meditations_created_at ON meditations(created_at);

-- Настройка RLS
ALTER TABLE meditations ENABLE ROW LEVEL SECURITY;

-- Политики доступа
CREATE POLICY "Users can view their own meditations"
    ON meditations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own meditations"
    ON meditations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Комментарии
COMMENT ON TABLE meditations IS 'Таблица для хранения медитаций пользователей';
COMMENT ON COLUMN meditations.id IS 'Уникальный идентификатор медитации';
COMMENT ON COLUMN meditations.user_id IS 'ID пользователя';
COMMENT ON COLUMN meditations.type IS 'Тип медитации (mindfulness/stress/sleep/energy)';
COMMENT ON COLUMN meditations.text IS 'Текст медитации';
COMMENT ON COLUMN meditations.audio_filename IS 'Имя аудиофайла';
COMMENT ON COLUMN meditations.created_at IS 'Дата и время создания медитации'; 