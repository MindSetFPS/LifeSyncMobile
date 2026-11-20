#!/usr/bin/env python3
"""Genera el par de llaves RSA (4096 bits) usado para firmar los JWT (RS256).

Uso: python scripts/generate_keys.py [directorio_de_salida]
"""

from __future__ import annotations

import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def main() -> None:
    output_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "keys")
    output_dir.mkdir(parents=True, exist_ok=True)
    private_path = output_dir / "private_key.pem"
    public_path = output_dir / "public_key.pem"

    if private_path.exists() and public_path.exists():
        print(f"Las llaves ya existen en {output_dir}. No se sobrescriben.")
        return

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    private_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    public_path.write_bytes(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    private_path.chmod(0o600)
    print(f"Llaves generadas en {output_dir} (privada con permisos 600).")


if __name__ == "__main__":
    main()
