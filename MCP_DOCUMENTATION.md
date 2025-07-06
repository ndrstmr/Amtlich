# MCP-CMS: Model Context Protocol Server

## Überblick

Das MCP-CMS ist ein modernes Content Management System, das als Model Context Protocol (MCP) Server fungiert. Es ermöglicht AI-Clients wie Claude, GPT-4, oder andere LLMs, strukturierte Tool-Calls zu senden und Content-Management-Operationen durchzuführen.

## Architektur

### Backend (FastAPI)
- **MCP Server**: Empfängt und verarbeitet Tool-Calls
- **Firebase Authentication**: Sichere Benutzerauthentifizierung
- **MongoDB**: Dokumentenbasierte Datenspeicherung
- **Tool Registry**: Modulares System für Tool-Erweiterungen
- **Role-based Access Control**: Granulare Berechtigungen

### Frontend (React)
- **Firebase Auth Integration**: Benutzeranmeldung
- **Admin Dashboard**: Inhalts- und Benutzerverwaltung
- **MCP Tool Tester**: Interaktive Tool-Testing-Oberfläche
- **Responsive Design**: Mobile-first Tailwind CSS

## Verfügbare MCP Tools

### 1. createPage
Erstellt eine neue Seite im CMS.

**Beispiel:**
```json
{
  "tool": "createPage",
  "args": {
    "title": "Über uns",
    "content": "<h1>Über unser Unternehmen</h1><p>Wir sind ein innovatives Technologieunternehmen...</p>",
    "meta_description": "Erfahren Sie mehr über unser Unternehmen und unsere Mission",
    "status": "published"
  }
}
```

**Parameter:**
- `title` (string, required): Seitentitel
- `content` (string, optional): HTML-Inhalt
- `slug` (string, optional): URL-Slug (automatisch generiert wenn nicht angegeben)
- `meta_description` (string, optional): SEO Meta-Description
- `parent_id` (string, optional): ID der übergeordneten Seite
- `status` (string, optional): "draft" oder "published" (default: "draft")

### 2. createArticle
Erstellt einen neuen Artikel/Blogpost.

**Beispiel:**
```json
{
  "tool": "createArticle",
  "args": {
    "title": "Die Zukunft der AI in der Content-Erstellung",
    "content": "<h1>AI revolutioniert Content-Creation</h1><p>Artificial Intelligence...</p>",
    "excerpt": "Wie AI die Art und Weise verändert, wie wir Content erstellen",
    "tags": ["AI", "Content", "Innovation"],
    "category_id": "tech-blog",
    "status": "published"
  }
}
```

**Parameter:**
- `title` (string, required): Artikel-Titel
- `content` (string, optional): HTML-Inhalt
- `excerpt` (string, optional): Kurzbeschreibung
- `featured_image` (string, optional): URL des Hauptbilds
- `tags` (array, optional): Tags für den Artikel
- `category_id` (string, optional): Kategorie-ID
- `status` (string, optional): "draft" oder "published"

### 3. updatePage
Aktualisiert eine bestehende Seite.

**Beispiel:**
```json
{
  "tool": "updatePage",
  "args": {
    "page_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Über uns - Aktualisiert",
    "content": "<h1>Unser aktualisiertes Unternehmensprofil</h1>",
    "status": "published"
  }
}
```

**Parameter:**
- `page_id` (string, required): ID der zu aktualisierenden Seite
- Alle anderen Parameter aus `createPage` (optional)

### 4. createUser
Erstellt einen neuen Benutzer (nur für Admins).

**Beispiel:**
```json
{
  "tool": "createUser",
  "args": {
    "firebase_uid": "firebase_user_uid_here",
    "email": "editor@example.com",
    "name": "Max Mustermann",
    "role": "editor"
  }
}
```

**Parameter:**
- `firebase_uid` (string, required): Firebase User ID
- `email` (string, required): E-Mail-Adresse
- `name` (string, required): Vollständiger Name
- `role` (string, optional): "admin", "editor", "author", "viewer"

## Benutzerrollen

### Admin
- Vollzugriff auf alle Funktionen
- Kann Benutzer erstellen und verwalten
- Kann alle Inhalte bearbeiten und löschen
- Zugriff auf System-Einstellungen

### Editor
- Kann alle Inhalte bearbeiten und veröffentlichen
- Kann Kategorien und Tags verwalten
- Kann Medien hochladen und verwalten
- Kann eigene und fremde Inhalte bearbeiten

### Author
- Kann eigene Inhalte erstellen und bearbeiten
- Kann eigene Entwürfe veröffentlichen
- Kann Medien für eigene Inhalte hochladen
- Kann keine fremden Inhalte bearbeiten

