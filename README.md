# 💬 Business Chatbot: AI Customer Support Platform

![Flask](https://img.shields.io/badge/Flask-2.3.3-black)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-3.1.1-red)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![OpenRouter](https://img.shields.io/badge/OpenRouter-API-purple)
![Claude](https://img.shields.io/badge/Claude-3--Haiku-green)
![License](https://img.shields.io/badge/License-Proprietary-red)

## 🌐 Live Demo
[View Business Chatbot Platform](https://business-chatbot.onrender.com)

## 📝 Project Overview
Business Chatbot is a powerful web application that enables businesses to create customized AI customer support assistants. This platform allows users to configure personalized chatbots with specific business information, FAQs, and service details. Powered by Claude AI through OpenRouter, the chatbots provide professional, accurate, and concise responses to customer inquiries, enhancing customer support capabilities without requiring 24/7 human staff.

## ⚠️ Copyright Notice
**This project is fully copyrighted and exclusively owned by Rohit Gunthal.** All rights reserved. No part of this application, including its code, design, data, or content may be reproduced, distributed, or transmitted in any form or by any means without prior written permission from Rohit Gunthal. Unauthorized use, copying, or modification of any part of this project is strictly prohibited.

## ✨ Features
- 🤖 Customizable AI chatbots for businesses
- 🏢 Business-specific configuration (hours, services, location)
- ❓ Custom FAQ management for each chatbot
- 💬 Persistent conversation history
- 🔌 Embeddable chat widget for websites
- 👤 User authentication and management
- 👨‍💼 Admin dashboard for monitoring
- 📱 Responsive design for all devices
- 🌙 Light/dark mode support
- 🔒 Secure environment variable management
- 📊 Database-backed conversation tracking

## 🛠️ Technologies Used
- Flask web framework
- SQLAlchemy ORM with SQLite database
- Flask-Login for authentication
- Flask-Migrate for database migrations
- OpenRouter API integration
- Claude 3 Haiku AI model
- Gunicorn WSGI server
- Bootstrap for responsive UI
- JavaScript for interactive features
- Render for cloud deployment
- Environment-based configuration

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- OpenRouter API key
- Git (for version control)

### Installation
1. Clone the repository
```bash
git clone https://github.com/rohitgunthal18/business-chatbot.git
cd business-chatbot
```

2. Create and activate a virtual environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
```bash
# Create a .env file with the following:
OPENROUTER_API_KEY=your_openrouter_api_key
SECRET_KEY=your_secure_secret_key
ADMIN_USERNAME=admin_username
ADMIN_PASSWORD=secure_admin_password
```

5. Initialize the database
```bash
python init_db.py
```

6. Run the application
```bash
python app.py
```

7. Access the application
```
http://localhost:5000
```

## 🌩️ Deployment
This application is configured for deployment on Render. Follow these steps:

1. Push your code to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Configure environment variables in the Render dashboard
5. Deploy the application

Detailed deployment instructions are available in the `deployment_guide.md` file.

## 🏗️ Project Structure
- `app.py`: Main application file with routes and business logic
- `templates/`: HTML templates using Bootstrap
- `static/`: CSS, JavaScript, and other static files
- `migrations/`: Database migration files
- `init_db.py`: Database initialization script
- `Procfile`: Deployment configuration for Render
- `requirements.txt`: Python dependencies
- `render.yaml`: Render deployment configuration

## 🗄️ Database Models
- **User**: User account information and authentication
- **BusinessConfig**: Business details and configuration
- **FAQ**: Frequently asked questions for each business
- **Conversation**: Persistent chat history storage

## 👨‍💻 Author
**Rohit Gunthal**
- LinkedIn: [xrohia](https://www.linkedin.com/in/xrohia)
- Instagram: [@xrohia](https://www.instagram.com/xrohia)
- GitHub: [@rohitgunthal18](https://github.com/rohitgunthal18)
- Email: rohitgunthal44@gmail.com
- Phone: 8408088454

## 📜 License
This project is proprietary and not open-source. All rights reserved by Rohit Gunthal. Permission is required for any use, distribution, or reproduction.

## ⚠️ Disclaimer
This platform utilizes AI models for customer support automation. While the AI is trained to provide accurate and helpful responses, it may not always provide perfect answers. Business owners should review and customize the AI's knowledge base thoroughly to ensure accurate information is provided to customers. Users are advised to verify critical information through official business channels.

## 🔖 Tags
#AICustomerSupport #BusinessChatbot #CustomerService #AIAssistant #ChatbotPlatform #CustomerExperience #BusinessAutomation #AIIntegration #FlaskApplication #PythonWebApp #ClaudeAI #OpenRouter #CustomerEngagement #BusinessTechnology #AutomatedSupport #ResponsiveDesign #WebApplication #BusinessSolution

## 📞 Contact
For any queries, permissions, or issues, please contact:
- Email: rohitgunthal44@gmail.com
- Phone: 8408088454

---
© 2024 Rohit Gunthal. All Rights Reserved. 