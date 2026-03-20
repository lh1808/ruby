# Variante A: curl
curl http://localhost:8501/api/health

# Variante B: falls curl nicht installiert
python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8501/api/health').read().decode())"

# Variante C: falls der Port anders ist (z.B. Domino)
curl http://localhost:${DOMINO_APP_PORT:-8501}/api/health
