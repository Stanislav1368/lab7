# Frontend: Vue 3 + Vite (dev-сервер, как требует задание).
FROM node:20-alpine

WORKDIR /app

# Сначала зависимости — слой кэшируется, пока не изменились package.json/package-lock.json.
COPY package*.json ./
RUN npm install --no-audit --no-fund

COPY . .

EXPOSE 5173

# --host 0.0.0.0 обязателен, иначе Vite слушает только localhost внутри контейнера.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
