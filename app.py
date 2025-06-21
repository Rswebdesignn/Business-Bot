from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
import json
import requests
import re
from dotenv import load_dotenv
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

# Debug: Print all environment variables to help diagnose issues
print("=== ENVIRONMENT VARIABLES ===")
for key, value in os.environ.items():
    # Print key but mask sensitive values
    if 'KEY' in key or 'SECRET' in key or 'PASSWORD' in key:
        print(f"{key}: ***MASKED***")
    else:
        print(f"{key}: {value}")
print("============================")

# Load environment variables from .env file
load_dotenv()

# Load environment variables from service.json if available
try:
    with open('service.json', 'r') as f:
        service_config = json.load(f)
        if 'environments' in service_config and 'production' in service_config['environments']:
            env_vars = service_config['environments']['production']['env']
            for key, value in env_vars.items():
                if key not in os.environ:
                    os.environ[key] = value
                    print(f"Loaded {key} from service.json")
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Could not load variables from service.json: {str(e)}")

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))  # Get from env or generate random

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///chatbot.db')
# If DATABASE_URL starts with postgres://, replace with postgresql:// (Railway PostgreSQL format)
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Default system prompt template for business assistant
BUSINESS_PROMPT_TEMPLATE = """You are {business_name}'s AI customer support assistant. You provide helpful, accurate, and professional responses to customer inquiries.

BUSINESS INFORMATION:
- Business type: {business_type}
- Business description: {business_description}
- Operating hours: {business_hours}
- Services offered: {services}
- Location: {location}
- Contact information: {contact_info}

APPOINTMENT BOOKING:
- Availability: {availability}
- Booking process: {booking_process}

FREQUENTLY ASKED QUESTIONS:
{faqs}

RESPONSE FORMAT GUIDELINES:
1. START with a brief greeting or acknowledgment.
2. STRUCTURE your response with clear sections:
   - Use BOLD HEADERS (using ** for bold) for different sections when appropriate
   - Use BULLET POINTS (using - ) for lists
   - Use EMOJIS to make the response visually appealing and highlight key points
3. KEEP responses EXTREMELY CONCISE - no more than 2-3 short sentences per paragraph.
4. AVOID lengthy explanations - focus on directly answering the question.
5. For contact info, business hours, or similar factual information, present it in a clean, structured format.
6. End with a very brief, friendly closing when appropriate.

RESPONSE EXAMPLES:
For website inquiry:
"Our website is **www.businessname.com** 🌐
You can book appointments, view services, and check pricing there!"

For contact information:
"**Contact Us** 📞
- Phone: +91 9876543210
- Email: info@business.com
- Hours: Mon-Fri 9am-5pm"

For appointment booking:
"**Available Slots** 📅
- Weekdays: 10am, 2pm, 4pm
- Weekends: 11am, 1pm
Book by calling us or through our website!"

Remember: You represent {business_name} and should uphold their professional standards while keeping responses SHORT, STRUCTURED, and VISUALLY APPEALING."""

# Get API key from environment with multiple fallback options
api_key = os.environ.get("OPENROUTER_API_KEY")

# Debug: Check if API key is found
print(f"API key found: {'Yes' if api_key else 'No'}")

# Fallback to service.json if available
if not api_key:
    try:
        # First try direct service.json
        with open('service.json', 'r') as f:
            service_config = json.load(f)
            if 'environments' in service_config and 'production' in service_config['environments']:
                api_key = service_config['environments']['production']['env'].get('OPENROUTER_API_KEY')
            else:
                api_key = service_config.get('OPENROUTER_API_KEY')
            if api_key:
                print("Using API key from service.json")
                # Set it in environment for other modules
                os.environ["OPENROUTER_API_KEY"] = api_key
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Could not load API key from service.json: {str(e)}")

# Final fallback to a hardcoded key for development/testing only
if not api_key:
    print("WARNING: Using fallback API key. This is not secure for production!")
    api_key = "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"
    # Set it in environment for other modules
    os.environ["OPENROUTER_API_KEY"] = api_key

