# Frontend Dockerfile
FROM node:16

# Set the working directory
WORKDIR /frontend

# Copy the package.json and yarn.lock
COPY ./frontend/package.json ./
COPY ./frontend/yarn.lock ./

# Install Yarn and dependencies
RUN yarn install

# Copy the rest of the frontend code
COPY ./frontend .

# Expose the port the frontend runs on
EXPOSE 5173

# Command to start the frontend
CMD ["yarn", "dev"]