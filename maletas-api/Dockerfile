# ---------- BUILD STAGE ----------
#FROM node:20-alpine AS build
#WORKDIR /usr/src/app
#COPY package*.json ./
#RUN npm ci
#COPY . .
#RUN npm run build
# ---------- RUNTIME STAGE ----------
#FROM node:20-alpine
#WORKDIR /usr/src/app
#COPY --from=build /usr/src/app/dist ./dist
#COPY --from=build /usr/src/app/node_modules ./node_modules
#COPY package*.json ./
#ENV NODE_ENV=production
#CMD ["node", "dist/main.js"]





# Base image
FROM node:20-alpine
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
COPY .env ./
RUN npm run build
CMD ["npm", "run", "start:prod"]