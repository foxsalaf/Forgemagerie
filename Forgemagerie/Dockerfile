FROM node:18-alpine AS base

# Backend build stage
FROM base AS backend-builder
WORKDIR /app/backend
COPY backend/package*.json ./
RUN npm ci --only=production
COPY backend/ .
RUN npm run build

# Frontend build stage  
FROM base AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
ENV NEXT_PUBLIC_API_URL=/api
RUN npm run build

# Production stage
FROM base AS production
WORKDIR /app

# Install backend dependencies
COPY backend/package*.json ./backend/
RUN cd backend && npm ci --only=production

# Copy built backend
COPY --from=backend-builder /app/backend/dist ./backend/dist
COPY --from=backend-builder /app/backend/prisma ./backend/prisma

# Copy built frontend
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/package.json ./frontend/

# Install frontend production dependencies
RUN cd frontend && npm ci --only=production

# Create startup script
RUN echo '#!/bin/sh\ncd /app/backend && npm start' > /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 3001

CMD ["/app/start.sh"]