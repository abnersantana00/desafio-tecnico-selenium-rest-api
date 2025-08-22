CREATE TABLE dom_publicacao (
    id           BIGSERIAL PRIMARY KEY,
    url_publica  TEXT NOT NULL,          -- link do 0x0.st
    url_local    TEXT NOT NULL,          -- caminho local ex.: data/2025-07/DOM_7123.pdf
    competencia  VARCHAR(7) NOT NULL,    -- formato 'MM/AA', ex.: '07/25'
    is_extra     BOOLEAN NOT NULL DEFAULT FALSE
);

