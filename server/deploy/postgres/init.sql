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
