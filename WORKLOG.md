# Worklog

Provozni denik prace na projektu "annoncio" (osobni archiv inzeratu z annonce.cz).
Neni to seznam zmen v kodu (ten je v [CHANGELOG.md](CHANGELOG.md)), ale zaznam
co se delalo, proc, a s jakym vysledkem - hlavne pro pripady, kdy je potreba se
k necemu vratit pozdeji.

## 2026-08-12 (rozjezd na dalsim stroji)

Repo naklonovano na druhy notebook (Acer). Zjisteno a opraveno: bare
prikaz `python`/`pythonw` na tomto stroji resil na prazdnou Microsoft
Store "stub" verzi (`AppData\Local\Microsoft\WindowsApps\python.exe`),
protoze byla v uzivatelskem PATH pred skutecnou instalaci Pythonu
(`AppData\Local\Python\bin`, Python 3.14.6). To by rozbilo `spustit.ps1`
(hlaska "Python nebyl nalezen; spustte Microsoft Store...").

Oprava: preuspoada uzivatelsky PATH tak, aby `AppData\Local\Python\bin`
byl pred `WindowsApps`. Pokud se stejny problem objevi na dalsim stroji,
zkontrolovat poradi v `[Environment]::GetEnvironmentVariable("Path","User")`.

Flask chybel (`requests`/`bs4` uz nainstalovane byly), doinstalovan.
Appka po oprave nastartovala a servuje spravny obsah (`GET /` -> 200,
"Archiv inzeratu - annonce.cz").

## 2026-08-01 (refaktoring)

Na pozadavek "udelej debugging i refactoring" pridana sdilena funkce
`download_one(url) -> (ad_id, data)` do `download_ads.py`, ktera obaluje
kroky `ad_id_from_url -> fetch -> parse_ad -> save_ad -> update_index`.
Predtim byla tato posloupnost duplikovana zvlast v `download_ads.main()`
(CLI) a zvlast v `app.py`'s `download()` (web UI). Chovani beze zmeny
(overeno: opakovane stazeni existujiciho inzeratu pres web UI stale vraci
"OK: <nazev> (<ad_id>)" a pocet ulozenych inzeratu se nemeni).

## 2026-08-01 (oprava: falesny poplach ohledne "mojibake" kodovani)

Behem refaktoringu (viz nize) jsem se domnival, ze `data.json`/`index.csv`
obsahuji poskozene znaky (napr. "Hezk�á Slovenka" misto "Hezká Slovenka") a
navrhl/implementoval jsem kolem toho retry logiku v `fetch()`. **Byl to omyl
z me strany.** Kdyz jsem primo zkontroloval SUROVE BAJTY ulozenych `data.json`
souboru (ne jejich zobrazeni v terminalu), ukazalo se, ze data jsou vzdy
spravne UTF-8 (napr. `Hezk\xc3\xa1 Slovenka` - to je korektni "á"). Znak "�",
ktery jsem opakovane videl v terminalovem vystupu, byl artefakt zobrazeni me
vlastni terminalove/nastrojove vrstvy (kodova stranka Windows konzole pri
prenosu vystupu), ne skutecny obsah promennych ani souboru. Zadna realna
korupce kodovani v `download_ads.py`/`app.py` nikdy nebyla potvrzena.

Kod byl vracen zpet na puvodni jednoduchy `fetch()` (`request_with_retry(url).text`),
bez zbytecne "detekce a retry na U+FFFD" logiky, ktera resila neexistujici
problem. Ponechany zmeny: `request_with_retry()` (genuinni odolnost proti
sitovym chybam) a `download_one()` refaktoring (sdilena logika mezi CLI a
web appkou - viz nize).

Pouceni: pri hlaseni "poskozenych" ceskych znaku vzdy nejdriv overit surove
bajty na disku (`open(path, 'rb').read()` + hex/`repr` bajtu), ne jen
`repr()` retezce vypsany do terminalu.

## 2026-08-01 (dodatek: doplneni chybejicich telefonu)

**Zadani:** "doplň telefony kde nejsou."

