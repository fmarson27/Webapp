from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the database table as a Python class
class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/music')
def music():
    return render_template('music.html')

# Route to process the form data
@app.route('/subscribe', methods=['POST'])
def subscribe():
    # Grab the data from the HTML form
    user_name = request.form.get('name')
    user_email = request.form.get('email')

    # Create a new database entry
    new_subscriber = Subscriber(name=user_name, email=user_email)
    
    try:
        db.session.add(new_subscriber)
        db.session.commit()
        return "Success! You are now on the mailing list."
        
    except IntegrityError:
        # This triggers if the email is already in the database
        db.session.rollback()
        return "This email is already registered."

if __name__ == '__main__':
    # Create the database table before running the app
    with app.app_context():
        db.create_all()
        
    # Run the server
    app.run(debug=True)