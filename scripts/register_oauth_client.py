#!/usr/bin/env python3
"""Registra un cliente OAuth 2.0 en la base de datos de LifeSync.

Uso:
    python scripts/register_oauth_client.py --client-id mi-app --name "Mi App" \\
        --redirect-uri https://app.example/callback --scope "read write"

El secreto (solo para clientes confidenciales) se imprime una única vez.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))

from app.core.database import database  # noqa: E402
from app.services.client_service import ClientService  # noqa: E402


async def _register(args: argparse.Namespace) -> int:
    database.init()
    await database.create_all()
    async with database.session_factory() as session:
        service = ClientService(session)
        try:
            client, secret = await service.register_client(
                client_id=args.client_id,
                client_name=args.name,
                redirect_uris=args.redirect_uri,
                allowed_scopes=args.scope,
                is_public=not args.confidential,
            )
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        await session.commit()

    print(f"Cliente registrado: {client.client_id}")
    print(f"Tipo: {'confidencial' if args.confidential else 'público'}")
    print(f"Scopes permitidos: {client.allowed_scopes}")
    print(f"Redirect URIs: {', '.join(client.redirect_uri_list)}")
    if secret:
        print(f"client_secret (se muestra una sola vez): {secret}")
    await database.dispose()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--redirect-uri", action="append", default=[])
    parser.add_argument("--scope", default="read write")
    parser.add_argument(
        "--confidential",
        action="store_true",
        help="Genera un client_secret (servidores, no apps nativas)",
    )
    args = parser.parse_args()
    if not args.redirect_uri:
        args.redirect_uri = ["com.lifesync.mobile://oauth2callback"]
    return asyncio.run(_register(args))


if __name__ == "__main__":
    raise SystemExit(main())
