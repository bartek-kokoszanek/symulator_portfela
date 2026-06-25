# Portfel GPW — Analizator 3Y / 8Y

Interaktywny dashboard portfela inwestycyjnego (GPW + NASDAQ/NYSE) z modelem
DCA, scenariuszami rynkowymi i automatyczną aktualizacją cen po sesji GPW.

## Struktura repo

```
.
├── index.html                      <- aplikacja (otwórz w przeglądarce / Pages)
├── data/
│   ├── prices.json                 <- ceny zamknięcia (nadpisywane automatycznie)
│   └── positions-template.csv      <- szablon importu ilości akcji/obligacji
├── scripts/
│   └── fetch_prices.py             <- pobiera ceny ze stooq.pl
└── .github/workflows/
    └── update-prices.yml           <- GitHub Action: codziennie po sesji GPW
```

## Jak to działa

1. **`scripts/fetch_prices.py`** pobiera ostatnie ceny zamknięcia ze stooq.pl
   dla wszystkich tickerów z portfela (GPW + US) i zapisuje je do
   `data/prices.json`.
2. **`.github/workflows/update-prices.yml`** uruchamia ten skrypt automatycznie
   każdego dnia roboczego o 17:40 czasu Warszawy (czyli ~40 minut po zamknięciu sesji
   GPW) i commituje zaktualizowany plik z powrotem do repo.
3. **`index.html`** przy każdym otwarciu wczytuje `data/prices.json` przez
   `fetch()` i nadpisuje ceny aktualne (`currentPrice`) w pozycjach portfela.

**Ważne ograniczenie:** strona HTML sama nie może bezpiecznie pobierać cen
bezpośrednio z internetu codziennie bez Twojej interakcji (przeglądarki
blokują automatyczne żądania w tle, a wiele giełdowych API blokuje CORS).
Dlatego aktualizacja odbywa się "po stronie repozytorium" przez GitHub Action,
a strona tylko czyta już gotowy plik JSON. To rozwiązanie działa identycznie
jak prawdziwa usługa danych rynkowych — różnica jest niewidoczna dla Ciebie.

## Wdrożenie (GitHub Pages)

1. Stwórz nowe repozytorium na GitHubie, np. `gpw-portfolio`.
2. Wgraj zawartość tego folderu (`git push`).
3. W ustawieniach repo: **Settings → Pages → Branch: main → folder: / (root)**.
4. Po chwili strona będzie dostępna pod `https://TWÓJ_LOGIN.github.io/gpw-portfolio/`.
5. W zakładce **Actions** uruchom workflow `Aktualizacja cen portfela` ręcznie
   pierwszy raz (przycisk "Run workflow"), żeby wypełnić `prices.json`
   prawdziwymi danymi od razu, bez czekania do następnej sesji.

## Import ilości akcji z CSV

W aplikacji kliknij **„Import CSV"** i wskaż plik w formacie:

```csv
ticker,class,quantity,avgPrice,yieldPct
XTB,Akcje GPW,230,44.30,
KRUK,Akcje GPW,26,400.00,
BST 2027,Catalyst,155,100.00,8.5
```

- `ticker` — musi odpowiadać tickerowi w aplikacji (wielkość liter ma znaczenie).
- `class` — jedna z: `Akcje GPW`, `Akcje US`, `Catalyst`, `Skarbowe`, `Gotówka`.
- `quantity` — liczba akcji / jednostek obligacji / kwota w PLN (dla gotówki).
- `avgPrice` — średnia cena zakupu (opcjonalnie).
- `yieldPct` — rentowność roczna, tylko dla obligacji/gotówki (opcjonalnie).

Plik startowy: `data/positions-template.csv` — **wartości ilości i cen zakupu
w nim są przykładowe** (wyliczone z poprzednich szacunków wartości). Podmień
je na swoje rzeczywiste dane z domu maklerskiego przed importem.

## Dodawanie nowych tickerów do automatycznego pobierania cen

Edytuj `TICKER_MAP` w `scripts/fetch_prices.py` — dodaj nowy wpis
`"TICKER_W_APCE": "symbol_w_stooq"`. Dla GPW symbol to zwykle mały skrót
spółki (np. `kru` dla KRUK), dla USA dodaj `.us` (np. `aapl.us`).

## Znane ograniczenia

- Stooq.pl czasem blokuje zapytania z niektórych chmurowych adresów IP
  (HTTP 403). GitHub Actions zwykle działa bez problemu, ale jeśli pojawią
  się błędy, rozważ alternatywne API (np. Yahoo Finance przez `yfinance`).
- Reguła "po sesji GPW" w `index.html` sprawdza tylko godzinę 17:00+ czasu
  Warszawy — nie odróżnia dni wolnych od pracy czy świąt giełdowych.
- Ceny obligacji (Catalyst/Skarbowe) nie są automatycznie pobierane —
  domyślnie ustawione na wartość nominalną (par). Aktualizuj ręcznie w UI.
