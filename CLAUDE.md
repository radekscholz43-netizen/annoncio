# Pokyny pro AI asistenta — annoncio

Na zacatku session si projdi:
- [README.md](README.md) — co annoncio dela, checklist nastaveni na dalsim stroji vcetne mobilu
- [WORKLOG.md](WORKLOG.md) — denik prace, vyresene bugy (nejnovejsi nahore)

## Klicove, co nezapomenout

- annoncio je **oddeleny osobni projekt** od mercurio (realitni byznys) — nesouvisi spolu.
- Repo je **soukrome** — HTTPS klonovani potrebuje GitHub Personal Access Token (scope `repo`), ne heslo.
- **Windows: bare `python`/`pythonw` muze mirit na prazdny Microsoft Store stub** misto skutecne instalace — zkontrolovat poradi v uzivatelskem PATH, viz README a WORKLOG (2026-08-12).
- **Windows Defender Controlled Folder Access** muze blokovat zapis do `stazene_inzeraty/` s nesourodymi chybami (WinError 2, pak Errno 9 pro stejne URL) — reseno pridanim python.exe/pythonw.exe do povolenych aplikaci, viz WORKLOG (2026-08-01).
- **Mobil (Android):** funguje pres Termux + proot-distro Ubuntu (cisty Termux nema binarku pro Claude Code) — postup v README.
- **Bezpecnost:** hesla/tokeny/API klice nikdy nepsat do chatu — jen primo do terminalu.
