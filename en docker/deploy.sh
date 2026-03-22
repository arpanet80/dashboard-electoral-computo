#!/bin/bash

# Detener y eliminar contenedores existentes
echo "Deteniendo contenedores existentes..."
docker compose down

# Hacer pull de las últimas imágenes desde Docker Hub
echo "Actualizando imágenes desde Docker Hub..."
docker pull 10.51.15.42:5000/contrataciones-api
docker pull 10.51.15.42:5000/contrataciones-ui

# Reiniciar contenedores con las nuevas imágenes
echo "Reiniciando contenedores..."
docker compose up -d


#    chmod +x deploy.sh
#    ./deploy.sh