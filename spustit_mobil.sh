#!/data/data/com.termux/files/usr/bin/bash
# Jednoklikove spusteni annoncio na mobilu (Termux). Ekvivalent spustit.ps1/.bat
# pro Windows. Spusti server na pozadi (prezije zavreni Termuxu jen s
# termux-wake-lock, jinak Android proces casem uspi) a otevre Chrome.

set -e
cd "$(dirname "$0")"

server_up() {
    curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/ 2>/dev/null | grep -q "^200$"
}

if ! server_up; then
    python3 -c "import flask, requests, bs4" 2>/dev/null || pip install --quiet flask requests beautifulsoup4

    nohup python3 app.py > /tmp/annoncio.log 2>&1 &
    disown

    for i in $(seq 1 20); do
        sleep 0.5
        server_up && break
    done
fi

if command -v termux-open-url >/dev/null 2>&1; then
    termux-open-url http://127.0.0.1:5000
else
    echo "Server bezi. Otevri v Chrome: http://127.0.0.1:5000"
fi
