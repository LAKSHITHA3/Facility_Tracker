from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facilities.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Login credentials dictionary (replace with your actual credentials)
login_credentials = {
    'admin': '123'  # Username: password (can be changed as per your needs)
}

# Database model for the Facility
class Facility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(50), nullable=False)

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Vendor login route
@app.route('/vendor', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if login_credentials.get(username) == password:
            session['username'] = username  # Store username in session
            return redirect(url_for('update_facilities'))  # Correct route name to update_facilities
        else:
            return "Invalid credentials"
    return render_template('vendor.html')


# Update facilities route (admin panel)
@app.route('/update-facilities', methods=['GET', 'POST'])
def update_facilities():
    if 'username' not in session:
        return redirect(url_for('vendor'))  # Redirect to login if not logged in

    # Get all facilities from the database
    facilities = Facility.query.all()
    
    if request.method == 'POST':
        # Get the updated facility name and status from the form
        facility_name = request.form['facility_name']
        status = request.form['status']
        
        # Find the facility in the database by name
        facility = Facility.query.filter_by(name=facility_name).first()
        
        # If facility exists, update its status
        if facility:
            facility.status = status
            db.session.commit()  # Commit the changes to the database
    
    # Render the page with the list of facility names
    return render_template('update_facilities.html', facilities=[f.name for f in facilities])

# API to get all facilities in JSON format
@app.route('/api/facilities')
def api_facilities():
    facilities = Facility.query.all()
    return jsonify([{'name': f.name, 'status': f.status} for f in facilities])

# Logout route (to clear session)
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)  # Clear the session
    return redirect(url_for('home'))  # Redirect to the home page

# Initialize the database and create tables if they don't exist
@app.before_request
def create_tables():
    db.create_all()

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
