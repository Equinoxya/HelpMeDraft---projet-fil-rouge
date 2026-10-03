# ==============================================================================
# HelpMeDraft — image du frontend Vue
#
# Construction en deux étapes : Node ne sert qu'à produire les fichiers
# statiques. L'image finale ne contient que nginx et le résultat du build —
# environ 50 Mo au lieu de plusieurs centaines, et aucune chaîne de compilation
# ni dépendance de développement exposée en production.
# ==============================================================================

# ── Étape 1 : construction ────────────────────────────────────────────────────
FROM node:22-alpine AS build

WORKDIR /app

# Dépendances d'abord, pour que le cache Docker survive aux modifications du
# code. « npm ci » et non « npm install » : il installe exactement ce que
# décrit package-lock.json, sans jamais le réécrire — c'est ce qui rend une
# construction reproductible.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# L'URL de l'API est figée dans le bundle au moment du build : Vite remplace
# import.meta.env.VITE_* par des littéraux. Elle ne peut donc PAS être changée
# au démarrage du conteneur — il faut reconstruire l'image pour la modifier.
ARG VITE_API_URL=http://localhost:5000/
ARG VITE_IA_JETONS_PAR_SECONDE=30
ENV VITE_API_URL=$VITE_API_URL \
    VITE_IA_JETONS_PAR_SECONDE=$VITE_IA_JETONS_PAR_SECONDE

RUN npm run build

# ── Étape 2 : service ─────────────────────────────────────────────────────────
FROM nginx:1.29-alpine AS serve

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# nginx tourne en premier plan : un conteneur dont le processus principal passe
# en arrière-plan s'arrête aussitôt.
CMD ["nginx", "-g", "daemon off;"]
