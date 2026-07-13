from app import create_app
from app.services.auth_service import (
    hash_password, verify_password,
    generate_access_token, decode_access_token
)

app = create_app()

with app.app_context():
    # Test hash
    h = hash_password("motdepasse123")
    print("Hash :", h)
    print("Vérif OK :", verify_password("motdepasse123", h))
    print("Vérif KO :", verify_password("mauvais_mdp", h))

    # Test JWT
    token = generate_access_token("un-uuid-test-123")
    print("Token :", token)
    print("Décodé :", decode_access_token(token))