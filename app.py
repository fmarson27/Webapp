from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True, nullable=False)

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, default="Anonymous")
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Links replies to this thread. If a thread is deleted, replies go with it.
    replies = db.relationship('Reply', backref='thread', lazy=True, cascade="all, delete-orphan")

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False)
    username = db.Column(db.String(50), nullable=False, default="Anonymous")
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

# Homepage Route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the form submitted was a New Thread or a Reply
        if 'title' in request.form:
            username = request.form.get('username') or "Anonymous"
            title = request.form.get('title')
            content = request.form.get('content')
            
            if title and content:
                new_thread = Thread(username=username, title=title, content=content)
                db.session.add(new_thread)
                db.session.commit()
                
        elif 'thread_id' in request.form:
            username = request.form.get('username') or "Anonymous"
            content = request.form.get('content')
            thread_id = request.form.get('thread_id')
            
            if content and thread_id:
                new_reply = Reply(username=username, content=content, thread_id=thread_id)
                db.session.add(new_reply)
                db.session.commit()
                
        return redirect(url_for('index'))

    # Fetch threads and pass them to the template
    threads = Thread.query.order_by(Thread.created_at.desc()).all()
    return render_template('index.html', threads=threads)

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/music')
def music():
    return render_template('music.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    user_name = request.form.get('name')
    user_email = request.form.get('email')
    new_subscriber = Subscriber(name=user_name, email=user_email)
    try:
        db.session.add(new_subscriber)
        db.session.commit()
        return "Success! You are now on the mailing list."
    except IntegrityError:
        db.session.rollback()
        return "This email is already registered."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)