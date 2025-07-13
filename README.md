# AMTLICH.AI

_**Automated Management of Tasks, Laws, Information & Content with Hyperintelligence**_

> 🏛️ Der MCP-Server, den kein Amtsleiter freigeben würde – aber jede:r braucht.

AMTLICH.AI ist ein **modularer MCP-Server** auf Basis von **FastAPI + MongoDB + React**, der eine neue Ära im digitalen Verwaltungsumfeld einläutet:

- 🚀 **AI-first**: Vollintegrierte Sprachmodelle steuern Inhalte, Workflows und Strukturen
- 🧠 **Context-aware**: Jeder Vorgang kennt seinen Kontext – und reagiert
- 🧩 **Modular & API-driven**: Inhalte, Rechte, Medien, Workflows – alles Headless
- 🔒 **Secure & Public-Ready**: Optional BSI-konform, 100 % Open Source
- 🧰 **Dev-friendly**: Schlanker Stack, moderne DX, schnelle Erweiterbarkeit
- 🌍 **Multilingual & Multijurisdictional**: Für echte Digital-Souveränität in Europa

---

## 🔧 Tech Stack

| Layer       | Technologie        | Besonderheiten                              |
|-------------|--------------------|---------------------------------------------|
| Frontend    | React (Vite)       | Modular, Lazy-Loaded Components             |
| API         | FastAPI            | Async, typed, Swagger-ready                 |
| Backend     | MongoDB Atlas/Local| Flexibles Schema für dynamische Inhalte     |
| AI-Client   | Claude, GPT, Gemini| Vollintegriert über Tool-Calling            |
| Auth        | OIDC / OAuth2      | Behörden-ready mit SSO-Unterstützung        |

---

## 📦 Module (Beispiele)

- `createPage()` – Anlage neuer Seiten mit Inhaltstypen
- `updateContent()` – KI-gestütztes Bearbeiten von Content
- `manageUsers()` – Rechteverwaltung & Redaktionsrollen
- `uploadMedia()` – Mediendatenbank mit Drag’n’Drop
- `promptQueue()` – Verarbeitung eingehender AI-Tasks
- Neu registrierte Benutzer erhalten automatisch die Rolle `viewer`.

---

## 🧠 Vision

Die Verwaltung ist nicht zu langsam – sie wurde nur **noch nie mit echten Werkzeugen** digitalisiert.

Mit AMTLICH.AI beweisen wir:  
> 🧾 *Ein KI-gesteuerter Server kann in Minuten erledigen, wofür Behörden Wochen brauchen.*

---

## 🚀 Demo, Roadmap & Contribute

→ Coming soon auf [amtlich.ai](https://amtlich.ai)  
→ MVP Release: Q4/2025  
→ Starte lokal mit `docker-compose` und deinem eigenen Claude oder GPT-Account.  
→ Beitrag willkommen! Siehe `CONTRIBUTING.md`.

### Local Docker Setup

1. Build and run all services:
   ```bash
   docker-compose up --build
   ```
2. Backend erreichbar unter [http://localhost:8000](http://localhost:8000)
3. Frontend erreichbar unter [http://localhost:3000](http://localhost:3000)
4. MongoDB läuft als Container und wird vom Backend automatisch über `mongodb://mongo:27017` angesprochen.

Stoppe alle Dienste mit:
```bash
docker-compose down
```

### Linting

Back-end formatting and lint checks:
```bash
black --check backend tests
flake8 backend tests
```

Front-end lint and style checks:
```bash
yarn lint
yarn prettier --check .
```

These commands are executed in CI for every commit.

## ⚙️ Voraussetzungen & lokale Entwicklung

Bevor du loslegst, installiere **Python 3.11**, **Node.js 20** und **Yarn**. Optional kannst du alle Dienste auch komplett in Docker starten.

### Wichtige Umgebungsvariablen

| Variable                 | Beschreibung                                                    | Default                          |
|--------------------------|----------------------------------------------------------------|----------------------------------|
| `MONGO_URL`              | MongoDB-Verbindungs-URL                                         | `mongodb://localhost:27017`      |
| `DB_NAME`                | Datenbankname                                                  | `amtlich`                        |
| `FIREBASE_SERVICE_ACCOUNT` | JSON mit Firebase-Credentials                                 | `{}`                             |
| `AI_BASE_URL`            | Basis-URL eines externen AI-Dienstes                           | *(optional)*                     |
| `AI_API_KEY`             | API-Key für den AI-Dienst                                      | *(optional)*                     |
| `ALLOWED_ORIGINS`        | Kommagetrennte Liste erlaubter CORS-Origin            | `http://localhost:3000`          |
| `REACT_APP_API_URL`      | API-Endpunkt für das Frontend                                  | `http://localhost:8000`          |

Lege für das Backend eine `.env`-Datei an oder exportiere die Variablen in deiner Shell.
Die Variablen `MONGO_URL` und `DB_NAME` sind erforderlich. Fehlen sie, stoppt der Backend-Start mit einem Fehler.

### Schritte ohne Docker

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --reload

# Frontend
cd ../frontend
yarn install
yarn start
```

### Docker-Variante

Mit `docker-compose up --build` werden alle Container (MongoDB, Backend, Frontend) erstellt und gestartet. Passe bei Bedarf die oben genannten Variablen in `docker-compose.yml` an.

## 🗄️ Architekturüberblick

**Backend**

- `backend/routes` – FastAPI-Routen (öffentliche und geschützte Endpunkte)
- `backend/services` – Business-Logik und Integrationen (Datenbank, Auth, AI-Tools)
- `backend/models` – Pydantic-Modelle für User, Page, Article usw.
- `server.py` – zentrale App-Konfiguration

**Frontend**

- `src/components` – React-Komponenten für Dashboard und CMS
- `src/__tests__` – Frontend-Tests mit Jest/React Testing Library

## 🧪 Tests ausführen

Backend-Tests laufen mit **pytest**:

```bash
pytest
```

Im Docker-Setup kannst du sie mit `docker-compose exec backend pytest` starten.

Frontend-Tests startest du im `frontend`-Verzeichnis:

```bash
yarn test
```

## Deployment Notes

Beim Start des Backends werden wichtige MongoDB-Indizes erzeugt. Dies umfasst
einzigartige Indizes auf den Feldern `firebase_uid` und `id` sowie einen
nicht eindeutigen Index auf `email` der `users` Collection. Bei einem frischen
Deployment stellt das Backend so sicher, dass Abfragen performant bleiben.

