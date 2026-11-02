"""
HelpMeDraft — tests de non-régression des correctifs de sécurité.

Couvre :
  [2] refresh token : seule l'empreinte SHA-256 est en base, rotation,
      détection de rejeu, logout par empreinte ;
  [3] JWT_SECRET_KEY : démarrage refusé si la variable est absente ;
  [4] cookie de refresh : HttpOnly, Path=/auth, Secure piloté par APP_ENV ;
  [6] CSRF : SameSite=Strict sur le cookie de refresh ;
  [5] ON DELETE CASCADE : vérifié en SQL pur, hors SQLAlchemy (RGPD art. 17).

Le test XSS du point [1] est côté frontend (voir frontend/test_xss.mjs).

Exécution (depuis backend/, venv activé) :
    python test_securite.py
Il crée et détruit sa propre HelpMeDraft.db — ne pas lancer sur une base
de dev contenant des données à conserver.
"""

import hashlib
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
os.chdir(HERE)

# --- Test 3 : absence de JWT_SECRET_KEY => échec explicite au démarrage ------
code = "import app.config"
env = {k: v for k, v in os.environ.items() if k != "JWT_SECRET_KEY"}
env["PATH"] = os.environ["PATH"]
env["DOTENV_DISABLED"] = "1"
r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, cwd=HERE)
assert r.returncode != 0, "L'app a démarré sans JWT_SECRET_KEY !"
assert "JWT_SECRET_KEY est absente" in r.stderr, r.stderr[-500:]
print("[3] OK  démarrage refusé sans JWT_SECRET_KEY :", r.stderr.strip().splitlines()[-1][:90])

# --- Boot de l'app ----------------------------------------------------------
os.environ["JWT_SECRET_KEY"] = "cle_de_test_" + "x" * 40
os.environ["APP_ENV"] = "development"
for p in ("HelpMeDraft.db",):
    pathlib.Path(p).unlink(missing_ok=True)

from sqlalchemy import select

from app import create_app
from database.db import SessionLocal, UserSession

app = create_app()
app.config["RATELIMIT_ENABLED"] = False
c = app.test_client()
print("[boot] OK  create_app() sans erreur")

EMAIL = "equi@test.fr"
MDP = "Motdepasse1"

r = c.post(
    "/auth/register",
    json={"email": EMAIL, "mdp": MDP, "lastname": "B", "firstname": "Equi", "rgpd_consent": True},
)
assert r.status_code == 201, (r.status_code, r.get_json())
print("[parcours] OK  inscription 201")

r = c.post("/auth/login", json={"email": EMAIL, "mdp": MDP})
assert r.status_code == 200, (r.status_code, r.get_json())
access = r.get_json()["access_token"]
cookie_hdr = r.headers.get("Set-Cookie")
plain_token = c.get_cookie("refresh_token", path="/auth").value
print("[parcours] OK  connexion 200")

# --- Test 4 : attributs du cookie en dev ------------------------------------
assert "HttpOnly" in cookie_hdr and "Path=/auth" in cookie_hdr, cookie_hdr
assert "Secure" not in cookie_hdr, cookie_hdr
print("[4] OK  dev : HttpOnly + Path=/auth, sans Secure ->", cookie_hdr)

# --- Test 6 : SameSite=Strict (CSRF) ----------------------------------------
assert "SameSite=Strict" in cookie_hdr, cookie_hdr
print("[6] OK  SameSite=Strict pose\u0301 sur le cookie de refresh")

# --- Test 2 : la base ne contient que l'empreinte ---------------------------
with SessionLocal() as db:
    rows = db.execute(select(UserSession)).scalars().all()
    assert len(rows) == 1
    stored = rows[0].refresh_token_hash
assert stored != plain_token, "le jeton est stocké en clair !"
assert stored == hashlib.sha256(plain_token.encode()).hexdigest()
assert len(stored) == 64
print(f"[2] OK  base = empreinte SHA-256 ({stored[:16]}...), jeton en clair absent")

# --- refresh : rotation + rejeu détecté -------------------------------------
r = c.post("/auth/refresh")
assert r.status_code == 200, (r.status_code, r.get_json())
new_plain = c.get_cookie("refresh_token", path="/auth").value
assert new_plain != plain_token
with SessionLocal() as db:
    hashes = [s.refresh_token_hash for s in db.execute(select(UserSession)).scalars().all()]
assert hashlib.sha256(new_plain.encode()).hexdigest() in hashes
print("[2] OK  /auth/refresh : rotation avec nouvelle empreinte")

c.set_cookie("refresh_token", plain_token, path="/auth")
r = c.post("/auth/refresh")
assert r.status_code == 401, r.status_code
assert "utilisation" in r.get_json()["error"] or "Réutilisation" in r.get_json()["error"], (
    r.get_json()
)
with SessionLocal() as db:
    assert db.execute(select(UserSession)).scalars().all() == []
print("[2] OK  rejeu d'un ancien jeton -> 401 + révocation de toutes les sessions")

# --- document : parcours complet --------------------------------------------
r = c.post("/auth/login", json={"email": EMAIL, "mdp": MDP})
access = r.get_json()["access_token"]
H = {"Authorization": "Bearer " + access}
XSS = '# Titre\n\n<img src=x onerror="alert(1)">\n'
r = c.post("/documents", json={"titre": "Doc test", "content": XSS}, headers=H)
assert r.status_code in (200, 201), (r.status_code, r.get_json())
print("[parcours] OK  création de document", r.status_code)

r = c.post("/auth/logout")
assert r.status_code == 200, r.get_json()
with SessionLocal() as db:
    assert db.execute(select(UserSession)).scalars().all() == []
print("[2] OK  /auth/logout supprime bien la session (recherche par empreinte)")

# --- Test 5 : cascade côté SGBD ---------------------------------------------
from sqlalchemy import text

from database.db import engine

with engine.connect() as conn:
    ddl = conn.execute(text("SELECT sql FROM sqlite_master WHERE name='user_session'")).scalar()
assert "ON DELETE CASCADE" in ddl, ddl
print("[5] OK  DDL généré :", [ligne.strip() for ligne in ddl.splitlines() if "CASCADE" in ligne])

with engine.connect() as conn:
    conn.execute(text("PRAGMA foreign_keys=ON"))
    uid = conn.execute(text("SELECT user_id FROM user")).scalar()
    n_before = conn.execute(text("SELECT COUNT(*) FROM document")).scalar()
    conn.execute(text("DELETE FROM user WHERE user_id = :u"), {"u": uid})
    conn.commit()
    n_after = conn.execute(text("SELECT COUNT(*) FROM document")).scalar()
    n_cons = conn.execute(text("SELECT COUNT(*) FROM consentement")).scalar()
assert n_before == 1 and n_after == 0 and n_cons == 0, (n_before, n_after, n_cons)
print("[5] OK  DELETE FROM user en SQL pur -> documents et consentements supprimés (RGPD art.17)")
print("\nTOUS LES TESTS PASSENT")
