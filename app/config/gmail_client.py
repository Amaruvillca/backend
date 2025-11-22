import os
import json
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailClient:
    """
    Cliente para interactuar con la API de Gmail usando OAuth2.
    """

    def __init__(self, credentials_file: str = None,
                 token_file: str = 'token.json',
                 scopes: Optional[List[str]] = None):
        self.credentials_file = self._find_credentials_file(credentials_file)
        self.token_file = token_file
        self.scopes = scopes or ['https://www.googleapis.com/auth/gmail.readonly']
        self.service = None
        self.authenticate()

    def _find_credentials_file(self, credentials_file: Optional[str] = None) -> str:
        """
        Busca el archivo de credenciales automáticamente si no se pasa uno.
        """
        if credentials_file and os.path.exists(credentials_file):
            print(f"✅ Usando archivo especificado: {credentials_file}")
            return credentials_file

        possible_names = [
            'client_secret.json',
            'credentials.json',
            'client_secrets.json',
            'gmail_credentials.json',
            'google_credentials.json',
            'oauth_credentials.json'
        ]
        common_folders = ['.', 'config', 'credentials', 'auth', 'secrets']

        for folder in common_folders:
            for name in possible_names:
                path = os.path.join(folder, name)
                if os.path.exists(path):
                    print(f"✅ Archivo de credenciales encontrado: {path}")
                    return path

        raise FileNotFoundError(
            f"No se encontró el archivo de credenciales.\n"
            f"Busqué: {', '.join(possible_names)}\n"
            f"Coloca tu archivo JSON en el proyecto o especifica la ruta."
        )

    def _validate_credentials_file(self) -> bool:
        """
        Verifica que el JSON de credenciales tenga estructura válida.
        """
        try:
            with open(self.credentials_file, 'r') as f:
                creds_data = json.load(f)

            def check_fields(data, fields):
                return all(field in data for field in fields)

            if 'web' in creds_data:
                if check_fields(creds_data['web'], ['client_id', 'client_secret', 'redirect_uris']):
                    print("✅ Estructura 'web' válida")
                    return True

            elif 'installed' in creds_data:
                if check_fields(creds_data['installed'], ['client_id', 'client_secret', 'redirect_uris']):
                    print("✅ Estructura 'installed' válida")
                    return True

            print("❌ Estructura inválida: falta 'web' o 'installed'")
            return False

        except Exception as e:
            print(f"❌ Error validando archivo: {e}")
            return False

    def authenticate(self) -> None:
     """
     Autentica al usuario y crea el servicio de Gmail.
     """
     creds = None
     print(f"🔐 Autenticando con: {self.credentials_file}")

     if not self._validate_credentials_file():
         raise Exception("Archivo de credenciales inválido o incompleto.")

     if os.path.exists(self.token_file):
         try:
             creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
             print("✅ Token cargado desde archivo")
         except Exception as e:
             print(f"⚠️ Error al cargar token: {e}")
             creds = None

     if not creds or not creds.valid:
         if creds and creds.expired and creds.refresh_token:
             print("🔄 Token expirado, intentando refrescar...")
             try:
                 creds.refresh(Request())
                 print("✅ Token refrescado exitosamente")
             except Exception as e:
                 print(f"❌ Error refrescando token: {e}")
                 creds = None

         if not creds:
             print("🚀 Iniciando flujo OAuth...")
             flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.scopes)

             # ⚠️ CAMBIO IMPORTANTE: Puerto FIJO
             creds = flow.run_local_server(
                 port=8090,  # ⬅️ PUERTO FIJO
                 host='localhost',
                 open_browser=True
             )
             print("✅ Autenticación completada")

         with open(self.token_file, 'w') as token:
             token.write(creds.to_json())
             print(f"💾 Token guardado en {self.token_file}")

     self.service = build('gmail', 'v1', credentials=creds)
     print("🎉 Servicio de Gmail inicializado correctamente")

    def get_user_profile(self) -> Dict:
        """
        Obtiene el perfil del usuario autenticado.
        """
        try:
            print("👤 Obteniendo perfil de usuario...")
            profile = self.service.users().getProfile(userId='me').execute()
            print(f"✅ Perfil obtenido: {profile['emailAddress']}")
            return profile
        except HttpError as error:
            raise Exception(f"Error obteniendo perfil: {error}")

    def list_emails(self, max_results: int = 10, label_ids: Optional[List[str]] = None) -> List[Dict]:
        """
        Lista los correos más recientes.
        """
        try:
            print(f"📧 Obteniendo últimos {max_results} correos...")
            params = {'userId': 'me', 'maxResults': max_results}
            if label_ids:
                params['labelIds'] = label_ids

            results = self.service.users().messages().list(**params).execute()
            messages = results.get('messages', [])

            print(f"📬 Encontrados {len(messages)} mensajes")
            emails = [self.get_email(msg['id']) for msg in messages if msg.get('id')]
            return [email for email in emails if email]

        except HttpError as error:
            raise Exception(f"Error listando emails: {error}")

    def get_email(self, message_id: str) -> Optional[Dict]:
        """
        Obtiene un correo específico por ID.
        """
        try:
            message = self.service.users().messages().get(
                userId='me', id=message_id, format='metadata'
            ).execute()
            return self._parse_email_data(message)
        except HttpError as error:
            print(f"⚠️ Error obteniendo email {message_id}: {error}")
            return None

    def _parse_email_data(self, message: Dict) -> Dict:
        """
        Extrae los campos más importantes del correo.
        """
        headers = message['payload'].get('headers', [])
        get_header = lambda name: next((h['value'] for h in headers if h['name'] == name), 'Desconocido')

        return {
            'id': message['id'],
            'subject': get_header('Subject'),
            'from': get_header('From'),
            'date': get_header('Date'),
            'snippet': message.get('snippet', ''),
            'labelIds': message.get('labelIds', []),
            'body': self._get_email_body(message['payload'])
        }

    def _get_email_body(self, payload: Dict) -> str:
        """
        Extrae el cuerpo del mensaje (texto plano o HTML).
        """
        import base64
        
        body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode()
                        break
        else:
            data = payload['body'].get('data')
            if data:
                body = base64.urlsafe_b64decode(data).decode()
        
        return body

    def search_emails(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Busca correos con una consulta tipo Gmail (por ejemplo: 'from:google.com')
        """
        try:
            print(f"🔍 Buscando: '{query}'...")
            results = self.service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            ).execute()
            messages = results.get('messages', [])
            emails = [self.get_email(m['id']) for m in messages if m.get('id')]
            print(f"✅ {len(emails)} correos encontrados.")
            return [e for e in emails if e]
        except HttpError as error:
            raise Exception(f"Error buscando emails: {error}")

    def test_connection(self) -> bool:
        """
        Prueba de conexión rápida a la API de Gmail.
        """
        try:
            self.get_user_profile()
            self.list_emails(max_results=1)
            print("✅ Conexión a Gmail verificada correctamente.")
            return True
        except Exception as e:
            print(f"❌ Error en prueba de conexión: {e}")
            return False
