from app import create_app
from app.services.auth_service import (
    hash_password, verify_password,
    generate_access_token, decode_access_token
)

app = create_app()

with app.app_context():
    # Test hash
    h = hash_password("motdepasse123")
    # Test JWT
    token = generate_access_token("un-uuid-test-123")
