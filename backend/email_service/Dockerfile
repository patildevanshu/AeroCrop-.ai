FROM node:20-bookworm-slim

# Install system dependencies, Chromium, fonts (including Marathi/Hindi Devanagari & Emojis), and dumb-init
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    fonts-noto-core \
    fonts-noto-devanagari \
    fonts-noto-color-emoji \
    fonts-freefont-ttf \
    fonts-liberation \
    fontconfig \
    dumb-init \
    debianutils \
    ca-certificates \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PORT=5000

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

COPY . .

EXPOSE 5000

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["node", "server.js"]
