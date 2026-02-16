# Deploying Your Business Chatbot to Render

This guide will walk you through deploying your Business Chatbot application to Render.com.

## Prerequisites

1. A [GitHub](https://github.com) account
2. A [Render](https://render.com) account (you can sign up with your GitHub account)
3. Your OpenRouter API key

## Step 1: Prepare Your Repository

Before deploying, make sure your code is in a GitHub repository:

1. Create a new repository on GitHub
2. Push your code to the repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/your-username/your-repo-name.git
   git push -u origin main
   ```

## Step 2: Set Up Your Render Account

1. Go to [Render](https://render.com) and sign up or log in
2. Connect your GitHub account if you haven't already

## Step 3: Create a New Web Service on Render

1. From your Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub repository
4. Configure your web service:
   - **Name**: Choose a name for your service (e.g., "business-chatbot")
   - **Environment**: Select "Python"
   - **Region**: Choose the region closest to your users
   - **Branch**: main (or your preferred branch)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

## Step 4: Configure Environment Variables

Add the following environment variables in the Render dashboard:

1. `OPENROUTER_API_KEY`: Your OpenRouter API key
2. `SECRET_KEY`: A secure random string for Flask sessions
3. `ADMIN_USERNAME`: Admin username for your application
4. `ADMIN_PASSWORD`: Admin password for your application

To add environment variables:
1. Go to your web service dashboard
2. Click on "Environment" in the left sidebar
3. Add each key-value pair
4. Click "Save Changes"

## Step 5: Deploy Your Application

1. Click "Create Web Service" at the bottom of the page
2. Wait for the deployment to complete (this may take a few minutes)

## Step 6: Set Up Database

Render automatically creates a persistent disk for your application. Your SQLite database will be stored there.

## Step 7: Test Your Deployment

1. Once deployment is complete, Render will provide a URL for your application (e.g., https://business-chatbot.onrender.com)
2. Visit the URL to ensure your application is running correctly
3. Try logging in and testing the chat functionality

## Step 8: Update Your Application

When you need to update your application:

1. Push changes to your GitHub repository
2. Render will automatically detect the changes and redeploy your application

## Troubleshooting

If you encounter any issues:

1. Check the logs in your Render dashboard
2. Make sure all environment variables are set correctly
3. Verify that your API key is valid by running the test script locally

## Important Notes

1. **Database**: The SQLite database is stored on Render's persistent disk. For production applications with high traffic, consider using a more robust database solution like PostgreSQL.

2. **Environment Variables**: Never commit sensitive information like API keys or passwords to your repository. Always use environment variables.

3. **Custom Domain**: If you want to use a custom domain, you can configure it in the Render dashboard under the "Settings" tab.

4. **Scaling**: Render's free tier has limitations. If your application grows, consider upgrading to a paid plan.

5. **Monitoring**: Regularly check your application's logs and performance in the Render dashboard.

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [OpenRouter Documentation](https://openrouter.ai/docs) 