# 🎄 Familien-Wunschliste

Eine einfache Webanwendung für die Familie, um Weihnachtswünsche zu teilen und zu koordinieren.

## ✨ Funktionen

- **Wunschliste**: Jedes Familienmitglied kann Wünsche hinzufügen und löschen
- **Geschenke markieren**: Familie kann Geschenke als "gekauft" markieren
- **Übersichtlich**: Alle Wünsche der Familie auf einen Blick
- **Diskret**: Beschenkte sehen nicht, wer ihre Geschenke gekauft hat
- **Benutzerverwaltung**: Einfache Anmeldung nur mit Namen
- **Einladungslinks**: Zugriffskontrolle via Einladungslinks (nur in Produktion)
- **Weihnachtliches Design**: Festliche Benutzeroberfläche

## 🚀 Lokale Entwicklung

1. Repository klonen:
```bash
git clone https://github.com/yourusername/wishlist.git
cd wishlist
```

2. Virtuelle Umgebung erstellen und aktivieren:
```bash
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
```

3. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

4. Anwendung starten:
```bash
flask run
```

Die Anwendung ist dann unter `http://localhost:5000` erreichbar. Im lokalen Entwicklungsmodus wird kein Einladungslink benötigt.

## 🌍 Deployment auf Render.com

1. Erstelle einen Account auf [Render.com](https://render.com)

2. Verbinde dein GitHub-Repository

3. Erstelle einen neuen Web Service:
   - Wähle dein Repository
   - Wähle "Python" als Environment
   - Die Build-Befehle sind bereits in `render.yaml` konfiguriert

4. Setze die Umgebungsvariablen:
   - `SECRET_KEY`: Wird automatisch generiert
   - `INVITE_TOKEN`: Wird automatisch generiert
   - `DATABASE_URL`: Wird automatisch von der PostgreSQL-Datenbank gesetzt

5. Teile den Einladungslink:
   ```
   https://[deine-app].onrender.com/invite?token=[INVITE_TOKEN]
   ```
   Den Token findest du in den Umgebungsvariablen deines Render-Projekts.

## 💻 Technologien

- **Backend**: Python mit Flask
- **Datenbank**: 
  - PostgreSQL (Produktion)
  - SQLite (Entwicklung)
- **Frontend**: Bootstrap 5
- **Zusätzlich**: 
  - Flask-Login für Benutzerverwaltung
  - Flask-SQLAlchemy für Datenbankzugriff
  - Requests für HTTP-Anfragen
  - Gunicorn für Produktionsbereitstellung

## 🔧 Entwicklung

Die Anwendung verwendet eine SQLite-Datenbank für die lokale Entwicklung und PostgreSQL in der Produktion. Die Datenbanktabellen werden automatisch erstellt, wenn die Anwendung zum ersten Mal gestartet wird.

## 🔒 Sicherheit

- Einladungslinks sind nur in der Produktionsumgebung erforderlich
- Lokale Entwicklung überspringt die Token-Überprüfung
- Benutzer können sich nur mit Namen anmelden (kein Passwort erforderlich)
- Geschenkreservierungen sind anonym

## 🌟 Beitragen

Verbesserungsvorschläge und Pull Requests sind willkommen!
