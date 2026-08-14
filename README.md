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
- `WORKLOG.md` - denik prace vcetne detailu vyresenych bugu (co se delalo, proc, a s jakym vysledkem - vcetne technickych zmen v kodu)

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

## Mobil (Android, Termux)

Kod nema zadne Windows-specificke zavislosti (`pathlib` vsude, zadne
`win32`/zpetna lomitka) - na Termuxu (viz mercurio/docs/nastaveni-noveho-stroje.md
§4 pro instalaci Termuxu samotneho) by mel bezet beze zmen:

1. `pkg install git nodejs` (git uz je potreba i pro mercurio, nodejs jen pro Claude Code)
2. `pkg install python`
3. `git clone https://github.com/radekscholz43-netizen/annoncio.git`
4. `cd annoncio && git config user.name "Radek" && git config user.email "radek.scholz43@gmail.com"`
5. `bash spustit_mobil.sh` - jednoklikovy ekvivalent `spustit.ps1` pro Termux:
   doinstaluje `flask`/`requests`/`beautifulsoup4`, spusti server na pozadi
   (nohup, prezije zavreni tohoto prikazu) a pokud je nainstalovany
   `termux-api` balicek, rovnou otevre Chrome. Bez `termux-api` jen vypise
   URL k rucnimu otevreni.
6. Otevrit (nebo zkontrolovat, ze se otevrelo) `http://127.0.0.1:5000` v
   mobilnim prohlizeci - bezi primo na telefonu, notebook nemusi byt zapnuty.
   Pro dalsi pouziti stranku v Chrome zalozkovat, at se nemusi pokazde
   spoustet Termux rucne pres prikazovou radku.

**Bezi primo na telefonu, ne v cloudu** - vedomé rozhodnuti (2026-08-14):
appka archivuje osobni udaje (telefonni cisla, fotky) tretich osob z
inzeratu, takze verejne cloudove hostovani by je vystavilo internetu bez
jejich souhlasu. Spusteni v Termuxu na vlastnim telefonu tohle obchazi -
zadna verejna expozice, zadny novy ucet, zadna zavislost na tom, jestli je
zapnuty nejaky notebook.

**Neotestovano na realnem telefonu** (2026-08-12, skript `spustit_mobil.sh`
pridan 2026-08-14 a taky jeste neotestovan zive) - jen odvozeno z toho, ze
kod nema OS-specificke zavislosti. Windows Defender Controlled Folder Access
bug (viz WORKLOG 2026-08-01) je Windows-specificky, na Androidu nerelevantni.

## Stav po strojich

- **Acer 16** - hotovo a overeno zive (2026-08-12): git napojen, PATH opraven, appka bezi.
- **Acer 32** - hotovo a overeno zive (2026-08-12): cisty Python 3.14.7 pres winget, appka bezi. Stahovani novych inzeratu (zapis do `stazene_inzeraty/`) tam jeste netestovano.
- **HP stribrny** (puvodni stroj) - predpoklad, ze funguje (tady se delal puvodni vyvoj/debugging 2026-08-01), neni ale zive overeno po zalozeni tohoto checklistu.
- **Mobil (Android)** - postup napsany, zatim neprovedeno/neotestovano na realnem telefonu.
