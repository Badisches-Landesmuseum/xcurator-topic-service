
'''
KeyCloak Configuration

ToDo: Read config from application.yaml file
ToDo: Do we need all params here?
'''
class KeyCloakConfiguration:
    REALM = 'master'
    CLIENT_ID = 'python-client'
    CLIENT_SECRET = '29024b7e-ee38-4854-8f08-e079d1ee7b0f'
    ALGORITHM = "RS256"
    KEYCLOAK_BASE_URL = "https://keycloak.k8s.3pc.de"

    AUTH_URL = (
        f"{KEYCLOAK_BASE_URL}/auth/realms/{REALM}"
        f"/protocol/openid-connect/auth?client_id={CLIENT_ID}&response_type=code"
    )
