# app/crud.py
from sqlalchemy import create_engine, text
import os

# --- Conexão e schema ---
DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://meu_user:meu_pass@db:5432/meu_bd"
)
engine = create_engine(DB_URL, future=True)

def init_db() -> None:
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS publicacoes (
                id   SERIAL PRIMARY KEY,
                data DATE NOT NULL,
                link TEXT NOT NULL UNIQUE
            );
        """))

# --- Operações ---
def salvar_bd(lista_links: list[dict]) -> int:
    """Insere [{'data_publicacao','link'}, ...] no PostgreSQL (ignora duplicados por link)."""
    sql = text("""
        INSERT INTO publicacoes (data, link)
        VALUES (:data, :link)
        ON CONFLICT (link) DO NOTHING
    """)
    with engine.begin() as conn:
        for item in lista_links:
            conn.execute(sql, {"data": item["data_publicacao"], "link": item["link"]})
    return len(lista_links)

def listar_todas() -> list[dict]:
    with engine.begin() as conn:
        rows = conn.execute(text(
            "SELECT id, data, link FROM publicacoes ORDER BY id DESC"
        )).all()
    return [dict(r._mapping) for r in rows]

def listar_por_ano_mes(ano: int, mes: int) -> list[dict]:
    sql = text("""
        SELECT id, data, link
        FROM publicacoes
        WHERE EXTRACT(YEAR  FROM data) = :ano
          AND EXTRACT(MONTH FROM data) = :mes
        ORDER BY data, id
    """)
    with engine.begin() as conn:
        return [dict(r) for r in conn.execute(sql, {"ano": ano, "mes": mes}).mappings().all()]
    

def delete_all_rows():
    with engine.begin() as conn:
        result = conn.execute(text("DELETE FROM publicacoes RETURNING link"))
        deletados = [r[0] for r in result.fetchall()]
    return {"apagados": len(deletados), "links": deletados}