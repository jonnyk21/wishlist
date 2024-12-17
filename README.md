# 🎄 Familien-Wunschliste

Eine einfache und benutzerfreundliche Weihnachtswunschliste-Anwendung für Familien. Familienmitglieder können ihre Wünsche teilen und sehen, welche Geschenke bereits gekauft wurden, ohne dass der Beschenkte es mitbekommt.

## ✨ Funktionen

- **Einfache Anmeldung**: Nur den Namen eingeben, keine Passwörter nötig
- **Wünsche hinzufügen**: Einfach die URL eines Produkts einfügen
- **Automatische Informationen**: Titel und Vorschaubild werden automatisch von der Webseite geholt
- **Geschenke markieren**: Familie kann Geschenke als "gekauft" markieren
- **Übersichtlich**: Alle Wünsche der Familie auf einen Blick
- **Diskret**: Beschenkte sehen nicht, wer ihre Geschenke gekauft hat
- **Benutzerverwaltung**: Benutzer können sich anmelden und ihre Wünsche verwalten
- **Einladungslinks**: Zugriffskontrolle via Einladungslinks
- **Weihnachtliches Design**: Verbesserte Benutzeroberfläche mit Weihnachts-Thema

## 🚀 Installation

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

4. Umgebungsvariablen setzen:
   - `SECRET_KEY`: Für Sitzungsverwaltung verwendet.
   - `DATABASE_URL`: PostgreSQL-Verbindungszeichenfolge für die Produktion.
   - `INVITE_TOKEN`: Token für Zugriffskontrolle.

5. Anwendung starten:
```bash
flask run
```

Die Anwendung ist dann unter `http://localhost:5000` erreichbar.

## 🚀 Deployment

- Die Anwendung wird auf Render.com mit einer PostgreSQL-Datenbank für persistenten Speicher bereitgestellt.
- Stellen Sie sicher, dass Sie die Umgebungsvariablen im Render-Dashboard setzen.

## 💻 Technologien

- **Backend**: Python mit Flask
- **Datenbank**: PostgreSQL mit Flask-SQLAlchemy
- **Frontend**: Bootstrap 5
- **Zusätzlich**: 
  - Flask-Login für Benutzerverwaltung
  - BeautifulSoup4 für Webscraping
  - Requests für HTTP-Anfragen
  - Gunicorn für die Produktionsbereitstellung
  - SQLite für lokale Entwicklung

## 🔧 Entwicklung

Die Anwendung verwendet PostgreSQL als Datenbank, was für große Familiengruppen ausreichend ist. Die Datenbank wird automatisch erstellt und initialisiert, wenn die Anwendung zum ersten Mal gestartet wird.

## 🌟 Beitragen

Verbesserungsvorschläge sind willkommen! Öffnen Sie einfach ein Issue oder einen Pull Request.

## 📝 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.
