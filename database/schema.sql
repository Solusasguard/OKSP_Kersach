CREATE SCHEMA IF NOT EXISTS oleg_gusev;

CREATE TABLE oleg_gusev.books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL
);

CREATE TABLE oleg_gusev.copies (
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES oleg_gusev.books(id),
    status VARCHAR(50) DEFAULT 'свободен' -- варианты: свободен, выдан
);

CREATE TABLE oleg_gusev.readers (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL
);

CREATE TABLE oleg_gusev.checkouts (
    id SERIAL PRIMARY KEY,
    copy_id INTEGER REFERENCES oleg_gusev.copies(id),
    reader_id INTEGER REFERENCES oleg_gusev.readers(id),
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL, -- дата ожидаемого возврата
    return_date DATE        -- фактическая дата возврата (NULL, если на руках)
);