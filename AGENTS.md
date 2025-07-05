# Überblick: 
AMTLICH.AI (Automated Management of Tasks, Laws, Information & Content with Hyperintelligence) ist ein neuartiger MCP-Server, der KI-gestützt Inhalte und Workflows in einem Verwaltungsumfeld managt ￼ ￼. Der Tech-Stack umfasst einen FastAPI-basierten Backend-Server, eine React-basierte Frontend-Single-Page-App und MongoDB als Datenbank ￼. Externe KI-Dienste (z.B. OpenAI GPT-4, Anthropic Claude, Google Gemini) sind nahtlos über ein Tool-Calling-System integriert ￼.

## Backend Architektur: 

Das Backend ist in Python (FastAPI) implementiert und in modulare Pakete gegliedert:
	•	Models (backend/models) – Definiert die Datenstrukturen mittels Pydantic. Beispielmodelle: User (Benutzer mit id, email, role usw.), Page/Article (Content-Modelle), ToolCall & ToolResponse (für KI-Aufträge und Antworten) ￼ ￼. Diese Modelle sichern die Datenkonsistenz und werden auch als Schemas für die API-Dokumentation genutzt.
	•	Services (backend/services) – Kapselt externe Systeme und Geschäftslogik. Wichtig sind:
	•	db: Verbindet zur MongoDB (z.B. Initialisierung des Mongo-Clients, Bereitstellung von Collection-Handles wie db.users, db.pages).
	•	auth: Kümmert sich um Authentifizierung und Autorisierung. Verifiziert z.B. Firebase ID Tokens und liefert den aktuellen User (get_current_user) ￼ ￼. Stellt auch eine Rollen-Überprüfungs-Dependency bereit (require_roles), um Endpunkte auf bestimmte User-Rollen einzuschränken ￼ ￼.
	•	tools: Implementiert die KI-Integration. Hält einen zentralen Tool-Registry (tool_registry), welche verfügbare KI-Tools registriert (z.B. GPTTool, ClaudeTool). Jedes Tool hat eine einheitliche Schnittstelle (execute(...)), sodass der Aufrufer abstrakt damit arbeiten kann. Errors im Tool werden durch Exceptions oder spezielle Rückgaben kenntlich gemacht und vom Aufrufer behandelt.
	•	Routes (backend/routes) – Definiert die API-Endpunkte. Es gibt getrennte Router für öffentliche Endpunkte (z.B. POST /api/auth/register – Benutzerregistrierung) und geschützte Endpunkte (alles was Auth erfordert, z.B. /api/mcp/..., /api/pages/...). Geschützte Routen sind mit Abhängigkeiten versehen, die nur eingeloggten Benutzern mit passenden Rollen Zugriff erlauben ￼ ￼. Beispiele:
	•	POST /api/mcp/dispatch – Nimmt einen ToolCall an und ruft das entsprechende KI-Tool auf. Antwort ist ein ToolResponse mit success=true und Daten, oder success=false und Fehlermeldung ￼ ￼.
	•	GET /api/mcp/tools – Liefert die Liste aller verfügbaren Tools (für das Frontend, um z.B. Auswahl anzubieten) ￼ ￼.
	•	POST /api/auth/register – Legt nach erfolgreicher Firebase-Authentifizierung einen neuen Nutzer in der Datenbank an ￼ ￼.
	•	Weitere Endpunkte für Content-Verwaltung: GET /api/pages, POST /api/pages, GET /api/pages/{id} etc. (Diese sind vorhanden, um Inhalte wie Seiten/Artikel anzulegen und abzurufen – im Code ersichtlich durch Funktionen get_pages, create_page usw. und entsprechende Datenbankoperationen).

## Frontend Architektur: 

Das Frontend (React + Vite) bildet die Benutzeroberfläche. Es kommuniziert über die REST-API mit dem Backend. Wichtige Aspekte:
	•	Login/Auth: Erfolgt über Firebase (externe OAuth2). Nach Login erhält das Frontend ein JWT, das bei API-Calls als Bearer-Token mitgeschickt wird. Auf diese Weise sind geschützte API-Routen abgesichert.
	•	State Management: (nicht detailliert im Code-Auszug, aber anzunehmen) – React-Components werden genutzt für Inhalte, möglicherweise React Context oder Redux für globale Zustände (z.B. aktueller User, Auth-Status).
	•	Aufbau: Komponenten für typische Verwaltungsfunktionen: z.B. eine Seite zur Auflistung von Artikeln, ein Editor für Inhalte (der KI-gestützt sein könnte: „KI-gestütztes Bearbeiten von Content“ laut Vision), eine Benutzerverwaltung usw. Lazy Loading wird genutzt, um Module bei Bedarf zu laden ￼.
	•	Testing: Es gibt Frontend-Tests (z.B. für Login), was auf gut strukturierte, isolierbare Komponenten hindeutet.