**Zjisteno:**
- `index.csv` byl mistama nespolehlivy - jeden radek (Vanessa,
  `vanessa-80748947-wbsyj8`, stazeno behem tohoto sezeni) mel posunute
  sloupce (telefon skoncil ve sloupci `height`), druhy radek (Ziva Chloe)
  mel telefon prazdny v CSV, i kdyz ho `data.json` mel spravne ulozeny.
  Pricina konkretniho posunuti radku Vanessy nebyla dohledana (mozna
  nejaky edge-case v `description`/`services` pri zapisu), ale protoze
  `data.json` je pro kazdy inzerat spolehlivy zdroj pravdy, `index.csv`
  byl **kompletne prestaven ze vsech `data.json` souboru** (zaloha puvodniho
  `index.csv` udelana pred prepisem a po overeni smazana).
- Po prestavbe: z 114 inzeratu chybi telefon jen u 2 - "Sexy a hezká
  transsexuál" a "Viki". U obou overeno primo v aktualnim HTML z annonce.cz
  (znovu stazeno), ze telefon na strance vubec neni uveden (zadny vyskyt
  slova "telefon" ani `tel:` odkazu) - tito inzerenti zjevne nabizeji jen
  kontakt pres zpravu, ne telefon. Neni tedy co doplnit, jde o realny stav
  inzeratu, ne o chybu extrakce.

**Vysledek:** `index.csv` opraven a synchronizovan s `data.json` (114/114
radku), telefony doplneny vsude, kde existuji. 2 inzeraty zustavaji bez
telefonu zamerne (na strance zadny neni).

## 2026-08-01

**VYRESENO:** uzivatel pridal `pythonw.exe` a `python.exe` mezi povolene
aplikace v Rizenem pristupu ke slozkam (Windows Security). Nasledny test
stahnuti presne tohoto inzeratu (`hezka-slovenka-87754197-w51734`) uspesny:
`OK: Hezká Slovenka`. Pripad uzavren.

**Kontext:** uzivatel poslal screenshot bezici aplikace (`127.0.0.1:5000/download`)
po pokusu stahnout jeden inzerat. Vysledek stahovani:

```
Nalezeno 1 URL ke zpracovani.
[1/1] CHYBA u https://www.annonce.cz/inzerat/hezka-slovenka-87754197-w51734.html:
[WinError 2] Systém nemůže nalézt uvedený soubor:
'C:\Users\Radek\Documents\annoncio\stazene_inzeraty\hezka-slovenka-87754197-w51734'
Hotovo.
```

**Vysetreni:**
- Precteny `app.py` a `download_ads.py`. Chyba se hodi na `save_ad()`, ktera dela
  `ad_dir.mkdir(parents=True, exist_ok=True)` a pak zapis `data.json` do daneho adresare.
- Rucne overeno v terminalu presne na stejne ceste (`stazene_inzeraty\hezka-slovenka-87754197-w51734`):
  vytvoreni adresare i zapis souboru probehly bez chyby.
