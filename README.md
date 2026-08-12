# annoncio

Osobni archiv inzeratu z annonce.cz. Stahuje inzeraty (text, atributy, fotky,
telefon) podle zadanych URL a uklada je do `stazene_inzeraty/<ad_id>/`, s
prehledovym `index.csv`. Lokalni webove rozhrani (Flask) pro prohlizeni,
filtrovani a hromadne stahovani.

## Soubory

- `download_ads.py` - stahovani/parsovani/ukladani inzeratu (CLI i sdilena logika pro web appku)
- `app.py` - lokalni web (Flask, `127.0.0.1:5000`) - formular, tabulka, detail s galerii
- `spustit.ps1` / `spustit.bat` - jednoklikove spusteni (doinstaluje zavislosti, spusti server na pozadi, otevre prohlizec)
- `stazene_inzeraty/` - archiv (sledovano v gitu, ne gitignorovano)
- `WORKLOG.md` - denik prace vcetne detailu vyresenych bugu
- `CHANGELOG.md` - prehled zmen v kodu

## Nastaveni na dalsim stroji

1. `git clone https://github.com/radekscholz43-netizen/annoncio.git`
2. Nastavit lokalni git identitu (jen pro tenhle repo):
   ```
   git config user.name "Radek"
   git config user.email "radek.scholz43@gmail.com"
   ```
3. **Overit, ze `python --version` resi na skutecnou instalaci, ne na prazdny
   Microsoft Store stub** (hlaska "Python nebyl nalezen; spustte Microsoft
   Store..."). Pokud ano, zkontrolovat poradi v uzivatelskem PATH
   (`[Environment]::GetEnvironmentVariable("Path","User")` v PowerShellu) -
   slozka se skutecnym Pythonem musi byt pred
   `AppData\Local\Microsoft\WindowsApps`. Narazeno a opraveno na Acer 16,
   2026-08-12 - viz WORKLOG.md.
4. Spustit `spustit.ps1` (nebo dvojklik na `spustit.bat`) - doinstaluje
   `flask`, `requests`, `beautifulsoup4`, spusti server a otevre prohlizec.
5. **Pokud stahovani inzeratu selhava s nesourodymi chybami** (`WinError 2`,
   pak `Errno 9` pro stejne URL): zkontrolovat Windows Security > Ochrana
   pred ransomwarem > Rizeny pristup ke slozkam - `pythonw.exe`/`python.exe`
   tam musi byt mezi povolenymi aplikacemi, jinak blokuje zapis do
   `stazene_inzeraty\`. Uz jednou reseno, viz WORKLOG.md (2026-08-01).

## Stav po strojich

- **Acer 16** - hotovo a overeno zive (2026-08-12): git napojen, PATH opraven, appka bezi.
- **HP stribrny** (puvodni stroj) - predpoklad, ze funguje (tady se delal puvodni vyvoj/debugging 2026-08-01), neni ale zive overeno po zalozeni tohoto checklistu.
- **Acer 32** - zatim vubec nenastaveno.