## AI-Integration (Tool-Calling): Herzstück von AMTLICH.AI ist die KI-Integration:
	•	Die Tool-Registry hält Instanzen der KI-Tools. Zum Beispiel könnte ein GPT-Tool eingebunden sein, das über OpenAI-API Texte erzeugt, und ein Claude-Tool über Anthropics API. Jeder Tool-Aufruf enthält im ToolCall den Tool-Namen und Argumente (z.B. Prompt-Text, Parameter).
	•	Beim Dispatch (/api/mcp/dispatch) passiert folgendes: Das Backend validiert zunächst den User (ist eingeloggt, hat Rechte). Dann sucht tool_registry.get_tool(tool_name) das passende Tool ￼. Wird es nicht gefunden, gibt es sofort eine Fehlerrückmeldung ￼. Wenn doch, wird asynchron tool.execute(args, user) aufgerufen ￼. Die Tools können intern wiederum API-Calls machen (z.B. HTTP-Requests an OpenAI).
	•	Das Resultat des Tools (z.B. generierter Text, Analyseergebnis) wird zurückgegeben und als JSON an den Client geliefert. Fehlerbehandlung: Sollte das Tool einen Fehler werfen (Exception), fängt das Backend dies ab, loggt den Fehler und setzt im ToolResponse.success=False mit einer Fehlermeldung ￼. Unknown Tools werden mit einer Fehlermeldung "Tool 'xyz' not found" beantwortet ￼. Zeitouts oder API-Fehler können aktuell als generische Fehler kommen; in Zukunft evtl. mit spezifischem Code (z.B. "tool_timeout").
	•	Liste verfügbarer Tools: Über /api/mcp/tools kann das Frontend die aktuellen Tools abfragen – z.B. um dem User eine Dropdown-Liste anzubieten. Dies wird aus der Registry generiert ￼.

## Authentifizierung & Berechtigungen: 

AMTLICH.AI nutzt Firebase für Benutzer-Login (OIDC). Das heißt, Benutzer authentifizieren sich gegen einen externen Identity Provider (z.B. E-Mail/Passwort über Firebase oder SSO). Der Backend-Server erhält dann ein ID-Token und verifiziert es über die Firebase Admin SDK ￼. Nach erfolgreicher Verifikation wird in unserer eigenen MongoDB geprüft, ob der User bereits registriert ist. Wenn nicht, kann er über /api/auth/register angelegt werden (dort muss ein Admin-Token benutzt werden, um Self-Signup zu verhindern) ￼. Jeder User hat eine Rolle (admin, editor, author, viewer) ￼, welche seine Berechtigungen bestimmt:
	•	Admin: Vollzugriff, kann z.B. neue Nutzer anlegen, Inhalte bearbeiten, Einstellungen ändern.
	•	Editor/Author: Eingeschränkter Zugriff – z.B. Autoren dürfen nur ihre eigenen Inhalte bearbeiten, Editoren dürfen alle Inhalte bearbeiten, aber keine User verwalten.
	•	Viewer: Nur Leserechte auf Inhalte.
Diese Rollen werden bei jedem Request durch Dependencies überprüft. Beispiel: Ein Endpoint zum Seiten bearbeiten könnte mit Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)) geschützt sein, so dass nur Admins und Editoren ihn aufrufen dürfen ￼. Unberechtigte erhalten eine Fehlermeldung "Insufficient permissions" mit HTTP 403.

## Datenhaltung: MongoDB speichert die Daten schemalos in Collections:
	•	users Collection: Enthält Benutzer-Dokumente (id, name, email, role, firebase_uid, etc.).
	•	pages, articles, media Collections: Enthalten Content-Dokumente. Ein Page-Dokument könnte Felder haben wie id, title, body, author_id, timestamps usw. (Der genaue Aufbau wird durch Pydantic Models Page, Article vorgegeben).
	•	Die IDs sind bei uns als UUID-Strings realisiert (z.B. User.id wird per uuid4() generiert ￼, Content likewise), statt auf MongoDB ObjectIds zu setzen. Das macht das System unabhängig von MongoDB-spezifischen ID-Formaten – ein Plus für mögliche DB-Migrationen.
	•	Indizes: (noch zu ergänzen) Vermutlich werden Queries v.a. über {"id": ...} oder {"firebase_uid": ...} gemacht ￼. In Produktion sollten dafür Indizes definiert werden, um Performance zu sichern.

## Logging & Monitoring: 
Das Backend verfügt über strukturiertes Logging. In backend/logging_config.py ist ein benutzerdefiniertes Format definiert, das z.B. Exceptions mit Stacktrace ins Log schreibt ￼. Jeder API-Fehler wird geloggt (über logger.exception(...) in Exception-Handlern und in kritischen Catch-Blöcken) ￼ ￼. Dieses Logging ermöglicht es, Probleme nachzuvollziehen. Für ein volles Monitoring könnte man diese Logs an einen Dienst senden (ELK, CloudWatch etc.). Außerdem wäre denkbar, Metriken zu erheben (wie viele AI-Dispatches pro Stunde, Durchsatz, Latenzen der externen KI-APIs) – derzeit noch nicht umgesetzt, aber dank modularer Struktur leicht anzubauen.

## DevOps & Deployment: 
AMTLICH.AI ist containerisiert: Über docker-compose.yml kann man Backend, Frontend und eine MongoDB-Instanz hochfahren ￼. Das Backend liest Konfiguration aus Umgebungsvariablen (z.B. MongoDB-URL, erlaubte CORS-Origin, Firebase Credentials), sodass Deployment zwischen Entwicklung und Produktion unkompliziert angepasst werden kann. Die Tests (Unit- und Integrationstests) laufen automatisiert in der CI-Pipeline, was die Qualität sicherstellt. Für Production ist vorgesehen, das System in Q4/2025 als MVP bereitzustellen ￼ – bis dahin sind noch Performance-Optimierungen und Sicherheits-Audits (Stichwort BSI-Konformität) geplant. Durch die moderne, schlanke Codebasis ist das Projekt für Contributor attraktiv (gemäß README “Dev-friendly: schlanker Stack, moderne DX” ￼). Eine Contributing.md ist in Aussicht, um externe Beiträge zu erleichtern.
