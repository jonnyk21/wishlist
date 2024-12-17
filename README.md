# 🎄 Familien-Wunschliste

Eine einfache und benutzerfreundliche Weihnachtswunschliste-Anwendung für Familien. Familienmitglieder können ihre Wünsche teilen und sehen, welche Geschenke bereits gekauft wurden, ohne dass der Beschenkte es mitbekommt.

## ✨ Funktionen

- **Einfache Anmeldung**: Nur den Namen eingeben, keine Passwörter nötig
- **Wünsche hinzufügen**: Einfach die URL eines Produkts einfügen
- **Automatische Informationen**: Titel und Vorschaubild werden automatisch von der Webseite geholt
- **Geschenke markieren**: Familie kann Geschenke als "gekauft" markieren
- **Übersichtlich**: Alle Wünsche der Familie auf einen Blick
- **Diskret**: Beschenkte sehen nicht, wer ihre Geschenke gekauft hat

## 🚀 Installation

1. Python 3.12 oder höher installieren
2. Repository klonen:
```bash
git clone https://github.com/yourusername/wishlist.git
cd wishlist
```

3. Virtuelle Umgebung erstellen und aktivieren:
```bash
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
```

4. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

5. Anwendung starten:
```bash
python app.py
```

Die Anwendung ist dann unter `http://localhost:5000` erreichbar.

## 💻 Technologien

- **Backend**: Python mit Flask
- **Datenbank**: SQLite mit SQLAlchemy
- **Frontend**: Bootstrap 5
- **Zusätzlich**: 
  - Flask-Login für Benutzerverwaltung
  - BeautifulSoup4 für Webscraping
  - Requests für HTTP-Anfragen

## 🔧 Entwicklung

Die Anwendung verwendet SQLite als Datenbank, was für kleine Familiengruppen ausreichend ist. Die Datenbank wird automatisch erstellt und initialisiert, wenn die Anwendung zum ersten Mal gestartet wird.

## 🌟 Beitragen

Verbesserungsvorschläge sind willkommen! Öffnen Sie einfach ein Issue oder einen Pull Request.

## 📝 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.
