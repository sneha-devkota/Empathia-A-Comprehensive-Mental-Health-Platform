import json
from flask import make_response, session
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import timedelta
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(minutes=30)  # Auto-logout after 30 mins

# Set up SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# User Model for SQLite database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

# Psychologists data with image paths updated (still hardcoded in Python)
psychologists = [
    {
        "name": "Dr. Alice",
        "specialization": "Therapist",
        "description": "An experienced therapist helping individuals overcome emotional struggles",
        "education": "PhD in Psychology",
        "phone": f"+977 98{random.randint(10000000, 99999999)}",
        "available_times": ["2:00 PM - 3:00 PM", "7:00 PM - 8:00 PM"],
        "payment": 1300,
        "photo": "dr_alice.jpg"
    },
    {
        "name": "Dr. Bob",
        "specialization": "Counselor",
        "description": "A friendly counselor who focuses on personal growth and development",
        "education": "Masters in Counseling",
        "phone": f"+977 98{random.randint(10000000, 99999999)}",
        "available_times": ["3:00 PM - 4:00 PM", "5:00 PM - 6:00 PM"],
        "payment": 1300,
        "photo": "dr_bob.jpg"
    },
    {
        "name": "Dr. Charlie",
        "specialization": "Clinical psychologist",
        "description": "A clinical psychologist with expertise in treating anxiety, depression, and trauma.",
        "education": "PhD in Clinical Psychology",
        "phone": f"+977 98{random.randint(10000000, 99999999)}",
        "available_times": ["5:00 PM - 6:00 PM", "7:00 PM - 8:00 PM"],
        "payment": 1300,
        "photo": "dr_charlie.jpg"
    },
]

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('welcome'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if email is already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('login'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash('Sign up successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['username'] = user.username
            flash('Login successful', 'success')
            return redirect(url_for('welcome'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/welcome')
def welcome():
    if 'username' in session:
        return render_template('welcome.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Remove the user from the session and also clear the chat history
    session.pop('username', None)
    session.pop('chat_history', None)  # Clear chat history on logout
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if 'chat_history' not in session:
        session['chat_history'] = []

    if request.method == 'POST':
        user_message = request.form.get('user_message', '').strip()

        if user_message:
            # Keyword lists
            sad_keywords = ['sad', 'unhappy', 'down', 'low', 'blue', 'feeling bad', 'feeling down', 'depressed', 'hopeless', 'worthless']
            suicide_keywords = ['self harm', 'suicide','suicidal', 'cut myself', 'hurt myself']
            help_keywords = ['help', 'assistance', 'support']
            hi_keywords = ['hi', 'hello', 'greetings']
            too_keywords = ['too much']
            try_keywords = ['tried', 'trying', 'already tried that', 'didnt help', 'not working', 'have done that already']
            appointment_keywords = ['appointment', 'schedule', 'book']
            frustration_keywords = ['nothing is going right', 'everything is wrong', 'i feel lost', 'i don’t know what to do']
            work_keywords = ['work', 'school', 'college', 'study']
            trying_keywords = ['attempting', 'attempted', 'been pushing through', 'it’s hard', 'struggling', 'stuck']
            music_keywords = ['music', 'sing', 'song', 'songs']
            art_keywords = ['painting', 'sketching', 'draw', 'drwaing', 'sketching', 'art']
            thank_keywords = ['thank', 'thanks', 'thank you']
            break_keywords = ['break', 'time for myself', 'need a break', 'reset', 'self-care']
            relaxation_keywords = ['relax', 'how to relax', 'unwind', 'chill', 'stress relief', 'feel calm']
            stress_keywords = ['stressed', 'overwhelmed', 'anxious', 'pressure', 'too much']
            feelings_keywords = ['heavy', 'tired', 'drained', 'burned out', 'exhausted', 'worn out']
            depression_keywords = [
                "depressed", "mental health check", "depression test", "depression",
                "survey", "test", "assess my mood", "assessment", "depression symptoms",
                "how do i know if i'm depressed", "mental health survey", "self-assessment", "hopeless", "kill myself"
            ]
            normal_keywords = ["normal ups and downs"]
            mild_keywords = ["mild mood disturbance"]
            border_keywords = ["borderline depression"]
            moderate_keywords = ["moderate depression"]
            severe_keywords = ["severe depression"]
            extreme_keywords = ["extreme depression"]

            user_lower = user_message.lower()

            # Check for the most specific condition (borderline depression)
            if any(keyword in user_lower for keyword in border_keywords):
                bot_message = "You may be going through a rough patch, and that’s completely valid. It might help to explore what’s been affecting your mood lately. You're not alone—consider reaching out to someone you trust or trying short mental health exercises. A counselor or therapist could offer even more clarity."
            elif any(keyword in user_lower for keyword in moderate_keywords):
                bot_message = "It seems you're experiencing moderate depression, and that’s important to acknowledge. You deserve support and care. Speaking with a mental health professional can really help—you're not alone in this. You're taking a positive step just by checking in with yourself. ❤️"
            elif any(keyword in user_lower for keyword in severe_keywords):
                bot_message = "You're showing signs of severe depression. It's important to speak with a mental health professional. You're not alone."
                bot_message += f" <a href='{url_for('appointment')}' target='_blank'>Book Appointment</a>"
            elif any(keyword in user_lower for keyword in extreme_keywords):
                bot_message = "This indicates extreme depression. Please seek help immediately. A mental health professional can support you through this."
                bot_message += f" <a href='{url_for('appointment')}' target='_blank'>Book Appointment</a>"

            # Check for the general depression condition (after more specific checks)
           
            # Check for other mood conditions
            elif any(keyword in user_lower for keyword in normal_keywords):
                bot_message = "You're doing well emotionally! It's totally normal to have some ups and downs. Keep engaging in activities that bring you joy, stay socially connected, and remember that taking care of your mental health is always a good idea—even when you're feeling fine. 🌱"
            elif any(keyword in user_lower for keyword in mild_keywords):
                bot_message = "It looks like you're experiencing some mild mood changes. That happens to many of us, especially when life gets overwhelming. Consider talking to a friend, keeping a journal, or trying mindfulness techniques. Small steps can make a big difference. 💛"

            # -- Keep all your other responses exactly as you had them --
            elif any(keyword in user_lower for keyword in stress_keywords):
                bot_message = "I'm really sorry to hear you're feeling stressed. It can be really tough when everything feels like too much.  It might help to talk about what’s causing it. I'm here for you."
            elif any(keyword in user_lower for keyword in sad_keywords):
                bot_message = "I'm really sorry you're feeling this way. You're not alone — I'm here to support you. Would you like to talk more about it?"
            elif any(keyword in user_lower for keyword in feelings_keywords):
                bot_message = "It sounds like you're feeling really drained. It can be really tough when everything feels like too much.  Even short breaks can make a big difference."
            elif any(keyword in user_lower for keyword in frustration_keywords):
                bot_message = "It sounds like you're feeling really overwhelmed. It can feel overwhelming when everything seems to go wrong. Sometimes it's helpful to break things down and focus on one small thing at a time.  I'm here for you — take a breath and let’s talk it through."
            elif any(keyword in user_lower for keyword in suicide_keywords):
                bot_message = "I'm really sorry you're feeling this way.  It's important to reach out to someone who can support you, like a mental health professional or a friend. Would you like help connecting with a professional?"
                bot_message += f" <a href='{url_for('appointment')}' target='_blank'>Book Appointment</a>"
            elif any(keyword in user_lower for keyword in help_keywords):
                bot_message = "I'm here to help. How can I assist you further?"
            elif any(keyword in user_lower for keyword in depression_keywords):
                bot_message = "It seems like you might be feeling down. Would you like to take a mood assessment?"
                bot_message += f" You can book an appointment with one of our psychologists here:  <a href='{url_for('questionnaire')}' target='_blank'>Start the questionnaire</a>"
            elif any(keyword in user_lower for keyword in ['fight', 'disagreement', 'argument', 'conflict', 'mom', 'family']):
                bot_message = "It sounds like things have been tough with your mom lately. High expectations can be overwhelming, especially when it feels like you're not meeting them. It's okay to feel that way. How about we focus on something that might help you relax and feel more centered?"
            elif any(keyword in user_lower for keyword in try_keywords):
                bot_message = "I understand. Sometimes our usual methods don’t feel effective. It could help to try something different, like a short mindfulness exercise, journaling, or even chatting with someone you trust. Sometimes changing things up a bit can make a difference."
            elif any(keyword in user_lower for keyword in too_keywords):
                bot_message = "That’s understandable, especially if things are piling up. It's okay to feel overwhelmed. Sometimes taking a short break or stepping away for a few minutes can help reset your mind. Have you been able to take some time for yourself lately?"
            elif any(keyword in user_lower for keyword in break_keywords):
                bot_message = "Sometimes taking a short break and relax. It can help reset your mind. "
            elif any(keyword in user_lower for keyword in relaxation_keywords):
                bot_message = (
                    "It's important to find ways to relax. What helps you unwind when you're feeling stressed? "
                    "Here are a few things you might try: <br>  <a href='https://www.youtube.com/watch?v=VgdAcENXy84' target='_blank'> 🎵 Music Therapy</a>  <a href='https://www.youtube.com/watch?v=nA5dGCeZO5k' target='_blank'>🎨 Art Therapy</a>  <a href='https://www.youtube.com/watch?v=odADwWzHR24' target='_blank'> 🧘‍♀️ Breathing Exercises</a> Let me know if you'd like more suggestions!"
                )

            elif any(keyword in user_lower for keyword in thank_keywords):
                bot_message = "You're very welcome. It's great that you're being kind to yourself. If you ever need to talk or just vent, I’m always here for you. You're not alone in this! 🌟"
            elif any(keyword in user_lower for keyword in art_keywords):
                bot_message = "That sounds like a great way to unwind. Art can be really healing. Maybe you could set aside a little time to make some art as a way to recharge. Remember, it's okay to take breaks and prioritize your mental well-being. You might want to try some art therapy if you want: <a href='https://www.youtube.com/watch?v=nA5dGCeZO5k' target='_blank'>Art Therapy</a><br>"

            elif any(keyword in user_lower for keyword in music_keywords):
                bot_message = "That sounds like a great way to unwind. Music can be really healing. Maybe you could set aside a little time to listen to some of your favorite tunes as a way to recharge. Remember, it's okay to take breaks and prioritize your mental well-being. You might want to try some music therapy if you want: <a href='https://www.youtube.com/watch?v=VgdAcENXy84' target='_blank'>Music Therapy</a><br>"

            elif any(keyword in user_lower for keyword in trying_keywords):
                bot_message = "It's easy to get caught up in pushing through. You're doing your best, and that matters."
            elif any(keyword in user_lower for keyword in work_keywords):
                bot_message = "That sounds really tough. Work pressure can be draining.  It's important to find ways to manage that pressure. It'll help if you tried setting small, achievable goals for yourself throughout the day."
            elif any(keyword in user_lower for keyword in appointment_keywords):
                bot_message = "Would you like me to help you schedule an appointment? I can guide you to the booking page."
                bot_message += f" <a href='{url_for('appointment')}' target='_blank'>Book Appointment</a>"
            elif any(keyword in user_lower for keyword in hi_keywords):
                bot_message = "Hello! How can I assist you today?"
            else:
                bot_message = "How can I assist you today?"

            session['chat_history'].append(('You', user_message))
            session['chat_history'].append(('Bot', bot_message))
            session.permanent = True

    response = make_response(render_template('chatbot.html', chat_history=session['chat_history']))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    return render_template('questionnaire.html')  # make sure your HTML is named 'questionnaire.html'


@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        psychologist_name = request.form.get('psychologist')
        time_slot = request.form.get('time_slot')
        payment_method = request.form.get('payment_method')

        print(f"DEBUG: Psychologist={psychologist_name}, Time Slot={time_slot}, Payment={payment_method}")

        if not psychologist_name or not time_slot or not payment_method:
            flash("Please select all required fields", "error")
            return redirect(url_for('appointment'))

        # Find the psychologist
        psychologist = next((p for p in psychologists if p["name"] == psychologist_name), None)
        if not psychologist:
            flash("Invalid psychologist selection", "error")
            return redirect(url_for('appointment'))

        session['pending_appointment'] = {
            "psychologist": psychologist_name,
            "time_slot": time_slot,
            "user": session['username'],
            "payment": psychologist["payment"],
            "payment_method": payment_method
        }

        # **REDIRECTION TO PAYMENT GATEWAY**
        if payment_method == "eSewa":
            print("Redirecting to eSewa...")
            return redirect("https://esewa.com.np")
        elif payment_method == "Khalti":
            print("Redirecting to Khalti...")
            return redirect("https://khalti.com")

        flash("Invalid payment method selected", "error")
        return redirect(url_for('appointment'))

    return render_template('appointment.html', psychologists=psychologists)

@app.route('/payment_success')
def payment_success():
    if 'pending_appointment' not in session:
        flash("No appointment pending payment", "error")
        return redirect(url_for('welcome'))

    appointment = session.pop('pending_appointment')

    return render_template('confirmation.html', 
                           user=appointment["user"], 
                           date="Today", 
                           time=appointment["time_slot"], 
                           reason="Mental Health Consultation", 
                           payment=appointment["payment"])  

if __name__ == '__main__':
    app.run(debug=True)
