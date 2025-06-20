# Business Chatbot Application

A Flask web application that allows users to create and manage AI-powered chatbots for business customer support. The application uses OpenRouter API to power the chatbot conversations.

## Deployment on Railway

### Prerequisites
- A Railway account (https://railway.app/)
- OpenRouter API key (https://openrouter.ai/)

### Deployment Steps

1. **Fork or clone this repository to your GitHub account**

2. **Connect your Railway account to GitHub**
   - Sign in to Railway
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account if not already connected
   - Select the repository

3. **Configure Environment Variables**
   In the Railway dashboard for your project, go to the "Variables" tab and add the following environment variables:

   ```
   OPENROUTER_API_KEY=your_openrouter_api_key
   SECRET_KEY=your_random_secret_key
   APP_URL=your_railway_app_url (after deployment)
   ```

   You can generate a random secret key using Python:
   ```python
   import os
   os.urandom(24).hex()
   ```

4. **Deploy the Application**
   - Railway will automatically detect the Procfile and requirements.txt
   - The application will be deployed and a URL will be generated

5. **Set the APP_URL Environment Variable**
   - After deployment, copy the URL of your deployed application
   - Add it as the APP_URL environment variable in the Railway dashboard

## Admin Access

The application has a built-in admin account with the following credentials:
- Username: xrohia
- Password: 4482@AdmiN

You can access the admin dashboard by logging in with these credentials at the login page.

## Database

The application uses SQLite by default, but Railway will automatically provision a PostgreSQL database if you add it as a service.

To add a PostgreSQL database:
1. Go to your project in the Railway dashboard
2. Click "New"
3. Select "Database" and then "PostgreSQL"
4. Railway will automatically add the DATABASE_URL environment variable

## Features

- User registration and authentication system
- Create, edit, and delete chatbots for different businesses
- Customizable business information for each chatbot
- FAQ management for each chatbot
- Chat interface for end users
- Admin dashboard to monitor users and chatbots

## Technology Stack

- Flask (Python web framework)
- SQLAlchemy (ORM)
- OpenRouter API (AI integration)
- HTML/CSS/JavaScript (Frontend)
- PostgreSQL/SQLite (Database)
- Railway (Hosting platform) 