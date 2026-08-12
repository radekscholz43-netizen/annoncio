# Changelog

Zmeny v projektu "Osobni archiv inzeratu (annonce.cz)".
Format vychazi z [Keep a Changelog](https://keepachangelog.com/), datum ve formatu YYYY-MM-DD.

## [Unreleased]

### Pridano
- `download_ads.py`: `request_with_retry()` - stahovani HTML stranky inzeratu i
  jednotlivych fotek nyni zkousi az 3x s kratkou prodlevou pred tim, nez selze,
  aby prechodne sitove/systemove chyby nezpusobily selhani celeho stahovani.

### Zmeneno
- `download_ads.py`: nova sdilena funkce `download_one()` (fetch + parse + save
  + update indexu pro jedno URL), kterou nyni pouziva jak CLI (`main()`), tak
  webova appka (`app.py`'s `/download`) - odstranena duplicita, chovani beze zmeny.

### Opraveno
- `stazene_inzeraty/index.csv` byl mistama nespravne strukturovany (napr. u
  jednoho radku telefon skoncil v jinem sloupci nez mel) a u nekterych radku
  nebyl telefon zapsany, i kdyz ho prislusny `data.json` mel spravne ulozeny.
  `index.csv` byl prestaven ze vsech `data.json` souboru (spolehlivy zdroj
  pravdy). Po oprave chybi telefon jen u 2 ze 114 inzeratu - u obou overeno,
  ze telefon na aktualni strance annonce.cz proste neni uveden.

### Zkoumano / vyresrseno (mimo kod)
- Hlaseni chyby pri stahovani inzeratu (`[WinError 2] ...` a pri opakovanem
  pokusu `[Errno 9] Bad file descriptor` pro stejne URL): potvrzeny root cause
  je Windows Defender **Rizeny pristup ke slozkam (Controlled folder access)**,
  ktery blokuje `pythonw.exe` v zapisu do `Documents\annoncio\stazene_inzeraty\`.
  Neni to chyba v `download_ads.py`/`app.py` - reseni je pridat `pythonw.exe` a
  `python.exe` mezi povolene aplikace v Zabezpeceni Windows > Ochrana pred
  ransomwarem > Rizeny pristup ke slozkam. Podrobnosti viz [WORKLOG.md](WORKLOG.md).

## [0.1.0] - pocatecni stav

### Pridano
- `download_ads.py` - stahovani jednotlivych inzeratu z annonce.cz podle URL zadanych
  uzivatelem, parsovani nazvu, atributu, sluzeb, popisu, telefonu a fotek, ukladani do
  `stazene_inzeraty/<ad_id>/` (`data.json` + `foto_*`) a udrzovani souhrnneho `index.csv`.
- `app.py` - lokalni webove rozhrani (Flask, `127.0.0.1:5000`):
  - formular pro hromadne stahovani URL adres,
  - prehledova tabulka ulozenych inzeratu s razenim podle sloupcu,
  - filtrovani podle textu (nazev/popis) a podle nabizenych sluzeb,
  - detail ulozene kopie inzeratu vcetne galerie fotek s lightboxem,
  - servirovani fotek z lokalniho archivu.
- `spustit.ps1` / `spustit.bat` - jednoklikove spusteni: doinstaluje zavislosti
  (flask, requests, beautifulsoup4), spusti server na pozadi a otevre prohlizec.
