#!/usr/bin/env python3
"""
Pobiera aktualne ceny zamknięcia dla tickerów z portfela (GPW + US) ze stooq.pl
i zapisuje je do data/prices.json.

Działa jako część GitHub Actions workflow (.github/workflows/update-prices.yml),
uruchamiany automatycznie codziennie po zamknięciu sesji GPW (~17:35 CET/CEST).

Uruchomienie lokalne:
    python3 scripts/fetch_prices.py
"""
import csv
import io
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Mapowanie: ticker w portfelu -> symbol w stooq.pl
# Dla GPW symbol jest zwykle samym tickerem (małe litery).
# Dla rynku US dodajemy sufiks ".us".
TICKER_MAP = {
    # --- GPW ---
    "XTB": "xtb",
    "KRUK": "kru",
    "SYNEKTIK": "syn",
    "MOBRUK": "mbr",
    "VERCOM": "vrc",
    "CBF": "cbf",
    "RAINBOW": "rbw",
    "DEVELIA": "dvl",
    "DOMDEV": "dom",
    "UNIMOT": "unt",
    "GPW": "gpw",
    "ATREM": "atr",
    "ELEKTROTIM": "elt",
    "DINOPL": "dnp",
    "PZU": "pzu",
    # --- US (NASDAQ/NYSE) ---
    "NVO": "nvo.us",
    "MSFT": "msft.us",
    "AMZN": "amzn.us",
    "NVDA": "nvda.us",
    "AMD": "amd.us",
    "ADSK": "adsk.us",
    "PYPL": "pypl.us",
    "IREN": "iren.us",
    "CRWV": "crwv.us",
    "APLD": "apld.us",
}

STOOQ_URL = "https://stooq.pl/q/l/?s={symbol}&f=sd2t2ohlcv&h&e=csv"


def fetch_one(symbol: str) -> dict | None:
    """Pobiera jedną linię CSV ze stooq.pl dla danego symbolu."""
    url = STOOQ_URL.format(symbol=symbol)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
    except Exception as e:
        print(f"  [BŁĄD] {symbol}: {e}", file=sys.stderr)
        return None

    reader = csv.DictReader(io.StringIO(raw))
    row = next(reader, None)
    if not row or row.get("Close") in (None, "", "N/D"):
        print(f"  [BRAK DANYCH] {symbol}: {raw.strip()[:80]}", file=sys.stderr)
        return None

    try:
        return {
            "date": row.get("Date"),
            "close": float(row["Close"]),
        }
    except (ValueError, KeyError) as e:
        print(f"  [PARSE BŁĄD] {symbol}: {e}", file=sys.stderr)
        return None


def main() -> int:
    out_path = Path(__file__).resolve().parent.parent / "data" / "prices.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results: dict[str, dict] = {}
    failed: list[str] = []

    print(f"Pobieram ceny dla {len(TICKER_MAP)} tickerów ze stooq.pl...")
    for ticker, symbol in TICKER_MAP.items():
        data = fetch_one(symbol)
        if data:
            results[ticker] = data
            print(f"  OK  {ticker:12s} ({symbol:10s}) -> {data['close']}")
        else:
            failed.append(ticker)

    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source": "stooq.pl",
        "prices": results,
        "failed": failed,
    }

    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nZapisano {len(results)} cen do {out_path}")
    if failed:
        print(f"Nie udało się pobrać: {', '.join(failed)}", file=sys.stderr)

    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
