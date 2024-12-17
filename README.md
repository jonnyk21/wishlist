# Familien-Wunschliste 🎄

Eine einfache Webanwendung für die Familie, um Weihnachtswünsche zu teilen.

## Features

- **Einfache Anmeldung**: Melde dich nur mit deinem Namen an
- **Ähnliche Namen-Erkennung**: Verhindert versehentliche Duplikate von Benutzern
- **Wunschliste**: Füge Links zu deinen Wünschen hinzu
- **Automatische Metadaten**: Extrahiert automatisch Titel und Vorschaubilder von den Links
- **Familienübersicht**: Siehe die Wünsche aller Familienmitglieder
- **Zugriffskontrolle**: Geschützter Zugang über Einladungslinks (nur in Produktion)

## Technische Details

### Abhängigkeiten

- Python 3.12
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-Login 0.6.3
- BeautifulSoup4 4.12.2
- Gunicorn 21.2.0 (für Produktion)
- PostgreSQL (für Produktion)
- SQLite (für lokale Entwicklung)

### Lokale Entwicklung

1. Python Virtual Environment erstellen:
```bash
python3 -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
```

2. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

3. Anwendung starten:
```bash
python app.py
```

Die Anwendung ist dann unter `http://localhost:5000` erreichbar.

### Produktion

Die Anwendung läuft auf [Render.com](https://render.com) mit folgender Konfiguration:

- Web Service mit Python Runtime
- PostgreSQL Datenbank
- Automatische HTTPS-Verschlüsselung
- Zugriffskontrolle über Einladungslinks

### Umgebungsvariablen

- `SECRET_KEY`: Für Session-Management (wird automatisch generiert)
- `DATABASE_URL`: PostgreSQL Verbindungs-URL (wird von Render.com bereitgestellt)
- `INVITE_TOKEN`: Für Zugriffskontrolle in Produktion (wird automatisch generiert)

## Sicherheit

- Keine Passwörter erforderlich - einfache Anmeldung nur mit Namen
- Produktionszugriff nur über Einladungslinks
- Automatische HTTPS-Verschlüsselung in Produktion
- Sichere Datenbankverbindung

## Datenschutz

- Nur öffentlich zugängliche Daten werden gespeichert
- Keine persönlichen Daten außer Namen
- Keine Tracking- oder Analysewerkzeuge
