# app/models.py
from sqlalchemy import Column, BigInteger, Text, String, Boolean, text
from .db import Base

class DomPublicacao(Base):
    __tablename__ = "dom_publicacao"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    url_publica = Column(Text, nullable=False)   # link do 0x0.st/001.pdf
    url_local = Column(Text, nullable=False)     # ex.: data/2025-07/DOM_7123.pdf
    competencia = Column(String(7), nullable=False) # VARCHAR(7) NOT NULL no formato 'MM/AA'
    # BOOLEAN NOT NULL DEFAULT FALSE
    is_extra = Column(Boolean, nullable=False, server_default=text("false"))