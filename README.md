# Familien-Wunschliste 🎄

Eine einfache Webanwendung für die Familie, um Weihnachtswünsche zu teilen.

## Features

- **Einfache Anmeldung**: Melde dich nur mit deinem Namen an
- **Ähnliche Namen-Erkennung**: Verhindert versehentliche Duplikate von Benutzern
- **Wunschliste**: Füge Links zu deinen Wünschen hinzu
- **Automatische Metadaten**: Extrahiert automatisch Titel und Vorschaubilder von den Links
- **Familienübersicht**: Siehe die Wünsche aller Familienmitglieder
- **Zugriffskontrolle**: Geschützter Zugang über Einladungslinks (nur in Produktion)
- **Prioritäten**: Ordne deine Wünsche nach Wichtigkeit
  - "Muss ich haben ⭐⭐⭐"
  - "Wäre schön ⭐⭐"
  - "Vielleicht ⭐"

## Technische Details

### Abhängigkeiten

- Python 3.12
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-Login 0.6.3
- BeautifulSoup4 4.12.2
- Gunicorn 21.2.0 (für Produktion)
- Neon PostgreSQL (für Produktion)
- SQLite (für lokale Entwicklung)

### Lokale Entwicklung

1. Installiere `uv` falls noch nicht vorhanden:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Repository klonen und ins Verzeichnis wechseln:
```bash
git clone [repository-url]
cd wishlist
```

3. Python-Umgebung erstellen und aktivieren:
```bash
uv venv
source .venv/bin/activate  # Unter Windows: .venv\Scripts\activate
```

4. Abhängigkeiten installieren:
```bash
uv pip install -r requirements.txt
```

5. Anwendung starten:
```bash
python app.py
```

Die Anwendung ist dann unter `http://localhost:5000` erreichbar.

### Produktion

Die Anwendung läuft auf [Render.com](https://render.com) mit folgender Konfiguration:

- Web Service mit Python Runtime
- Datenbank: [Neon PostgreSQL](https://neon.tech) (Free Tier)

#### Einrichtung der Produktionsumgebung

1. Neon PostgreSQL Datenbank erstellen:
   - Auf [Neon Console](https://console.neon.tech) registrieren
   - Neues Projekt erstellen
   - Die Connection String kopieren

2. Render.com Konfiguration:
   - Unter "Environment Variables" die `DATABASE_URL` mit der Neon Connection String setzen
   - Format: `postgresql://user:password@endpoint/dbname`

### Umgebungsvariablen

- `DATABASE_URL`: PostgreSQL Connection String (nur Produktion)
- `SECRET_KEY`: Sitzungsschlüssel
- `INVITE_TOKEN`: Token für Einladungslinks (nur Produktion)

### Datenbank-Migrationen

Die Anwendung verwendet SQLAlchemy für Datenbankoperationen. Migrationen werden automatisch beim Start ausgeführt.

#### Manuelle Migration ausführen

```bash
source .venv/bin/activate
python -c "from app import create_app; app = create_app(); app.app_context().push(); from migrations.add_priority import upgrade; upgrade()"
```

### Sicherheit

- Alle Datenbankoperationen sind mit Retry-Logik und Fehlerbehandlung ausgestattet
- Verbindungs-Pooling für bessere Performance
- Automatische Reconnects bei Verbindungsabbrüchen
- Geschützte Routen durch Flask-Login
- Sichere Sitzungsverwaltung