### Viewer
- Nur Lesezugriff auf Inhalte
- Kann Dashboard einsehen
- Kann keine Inhalte erstellen oder bearbeiten

## API-Endpunkte

### MCP Endpoints
- `POST /api/mcp/dispatch` - Hauptendpunkt für Tool-Calls
- `GET /api/mcp/tools` - Liste verfügbarer Tools

### Authentication
- `POST /api/auth/register` - Benutzer registrieren (Rolle wird immer als `viewer` gesetzt)
- `GET /api/auth/me` - Aktuelle Benutzerinformationen

### Content Management
- `GET /api/pages` - Alle Seiten abrufen
- `GET /api/pages/{id}` - Einzelne Seite abrufen
- `GET /api/articles` - Alle Artikel abrufen
- `GET /api/articles/{id}` - Einzelnen Artikel abrufen
- `GET /api/categories` - Alle Kategorien abrufen

### Dashboard
- `GET /api/dashboard/stats` - Dashboard-Statistiken

## Sicherheit

### Authentication
- Firebase Authentication mit JWT-Token
- Automatische Token-Erneuerung
- Sichere Session-Verwaltung

### Authorization
- Role-based Access Control (RBAC)
- Granulare Berechtigungen pro Tool
- Ressourcen-basierte Zugriffskontrolle

### Datenvalidierung
- Pydantic-basierte Request-Validierung
- SQL-Injection-Schutz durch MongoDB
- Input-Sanitization

## Verwendung mit AI-Clients

### Claude Integration
```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

# Tool-Call an MCP Server
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    messages=[{
        "role": "user",
        "content": "Erstelle eine neue Seite mit dem Titel 'Datenschutz' und einem grundlegenden Datenschutzinhalt"
    }],
    tools=[{
        "name": "mcp_dispatch",
        "description": "Sendet Tool-Calls an MCP-CMS Server",
        "input_schema": {
            "type": "object",
            "properties": {
                "tool": {"type": "string"},
                "args": {"type": "object"}
            }
        }
    }]
)
```

### OpenAI Integration
```python
import openai

client = openai.OpenAI(api_key="your-api-key")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{
        "role": "user",
        "content": "Erstelle 5 Blogartikel über AI-Trends"
    }],
    tools=[{
        "type": "function",
        "function": {
            "name": "create_article",
            "description": "Erstellt einen neuen Artikel",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    }]
)
```

## Entwicklung und Erweiterung

### Neue Tools hinzufügen
1. Tool-Klasse implementieren:
```python
class CustomTool(Tool):
    def get_name(self) -> str:
        return "customTool"
    
    async def execute(self, args: Dict[str, Any], user: User) -> Dict[str, Any]:
        # Tool-Logik hier
        return {"success": True, "data": "result"}
```

2. Tool registrieren:
```python
tool_registry.register(CustomTool())
```

### Datenmodelle erweitern
```python
class CustomModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Deployment

### Lokale Entwicklung
```bash
# Backend starten
cd backend
pip install -r requirements.txt
uvicorn server:app --reload

# Frontend starten
cd frontend
yarn install
yarn start
```

### Produktion
```bash
# Docker-Container
docker-compose up -d

# Oder mit Supervisor
sudo supervisorctl start all
```

## Monitoring und Logging

### Logs
- Backend: `/var/log/supervisor/backend.*.log`
- Frontend: Browser-Konsole und Network-Tab
- Firebase: Firebase Console > Analytics

### Metriken
- API-Response-Zeiten
- Tool-Call-Erfolgsrate
- Benutzer-Aktivitäten
- Fehlerrate

## Backup und Recovery

### Datenbank-Backup
```bash
mongodump --host localhost --port 27017 --db mcp_cms --out /backup/
```

### Firebase-Backup
- Firestore: Automatische Backups in Firebase Console konfigurieren
- Authentication: User-Export über Firebase Admin SDK

## Troubleshooting

### Häufige Probleme
1. **Firebase Connection Error**: Überprüfen Sie die Service Account-Konfiguration
2. **Tool Call Fails**: Prüfen Sie Benutzerberechtigungen und Token-Gültigkeit
3. **CORS Issues**: Überprüfen Sie die erlaubten Origins
4. **MongoDB Connection**: Stellen Sie sicher, dass MongoDB läuft

### Debug-Modus
```bash
# Backend Debug-Logs
export LOG_LEVEL=DEBUG
uvicorn server:app --reload --log-level debug

# Frontend Debug
export REACT_APP_DEBUG=true
yarn start
```

## Support und Community

- **Dokumentation**: `/app/FIREBASE_SETUP.md`
- **Issues**: GitHub Issues
- **Diskussionen**: GitHub Discussions
- **API-Referenz**: `/api/docs` (Swagger UI)

## Lizenz

MIT License - Siehe LICENSE-Datei für Details.