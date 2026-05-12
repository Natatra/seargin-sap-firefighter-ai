"""Szybki test: odczyt GEMINI_API_KEY z .env i czy Google REST go akceptuje (lista modeli)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from reviewer import _DOTENV_PATH, _parse_gemini_api_key_from_dotenv_file


def main() -> None:
    load_dotenv(dotenv_path=_DOTENV_PATH, override=True)
    key = _parse_gemini_api_key_from_dotenv_file(_DOTENV_PATH) or (
        os.getenv("GEMINI_API_KEY") or ""
    ).strip()

    print(f"Plik: {_DOTENV_PATH} (istnieje: {_DOTENV_PATH.is_file()})")
    if not key:
        print("BRAK wartosci GEMINI_API_KEY — dodaj jedna linie: GEMINI_API_KEY=TwojKlucz")
        return

    print(f"Dlugosc klucza: {len(key)} znakow")
    ok_prefix = key.startswith("AIza")
    print(f"Prefiks AIza (typowy dla AI Studio): {'tak' if ok_prefix else 'NIE — moze to nie jest klucz z AI Studio'}")

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()
        names = [m.get("name", "") for m in data.get("models", []) if "generateContent" in m.get("supportedGenerationMethods", [])]
        print("OK: Google przyjal klucz (REST models dziala).")
        print("Przykladowe modele:", *names[:8], sep="\n  ")
    except Exception as exc:
        print("BLAD — Google odrzuca klucz lub problem sieci:", exc)


if __name__ == "__main__":
    main()
