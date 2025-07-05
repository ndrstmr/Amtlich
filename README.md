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
