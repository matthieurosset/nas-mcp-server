FROM python:3.12-alpine

WORKDIR /app

# Installer les dépendances système nécessaires
RUN apk add --no-cache gcc musl-dev

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ ./src/

# Définir le PYTHONPATH pour les imports
ENV PYTHONPATH=/app/src

# Port par défaut
EXPOSE 3001

# Lancer le serveur
CMD ["python", "src/main.py"]