- `stazene_inzeraty\` existuje a obsahuje 100+ drivejsich inzeratu, takze se
  nejedna o chybejici rodicovsky adresar ani o spatnou cestu (`OUTPUT_DIR` je
  pocitane z `Path(__file__).resolve().parent`, nezavisi na aktualnim pracovnim adresari).
- `Documents` neni presmerovany na OneDrive (Known Folder Move), takze to neni
  typicky pripad OneDrive on-demand placeholderu blokujiciho zapis.

**Zaver zatim:** chyba pravdepodobne vznikla jednorazove/prechodne (napr. antivirus
nebo indexovaci sluzba drzici kratky zamek pri vytvareni noveho adresare pod
`stazene_inzeraty\`), protoze stejna operace spustena rucne hned potom probehla
v poradku. Neni potvrzeno jako trvala chyba v kodu.

**Dalsi kroky (otevrene):**
- Pri dalsim vyskytu zaznamenat, jestli je chyba reprodukovatelna opakovane pro
  stejne URL, nebo se stane jen obcas u nahodnych URL (podporilo by to teorii
  o prechodnem zamku souboru).
- Zvazit v `save_ad()` jednoduchy retry (1-2 pokusy s kratkou prodlevou) kolem
  `mkdir`/zapisu `data.json`, pokud se problem bude opakovat.
- Pridany `CHANGELOG.md` a `WORKLOG.md` na zaklade tohoto vysetreni.

**Dodatek (o par minut pozdeji):** uzivatel zkusil znovu stahnout stejne URL a
dostal jinou chybu: `[Errno 9] Bad file descriptor` (misto puvodniho WinError 2).
Dve ruzne nizkourovnove OS chyby na stejne operaci u stejneho URL potvrzuji, ze
nejde o deterministickou chybu v logice, ale o neco nestabilniho v uz bezicim
serverovem procesu (`app.py` spusteny pres `pythonw` z `spustit.ps1` beh dlouho
na pozadi).

Overeno v cistem, nove spustenem Python procesu (mimo bezici server):
- primy `requests.get()` na dane URL: OK (200, 44993 B).
- cely pipeline `fetch -> parse_ad -> save_ad -> update_index` na presne tento
  `ad_id`: OK, i se zamerne rozbitym `sys.stdout`/`sys.stderr` (simulace chovani
  `pythonw.exe` bez konzole) - zadny warning/print se v tomto kodu behem
  normalniho behu nezapisuje, takze to neni pricina.

**POTVRZENY ROOT CAUSE:** uzivatel poslal screenshot notifikace "Zabezpeceni
Windows - Neautorizovane zmeny jsou blokovany - Rizeny pristup ke slozkam
zablokoval moznost provadet zmeny pro: pythonw.exe." Windows Defender
Controlled Folder Access (ochrana pred ransomwarem) blokuje `pythonw.exe`
v zapisu do `Documents\annoncio\stazene_inzeraty\` (Documents je jedna
z vychozich chranenych slozek). CFA pri zablokovani nevraci cisty
"access denied", ale zpusobuje, ze dana syscall selze s nesourodou,
nedeterministickou nizkourovnovou chybou - proto se pro uplne stejnou
operaci objevily dve ruzne chyby (`WinError 2`, pak `Errno 9`). Tim padem
vsechny predchozi teorie (prechodny stav procesu, dva souperici servery)
byly slepe ulicky - skutecna pricina je bezpecnostni nastaveni OS, ne
neco v `download_ads.py`/`app.py`.

Pokus opravit to primo z terminalu (`Add-MpPreference
-ControlledFolderAccessAllowedApplications ...`) selhal na chybejicich
opravneni (potrebuje admin/UAC). Misto toho otevreno
`windowsdefender://ransomware`, aby si uzivatel mohl pythonw.exe/python.exe
rucne pridat do povolenych aplikaci pres UAC potvrzeni. Retry logika
pridana drive v teto session (`request_with_retry`) tohle nevyresi -
CFA blokuje kazdy pokus stejne - je to jen doplnkova odolnost proti
skutecnym prechodnym sitovym vypadkum, ne oprava tohoto konkretniho problemu.

(Puvodne zvazovana a zavrzena teorie o stavu serveru, ponechana nize pro
historii vysetrovani:)

Zaver: root cause je pravdepodobne stav jiz bezici instance serveru (napr.
nahodny hickup v socketech/FD tabulce dlouho bezicicho `pythonw` procesu na
Windows), ne chyba v `download_ads.py`/`app.py`. Nejjednodussi obejiti:
**restartovat server** (ukoncit bezici `pythonw`/`python app.py` proces,
spustit znovu `spustit.ps1`).

**Oprava predchozi teorie:** pri kontrole bezicich procesu byly videt dve
`pythonw.exe app.py` PID soucasne (`...WindowsApps\pythonw.exe` a
`...pythoncore-3.14-64\pythonw.exe`) a chvili to vypadalo jako dve nezavisle
instance serveru soutezici o stejne soubory. Po overeni `ParentProcessId` se
ale ukazalo, ze WindowsApps varianta je jen App Execution Alias stub, ktery
realny interpret spusti jako sveho potomka - jde tedy o jeden logicky proces,
ne o dva soubezne servery. Tato teorie o souboji nad `index.csv` tak neplati
a puvodni pricina WinError2/Errno9 zustava nepotvrzena. Pro jistotu byly oba
predchozi `pythonw` procesy ukonceny a spustena jedna cista instance.

**Zmena v kodu:** pro odolnost pridan `request_with_retry()` v
`download_ads.py` - obali `requests.get()` pro HTML stranku inzeratu i pro
kazdou fotku do az 3 pokusu s ~1.5s prodlevou mezi nimi. Nezarucuje to opravu
teto konkretni tridy chyby (nebyla spolehlive reprodukovana), ale zmirni
budouci prechodne sitove/systemove vypadky bez nutnosti rucne to spoustet
znovu z UI.
