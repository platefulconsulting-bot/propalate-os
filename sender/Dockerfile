FROM node:20-slim

# Chromium + fonts + libs whatsapp-web.js / puppeteer needs
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    chromium \
    ca-certificates \
    fonts-liberation \
    fonts-noto-color-emoji \
    libasound2 \
    libnss3 \
    libxss1 \
    libxtst6 \
    dumb-init \
 && rm -rf /var/lib/apt/lists/*

# Use system Chromium; skip Puppeteer's bundled download.
ENV PUPPETEER_SKIP_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app

# Install deps first so layer caches well
COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force

# Copy app source
COPY . .

EXPOSE 3000

# dumb-init forwards SIGTERM cleanly to Node so client.destroy() runs on redeploy
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "sender.js"]
