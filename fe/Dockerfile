# Use the official Node.js 22 image as the base
FROM node:22

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and yarn.lock first to leverage Docker caching
COPY package.json yarn.lock ./

# Install dependencies using Yarn
RUN yarn install --frozen-lockfile

# Copy the rest of the application files
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# Start the React app
CMD ["yarn", "start"]