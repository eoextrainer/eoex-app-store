# EOEX Store Dockerfile
# Use official Node.js image for Expo/React Native
FROM node:20-bullseye

# Install required system dependencies for Android/Web
RUN apt-get update && apt-get install -y openjdk-17-jdk android-sdk adb wget git python3-pip && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install -g expo-cli && npm install

# Copy the rest of the app
COPY . .

# Expose Expo default port
EXPOSE 8081 19000 19001 19002

# Start Expo
CMD ["npx", "expo", "start", "--tunnel"]
