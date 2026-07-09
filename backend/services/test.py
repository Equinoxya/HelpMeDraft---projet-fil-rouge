from auth_service import hash_password, verify_password

h = hash_password("motdepasse123")
print(h)  # quelque chose comme $2b$12$...
print(verify_password("motdepasse123", h))  # True
print(verify_password("mauvais_mdp", h))   