#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Uploader 0x0.st para PDFs em data/AA-MM/
----------------------------------------
- Envia todos os .pdf encontrados em data/AA-MM/** para https://0x0.st
- Armazena as URLs públicas em CSV: data/AA-MM/uploads_0x0.csv
- Imprime um resumo ao final.

Uso:
  python upload_0x0.py                 # varre data/, envia PDFs
  python upload_0x0.py --root data     # raiz alternativa (padrão: data)
  python upload_0x0.py --force         # ignora CSV e reenvia tudo
  python upload_0x0.py --secret        # solicita URL "difícil de adivinhar"
  python upload_0x0.py --expires 24    # define retenção máx. (horas)

Requisitos: requests (pip install requests)
"""

from __future__ import annotations
import argparse
import csv
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

UPLOAD_URL = "https://0x0.st"
USER_AGENT = "user-uploader/1.0 (+https://0x0.st)"
MAX_SIZE_BYTES = 512 * 1024 * 1024  # 512 MiB segundo o manual

@dataclass(frozen=True)
class UploadResult:
    file_path: Path
    url: str
    x_token: Optional[str]
    size: int
    timestamp_iso: str

def listar_pdfs(root: Path) -> Iterator[Path]:
    """Varre recursivamente por .pdf (case-insensitive)."""
    pattern = "**/*.pdf"
    yield from (p for p in root.glob(pattern) if p.is_file())

def obter_pasta_mês(file_path: Path, root: Path) -> Path:
    """Retorna a pasta 'data/AA-MM' (primeiro nível abaixo de root) para um arquivo."""
    try:
        rel = file_path.relative_to(root)
    except ValueError:
        # Se não estiver dentro de root, salva CSV na própria pasta do arquivo
        return file_path.parent
    # Primeiro componente do caminho relativo é o diretório AA-MM
    return (root / rel.parts[0]) if rel.parts else file_path.parent

def ler_map_existente(csv_path: Path) -> Dict[str, str]:
    """Lê CSV existente e retorna {arquivo_absoluto: url}."""
    mapping: Dict[str, str] = {}
    if not csv_path.exists():
        return mapping
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "arquivo" in row and "url" in row:
                mapping[row["arquivo"]] = row["url"]
    return mapping

def gravar_csv(csv_path: Path, result: UploadResult) -> None:
    """Acrescenta uma linha ao CSV, criando cabeçalhos se necessário."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    exists = csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["arquivo", "url", "x_token", "bytes", "data_hora"]
        )
        if not exists:
            writer.writeheader()
        writer.writerow({
            "arquivo": str(result.file_path.resolve()),
            "url": result.url,
            "x_token": result.x_token or "",
            "bytes": result.size,
            "data_hora": result.timestamp_iso,
        })

def criar_sessao_http() -> requests.Session:
    """Session com retry/backoff razoáveis e UA próprio (boa prática sugerida no site)."""
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    retries = Retry(
        total=5, connect=5, read=5, backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["POST"])
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s

def enviar_arquivo(
    session: requests.Session,
    file_path: Path,
    *,
    secret: bool = False,
    expires: Optional[int] = None,
) -> UploadResult:
    """Faz POST multipart para 0x0.st com campo 'file' e retorna UploadResult."""
    size = file_path.stat().st_size
    if size > MAX_SIZE_BYTES:
        raise ValueError(f"Arquivo excede 512 MiB: {file_path.name} ({size} bytes)")

    data = {}
    if secret:
        data["secret"] = ""  # somente presença do campo já ativa URL difícil
    if expires is not None:
        data["expires"] = str(expires)  # horas (inteiro)

    with file_path.open("rb") as fp:
        files = {"file": (file_path.name, fp, "application/pdf")}
        resp = session.post(UPLOAD_URL, data=data, files=files, timeout=120)
    resp.raise_for_status()

    url_text = resp.text.strip()
    x_token = resp.headers.get("X-Token")
    ts = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    return UploadResult(
        file_path=file_path, url=url_text, x_token=x_token, size=size, timestamp_iso=ts
    )

def main(argv: Optional[Iterable[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Uploader de PDFs para 0x0.st")
    ap.add_argument("--root", default="data", help="Raiz a varrer (padrão: data)")
    ap.add_argument("--force", action="store_true", help="Reenviar mesmo se já houver URL no CSV")
    ap.add_argument("--secret", action="store_true", help="Gerar URL difícil de adivinhar (secret)")
    ap.add_argument("--expires", type=int, default=None, help="Definir retenção máx. em horas")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"[ERRO] Pasta raiz não encontrada: {root}", file=sys.stderr)
        return 2

    session = make_session()
    sent: list[UploadResult] = []
    skipped: list[Path] = []
    errors: list[tuple[Path, str]] = []

    pdfs = sorted(iter_pdfs(root))
    if not pdfs:
        print(f"Nenhum PDF encontrado em {root}")
        return 0

    print(f"==> Iniciando upload para 0x0.st")
    print(f"Raiz: {root}")
    print(f"Arquivos encontrados: {len(pdfs)}\n")

    for pdf in pdfs:
        try:
            month_dir = month_dir_for(pdf, root)
            csv_path = month_dir / "uploads_0x0.csv"
            mapping = read_existing_map(csv_path)

            already = mapping.get(str(pdf.resolve()))
            if already and not args.force:
                print(f"[pula] {pdf} (já possui URL)")
                skipped.append(pdf)
                continue

            if pdf.stat().st_size > MAX_SIZE_BYTES:
                print(f"[ERRO] {pdf.name}: excede 512 MiB — ignorado")
                errors.append((pdf, "arquivo maior que 512 MiB"))
                continue

            print(f"[envia] {pdf}")
            result = upload_file(session, pdf, secret=args.secret, expires=args.expires)
            append_csv(csv_path, result)
            sent.append(result)

        except requests.HTTPError as e:
            errors.append((pdf, f"HTTP {e.response.status_code}"))
            print(f"[falha] {pdf} -> HTTP {e.response.status_code}", file=sys.stderr)
        except Exception as e:
            errors.append((pdf, str(e)))
            print(f"[falha] {pdf} -> {e}", file=sys.stderr)

    # Resumo final
    print("\n=== RESUMO ===")
    if sent:
        print("Uploads concluídos:")
        for r in sent:
            print(f"- {r.file_path.name} -> {r.url}")
    else:
        print("Nenhum arquivo enviado.")

    if skipped:
        print(f"\nPulados ({len(skipped)}):")
        for p in skipped:
            print(f"- {p.name}")

    if errors:
        print(f"\nFalhas ({len(errors)}):")
        for p, msg in errors:
            print(f"- {p.name}: {msg}")

    print("\nConcluído.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
