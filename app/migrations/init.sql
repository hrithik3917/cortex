-- -- migrations/init.sql
-- -- Run this to create the schema from scratch on a fresh database

-- CREATE TABLE IF NOT EXISTS users (
--     id          SERIAL PRIMARY KEY,
--     email       VARCHAR(255) UNIQUE NOT NULL,
--     hashed_password VARCHAR(255) NOT NULL,
--     is_active   BOOLEAN DEFAULT TRUE NOT NULL,
--     created_at  TIMESTAMPTZ DEFAULT NOW() NOT NULL
-- );

-- CREATE TABLE IF NOT EXISTS books (
--     id          SERIAL PRIMARY KEY,
--     title       VARCHAR(255) NOT NULL,
--     author      VARCHAR(255) NOT NULL,
--     pages       INTEGER NOT NULL,
--     owner_id    INTEGER REFERENCES users(id) ON DELETE CASCADE
-- );

-- -- Indexes for columns you query frequently
-- -- (no separate index on users.email: the UNIQUE constraint above already creates one)
-- CREATE INDEX IF NOT EXISTS idx_books_owner ON books(owner_id);

