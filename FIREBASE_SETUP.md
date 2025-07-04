# Firebase Setup für MCP-CMS

## Schritt 1: Firebase-Projekt erstellen

1. Gehen Sie zu [Firebase Console](https://console.firebase.google.com)
2. Klicken Sie auf "Projekt hinzufügen"
3. Geben Sie einen Projektnamen ein (z.B. "mcp-cms-2025")
4. Aktivieren Sie Google Analytics (optional)
5. Erstellen Sie das Projekt

## Schritt 2: Services aktivieren

### Authentication
1. Navigieren Sie zu "Authentication" in der linken Sidebar
2. Klicken Sie auf "Get started"
3. Wählen Sie "Sign-in method" Tab
4. Aktivieren Sie "Email/Password" Provider
5. Klicken Sie auf "Save"

### Firestore Database
1. Navigieren Sie zu "Firestore Database"
2. Klicken Sie auf "Create database"
3. Wählen Sie "Start in test mode" (für Development)
4. Wählen Sie eine Region aus (z.B. europe-west1)
5. Klicken Sie auf "Done"

### Storage
1. Navigieren Sie zu "Storage"
2. Klicken Sie auf "Get started"
3. Wählen Sie "Start in test mode"
4. Wählen Sie eine Region aus
5. Klicken Sie auf "Done"

## Schritt 3: Web App registrieren

1. Klicken Sie auf das Web-Symbol (</>) in der Projektübersicht
2. Geben Sie einen App-Namen ein (z.B. "MCP-CMS-Web")
3. Aktivieren Sie "Firebase Hosting" (optional)
4. Klicken Sie auf "Register app"
5. Kopieren Sie die Konfiguration

## Schritt 4: Service Account erstellen

1. Navigieren Sie zu "Project settings" (Zahnrad-Symbol)
2. Klicken Sie auf "Service accounts" Tab
3. Klicken Sie auf "Generate new private key"
4. Speichern Sie die JSON-Datei sicher

## Schritt 5: Credentials einfügen

### Frontend Configuration (/app/frontend/src/App.js)
Ersetzen Sie diese Werte in der `firebaseConfig`:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSy...",                    // Ihre API Key
  authDomain: "ihr-projekt.firebaseapp.com",
  projectId: "ihr-projekt-id",
  storageBucket: "ihr-projekt.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef..."
};
```

### Backend Configuration (/app/backend/.env)
Ersetzen Sie den `FIREBASE_SERVICE_ACCOUNT` Wert mit dem kompletten Inhalt Ihrer Service Account JSON-Datei:

```bash
FIREBASE_SERVICE_ACCOUNT='{"type": "service_account", "project_id": "ihr-projekt-id", "private_key_id": "...", "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n", "client_email": "firebase-adminsdk-...@ihr-projekt.iam.gserviceaccount.com", "client_id": "...", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "..."}'
```

## Schritt 6: Sicherheitsregeln konfigurieren

### Firestore Security Rules
Navigieren Sie zu "Firestore Database" > "Rules" und ersetzen Sie die Regeln:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own user document
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Pages - authenticated users can read, authors/editors/admins can write
    match /pages/{pageId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
        (resource.data.author_id == request.auth.uid || 
         get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role in ['admin', 'editor']);
    }
    
    // Articles - same as pages
    match /articles/{articleId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
        (resource.data.author_id == request.auth.uid || 
         get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role in ['admin', 'editor']);
    }
    
    // Categories - admin/editor only
    match /categories/{categoryId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role in ['admin', 'editor'];
    }
  }
}
```

### Storage Security Rules
Navigieren Sie zu "Storage" > "Rules" und ersetzen Sie die Regeln:

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /uploads/{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

## Schritt 7: Ersten Admin-User erstellen

1. Starten Sie das Frontend (`yarn start`)
2. Öffnen Sie `http://localhost:3000/login`
3. Erstellen Sie einen Account mit Email/Password
4. Melden Sie sich in der MongoDB an und ändern Sie die Rolle des Users zu "admin":

```javascript
db.users.updateOne(
  { email: "ihre-email@example.com" },
  { $set: { role: "admin" } }
)
```

## Schritt 8: Services neu starten

Nach dem Einfügen der Credentials:

```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

## Troubleshooting

### Firebase Connection Error
- Überprüfen Sie die Projekt-ID in beiden Konfigurationen
- Stellen Sie sicher, dass die Service Account JSON korrekt formatiert ist
- Prüfen Sie die Backend-Logs: `tail -f /var/log/supervisor/backend.*.log`

### Authentication Errors
- Überprüfen Sie ob Email/Password Provider aktiviert ist
- Stellen Sie sicher, dass die Domain in Firebase Authentication zugelassen ist
- Prüfen Sie die Browser-Konsole für Fehler

### CORS Errors
- Fügen Sie Ihre Domain zu Firebase Authentication > Settings > Authorized domains hinzu
- Überprüfen Sie die CORS-Konfiguration im Backend

## Erweiterte Konfiguration

### Multi-Factor Authentication
```javascript
// In Firebase Console > Authentication > Settings
// Aktivieren Sie "Multi-factor authentication"
```

### Custom Claims für Rollen
```javascript
// Erweitern Sie die Service Account mit Custom Claims
admin.auth().setCustomUserClaims(uid, { role: 'admin' });
```

### Audit Logging
```javascript
// Aktivieren Sie Cloud Logging für Firebase
// Cloud Console > Logging > Logs Explorer
```

## Produktions-Checklist

- [ ] Firestore Security Rules aktiviert
- [ ] Storage Security Rules aktiviert
- [ ] Authentication Domains konfiguriert
- [ ] Service Account Permissions minimiert
- [ ] Backup-Strategie implementiert
- [ ] Monitoring und Alerts konfiguriert
- [ ] Rate Limiting aktiviert
- [ ] Budget Alerts konfiguriert