################
# Run in NGINX #
################

# Utilizamos una imagen base de Node.js para construir el proyecto
FROM node:20-alpine AS builder

# Establecer el directorio de trabajo para la etapa de construcción
WORKDIR /app

# Copiar package.json y package-lock.json para instalar dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código fuente
COPY . .

# Construir el proyecto Angular (se generará la carpeta dist)
RUN npm run build --prod

# Cambiar a la imagen base de nginx para servir la aplicación
FROM nginx:latest

# Copiar los archivos generados en la etapa de construcción a la carpeta pública de nginx
COPY --from=builder /app/dist/maletas-ui/browser /usr/share/nginx/html

# Copiar el archivo env.template.js
#COPY public/env.template.js /usr/share/nginx/html/env.template.js

# Copiar la configuración de nginx personalizada (si aplica)
#COPY nginx.conf /etc/nginx/conf.d/default.conf

# Comando para reemplazar variables en env.template.js y arrancar nginx
CMD ["/bin/sh", "-c", "envsubst < /usr/share/nginx/html/env.template.js > /usr/share/nginx/html/env.js && exec nginx -g 'daemon off;'"]