# OpenRouter API endpoint
api_url = "https://openrouter.ai/api/v1/chat/completions"

# Headers for OpenRouter API
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": os.environ.get("APP_URL", "https://web-production-7dd9.up.railway.app"),
    "X-Title": "Business Assistant Bot"
}

# Store conversation history
conversations = {}

# Business types for dropdown
BUSINESS_TYPES = [
    "Retail Store",
    "Restaurant",
    "Healthcare Provider",
    "Salon/Spa",
    "Legal Services",
    "Financial Services",
    "Real Estate",
    "Educational Institution",
    "Technology Services",
    "Hospitality",
    "Automotive Services",
    "Fitness Center",
    "Other"
]

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    chatbots = db.relationship('BusinessConfig', backref='owner', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class FAQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    config_id = db.Column(db.Integer, db.ForeignKey('business_config.id'), nullable=False)

class BusinessConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.String(50), unique=True, nullable=False)
    business_name = db.Column(db.String(100), nullable=False)
    business_type = db.Column(db.String(50))
    business_description = db.Column(db.Text)
    business_hours = db.Column(db.Text)
    services = db.Column(db.Text)
    location = db.Column(db.String(200))
    contact_info = db.Column(db.String(200))
    availability = db.Column(db.Text)
    booking_process = db.Column(db.Text)
    system_prompt = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    faqs = db.relationship('FAQ', backref='config', lazy=True, cascade="all, delete-orphan")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_system_prompt(config):
    """Generate a system prompt based on the business configuration."""
    # Format FAQs
    formatted_faqs = ""
    if isinstance(config, BusinessConfig):
        for faq in config.faqs:
            formatted_faqs += f"Q: {faq.question}\nA: {faq.answer}\n\n"
    else:
        for qa in config.get('faqs', []):
            formatted_faqs += f"Q: {qa['question']}\nA: {qa['answer']}\n\n"
    
    # Generate the prompt using the template
    if isinstance(config, BusinessConfig):
        prompt = BUSINESS_PROMPT_TEMPLATE.format(
            business_name=config.business_name,
            business_type=config.business_type,
            business_description=config.business_description,
            business_hours=config.business_hours,
            services=config.services,
            location=config.location,
            contact_info=config.contact_info,
            availability=config.availability,
            booking_process=config.booking_process,
            faqs=formatted_faqs
        )
    else:
        prompt = BUSINESS_PROMPT_TEMPLATE.format(
            business_name=config.get('business_name', 'Our Business'),
            business_type=config.get('business_type', 'Service Provider'),
            business_description=config.get('business_description', ''),
            business_hours=config.get('business_hours', ''),
            services=config.get('services', ''),
            location=config.get('location', ''),
            contact_info=config.get('contact_info', ''),
            availability=config.get('availability', ''),
            booking_process=config.get('booking_process', ''),
            faqs=formatted_faqs
        )
    
    return prompt

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', messages=[])

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate inputs
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
            
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
            
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check for admin login
        if username == 'xrohia' and password == '4482@AdmiN':
            # Create a session for admin
            session['is_admin'] = True
            flash('Welcome, Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        # Regular user login
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard to manage chatbots."""
    chatbots = BusinessConfig.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', chatbots=chatbots)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    """Render the admin configuration page."""
    if request.method == 'POST':
        # Redirect POST requests to the save_config route
        return redirect(url_for('save_config'))
    return render_template('admin.html', business_types=BUSINESS_TYPES)

@app.route('/edit_chatbot/<config_id>', methods=['GET', 'POST'])
@login_required
def edit_chatbot(config_id):
    """Edit an existing chatbot configuration."""
    chatbot = BusinessConfig.query.filter_by(config_id=config_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        # Update chatbot configuration
        chatbot.business_name = request.form.get('business_name', '')
        chatbot.business_type = request.form.get('business_type', '')
        chatbot.business_description = request.form.get('business_description', '')
        chatbot.business_hours = request.form.get('business_hours', '')
        chatbot.services = request.form.get('services', '')
        chatbot.location = request.form.get('location', '')
        chatbot.contact_info = request.form.get('contact_info', '')
        chatbot.availability = request.form.get('availability', '')
        chatbot.booking_process = request.form.get('booking_process', '')
        
        # Delete existing FAQs
        for faq in chatbot.faqs:
            db.session.delete(faq)
        
        # Add new FAQs
        questions = request.form.getlist('faq_question[]')
        answers = request.form.getlist('faq_answer[]')
        
        for i in range(len(questions)):
            if questions[i].strip() and i < len(answers):
                faq = FAQ(
                    question=questions[i],
                    answer=answers[i],
                    config_id=chatbot.id
                )
                db.session.add(faq)
        
        # Update system prompt
        chatbot.system_prompt = generate_system_prompt(chatbot)
        
        db.session.commit()
        flash('Chatbot updated successfully', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_chatbot.html', chatbot=chatbot, business_types=BUSINESS_TYPES)

@app.route('/delete_chatbot/<config_id>', methods=['POST'])
@login_required
def delete_chatbot(config_id):
    """Delete a chatbot configuration."""
    chatbot = BusinessConfig.query.filter_by(config_id=config_id, user_id=current_user.id).first_or_404()
    
    # Delete the chatbot
    db.session.delete(chatbot)
    db.session.commit()
    
    flash('Chatbot deleted successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/save_config', methods=['POST'])
@login_required
def save_config():
    """Save the business configuration."""
    try:
        # Get form data
        business_name = request.form.get('business_name', '')
        business_type = request.form.get('business_type', '')
        business_description = request.form.get('business_description', '')
        business_hours = request.form.get('business_hours', '')
        services = request.form.get('services', '')
        location = request.form.get('location', '')
        contact_info = request.form.get('contact_info', '')
        availability = request.form.get('availability', '')
        booking_process = request.form.get('booking_process', '')
        
        # Process FAQs (they come in pairs)
        questions = request.form.getlist('faq_question[]')
        answers = request.form.getlist('faq_answer[]')
        
        # Generate a unique ID for this configuration
        config_id = f"config_{datetime.now().strftime('%Y%m%d%H%M%S')}_{current_user.id}"
        
        # Create new business config in database
        new_config = BusinessConfig(
            config_id=config_id,
            business_name=business_name,
            business_type=business_type,
            business_description=business_description,
            business_hours=business_hours,
            services=services,
            location=location,
            contact_info=contact_info,
            availability=availability,
            booking_process=booking_process,
            user_id=current_user.id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_config)
        db.session.flush()  # Flush to get the ID for the FAQs
        
        # Add FAQs
        for i in range(len(questions)):
            if questions[i].strip() and i < len(answers):
                faq = FAQ(
                    question=questions[i],
                    answer=answers[i],
                    config_id=new_config.id
                )
                db.session.add(faq)
        
        # Generate system prompt
        new_config.system_prompt = generate_system_prompt(new_config)
        
        db.session.commit()
        
        return redirect(url_for('config_success', config_id=config_id))
    
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", 'danger')
        return redirect(url_for('admin'))

@app.route('/config_success/<config_id>')
@login_required
def config_success(config_id):
    """Show success page with chat widget embed code."""
    chatbot = BusinessConfig.query.filter_by(config_id=config_id, user_id=current_user.id).first_or_404()
    return render_template('config_success.html', config=chatbot, config_id=config_id)

@app.route('/chat/<config_id>')
def chat(config_id):
    """Render the chat page for a specific business configuration."""
    chatbot = BusinessConfig.query.filter_by(config_id=config_id).first()
    if not chatbot:
        return redirect(url_for('index'))
    
    return render_template('chat.html', config=chatbot, config_id=config_id)

@app.route('/chat', methods=['OPTIONS'])
def chat_options():
    """Handle CORS preflight requests for the chat endpoint."""
    response = jsonify({})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/chat', methods=['POST'])
def process_chat():
    """Process chat messages from the frontend."""
    try:
        # Get data from request
        data = request.json
        user_message = data.get('message', '').strip()
        config_id = data.get('config_id')
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        if not config_id:
            return jsonify({"error": "Config ID is required"}), 400
        
        # Check if configuration exists
        chatbot = BusinessConfig.query.filter_by(config_id=config_id).first()
        if not chatbot:
            return jsonify({"error": "Business configuration not found"}), 404
        
        # Verify API key is available
        if not api_key:
            return jsonify({
                "error": "API key not configured. Please contact the administrator.",
                "response": "I'm sorry, but I'm unable to process your request at the moment. The service is experiencing technical difficulties. Please try again later or contact support."
            }), 503
        
        # Get the system prompt for this business
        system_prompt = chatbot.system_prompt
        
        # Get unique conversation ID for this chat session and business
        session_id = f"{config_id}_{request.remote_addr}"
        
        # Initialize conversation history if new session
        if session_id not in conversations:
            conversations[session_id] = [{"role": "system", "content": system_prompt}]
        
        # Add user message to conversation history
        conversations[session_id].append({"role": "user", "content": user_message})
        
        # Prepare the request payload for OpenRouter API
        payload = {
            "model": "anthropic/claude-3-haiku",  # Using Claude which is good for business contexts
            "messages": conversations[session_id],
            "temperature": 0.7,  # Balanced temperature for consistent yet natural responses
            "max_tokens": 250,  # Limiting token count to ensure concise responses
            "top_p": 0.95,
            "presence_penalty": 0.5  # Discourage repetitive content
        }
        
        # Make request to OpenRouter API
        try:
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise exception for HTTP errors
        except requests.exceptions.RequestException as api_error:
            print(f"API error: {str(api_error)}")
            return jsonify({"error": "API request failed", "response": "I'm sorry, but I'm having trouble connecting to my knowledge base right now. Please try again in a moment."}), 503
        
        # Parse response
        response_data = response.json()
        assistant_message = response_data['choices'][0]['message']['content']
        
        # Add assistant response to conversation history
        conversations[session_id].append({"role": "assistant", "content": assistant_message})
        
        # Keep conversation history manageable (limit to last 10 messages excluding system prompt)
        if len(conversations[session_id]) > 11:  # system prompt + 10 messages
            conversations[session_id] = [conversations[session_id][0]] + conversations[session_id][-10:]
        
        # Create response with proper headers for iframe compatibility
        response = jsonify({"response": assistant_message})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reset/<config_id>', methods=['OPTIONS'])
def reset_conversation_options(config_id):
    """Handle CORS preflight requests for the reset endpoint."""
    response = jsonify({})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/reset/<config_id>', methods=['POST'])
def reset_conversation(config_id):
    """Reset the conversation history for a specific chat session."""
    try:
        # Get unique conversation ID for this chat session and business
        session_id = f"{config_id}_{request.remote_addr}"
        
        # Check if conversation exists
        if session_id in conversations:
            # Keep only the system prompt
            system_prompt = conversations[session_id][0]
            conversations[session_id] = [system_prompt]
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin_dashboard')
def admin_dashboard():
    """Admin dashboard to view all users and chatbots."""
    # Check if user is admin
    if not session.get('is_admin'):
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('login'))
    
    # Get all users and their chatbots
    users = User.query.all()
    
    # Get total counts
    total_users = len(users)
    total_chatbots = BusinessConfig.query.count()
    
    return render_template('admin_dashboard.html', 
                          users=users, 
                          total_users=total_users, 
                          total_chatbots=total_chatbots)

@app.route('/admin_logout')
def admin_logout():
    """Logout admin user."""
    session.pop('is_admin', None)
    flash('Admin logout successful', 'success')
    return redirect(url_for('login'))

@app.route('/health')
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        "status": "healthy",
        "api_key_configured": bool(api_key),
        "timestamp": datetime.utcnow().isoformat()
    })

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 
