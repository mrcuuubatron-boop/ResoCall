CREATE TABLE IF NOT EXISTS users (
    login TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);

INSERT INTO users (login, password, role) VALUES
    ('admin', 'admin', 'admin'),
    ('engineer', 'engineer', 'engineer'),
    ('user', 'user', 'user')
ON CONFLICT (login) DO NOTHING;

-- uploads metadata table
CREATE TABLE IF NOT EXISTS uploads (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    area TEXT NOT NULL,
    size BIGINT NOT NULL,
    uploader TEXT,
    uploaded_at TIMESTAMPTZ DEFAULT now(),
    deleted_at TIMESTAMPTZ,
    deleted_by TEXT
);

ALTER TABLE uploads ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE uploads ADD COLUMN IF NOT EXISTS deleted_by TEXT;
