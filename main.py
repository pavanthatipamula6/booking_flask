import os
import sqlite3
from flask import Flask, render_template, redirect, flash, request,url_for,g
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo

from wtforms.fields import DateField,TimeField

from datetime import datetime

import pytz



from flask import session

#app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')

app.secret_key = 'your_secret_key_here'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")

# Create or connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create User table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS User (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        balance INTEGER        
    )
''')
conn.commit()
conn.close()
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
# Create User table if it doesn't exist
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS booking_details (
#         user_id INTEGER  ,
#         username TEXT NOT NULL,
#         place TEXT NOT NULL ,
#         date DATE NOT NULL ,
#         time TIME NOT NULL  
#     )
# ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS booking_details (
        user_id INTEGER  ,
        username TEXT NOT NULL,
        place TEXT NOT NULL ,
        slot_no INTEGER NOT NULL ,
        from_datetime DATETIME NOT NULL,
        to_datetime DATETIME NOT NULL
        
    )
''')
conn.commit()
conn.close()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(db_path)
    return db

def close_db(conn):
    conn.close()


def fetch_bookings(user_id):
    conn = sqlite3.connect('your_database.db')  # Replace 'your_database.db' with your database file
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM booking_details WHERE user_id = ?', (user_id,))
    bookings = cursor.fetchall()

    conn.close()
    return bookings




@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
# Define the registration form using Flask-WTF
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



# class BookingForm(FlaskForm):
#     place = RadioField('Place', choices=[('place1', 'Place 1'), ('place2', 'Place 2')], validators=[DataRequired()])
#     date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.now().date())
#     time = TimeField('Time', format='%H:%M', validators=[DataRequired()], default=datetime.now().time())
#     submit_booking = SubmitField('Book Slot')

from wtforms.fields import SelectField

class BookingForm(FlaskForm):
    place = RadioField('Place', choices=[('hanumakonda', 'Hanumakonda'), ('warangal', 'Warangal')], validators=[DataRequired()])
    from_date = DateField('From Date', format='%Y-%m-%d', validators=[DataRequired()])
    from_time = TimeField('From Time', format='%H:%M', validators=[DataRequired()])
    to_date = DateField('To Date', format='%Y-%m-%d', validators=[DataRequired()])
    to_time = TimeField('To Time', format='%H:%M', validators=[DataRequired()])
    slot_number = SelectField('Slot Number', choices=[(str(i), str(i)) for i in range(1, 7)], validators=[DataRequired()])
    submit_booking = SubmitField('Book Slot')

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     return render_template('home.html')

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         # Connect to the database
#         conn = sqlite3.connect('database.db')
#         cursor = conn.cursor()
        
#         # Fetch user data from the database
#         cursor.execute('SELECT * FROM User WHERE username=? AND password=?', (username, password))
#         user = cursor.fetchone()
        
#         conn.close()
        
#         if user:
#             # User authentication successful, redirect to dashboard or another page
#             flash('Login successful!', 'success')
#             # return redirect('/dashboard',username=username)
#             return redirect('/dashboard')
#         else:
#             flash('Invalid username or password. Please try again.', 'error')
    
#     return render_template('home.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Connect to the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Fetch user data from the database
        cursor.execute('SELECT * FROM User WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()    
        conn.close()
        if (username=='admin' and password == 'admin'):
            print("from if condition")
            return redirect(url_for('admin'))

        if user:
            # Store user data in session
            session['user_id'] = user[0]
            session['username'] = user[1]

            flash('Login successful!', 'success')
            return redirect('/dashboard')
        else:
            flash('Invalid username or password. Please try again.', 'error')
    
    return render_template('home.html')

# Route for handling user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    print("in registration form")
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        
        print(confirm_password)
        if username=="admin":
            flash('You cannot use USERNAME as ADMIN', 'error')
            return redirect('/register')

        # Check if the passwords match
        if password != confirm_password:
            print("password not match")
            flash('Passwords do not match', 'error')
            return redirect('/register')

        # Perform database operations here
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Insert user data into the database
            cursor.execute('INSERT INTO User (username, email, password,balance) VALUES (?, ?, ?,?)', (username, email, password,0))
            conn.commit()
            flash('Account created successfully! You can now log in.', 'success')
            conn.close()
            return redirect('/login')  # Redirect to login after successful registration
        except sqlite3.IntegrityError:
            flash('Username or email already exists. Please choose a different one.', 'error')
            conn.close()
            return redirect('/register')

    return render_template('register.html', form=form)


# @app.route('/admin', methods=['GET', 'POST'])
# def admin():
#     print("in admin")
#     return render_template('admin.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM User')
    users = cursor.fetchall()

    close_db(conn)
    return render_template('admin.html', users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        conn = get_db()
        cursor = conn.cursor()
        # Here, handle the login logic using SQLAlchemy or raw SQL queries
        cursor.execute('SELECT * FROM User WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()
        print("in login")
        print(user)
        close_db(conn)
        try:
            print(user[0])
        except:
            print("returned None")

        if (username=='admin' and password == 'admin'):
            print("from if condition")
            return redirect(url_for('admin'))
                
        if user:
            # User authentication successful, redirect to dashboard or another page
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/dashboard')
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect('/login')


# # Route to view a specific user's bookings
# @app.route('/user/<int:user_id>')
# def view_user_bookings(user_id):
#     conn = get_db()
#     cursor = conn.cursor()
    
#     # Fetch user details
#     cursor.execute('SELECT * FROM User WHERE id=?', (user_id,))
#     user = cursor.fetchone()
    
#     # Fetch user's order details
#     cursor.execute('SELECT * FROM booking_details WHERE user_id=?', (user_id,))
#     orders = cursor.fetchall()
    
#     close_db(conn)
    
#     return render_template('user_orders.html', user=user, orders=orders)

@app.route('/user/<int:user_id>')
def view_user_bookings(user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    # Fetch user details
    cursor.execute('SELECT * FROM User WHERE user_id=?', (user_id,))
    user = cursor.fetchone()
    
    # Fetch user's order details
    cursor.execute('SELECT * FROM booking_details WHERE user_id=?', (user_id,))
    orders = cursor.fetchall()
    
    close_db(conn)
    
    return render_template('user_orders.html', user=user, orders=orders)

# # Route to recharge a user
# @app.route('/recharge/<int:user_id>', methods=['POST'])
# def recharge_user(user_id):
#     recharge_amount = request.form['recharge_amount']

#     conn = get_db()
#     cursor = conn.cursor()

#     # Update the user's balance
#     cursor.execute('UPDATE User SET balance = ? WHERE user_id = ?', (recharge_amount, user_id))
#     conn.commit()
#     close_db(conn)

#     flash('User recharged successfully!', 'success')
#     return redirect(url_for('admin'))

@app.route('/recharge/<int:user_id>', methods=['POST'])
def recharge_user(user_id):
    recharge_amount = int(request.form['recharge_amount'])

    conn = get_db()
    cursor = conn.cursor()

    # Fetch the current recharge amount for the user
    cursor.execute('SELECT balance FROM User WHERE user_id = ?', (user_id,))
    current_recharge = cursor.fetchone()

    # Calculate the new total recharge amount
    if current_recharge:
        new_recharge = current_recharge[0] + recharge_amount
    else:
        new_recharge = recharge_amount

    # Update the user's recharge amount
    cursor.execute('UPDATE User SET balance = ? WHERE user_id = ?', (new_recharge, user_id))
    conn.commit()
    close_db(conn)

    flash('User recharged successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/book_slot/<int:user_id>', methods=['GET', 'POST'])
def book_slot(user_id):
    form = BookingForm()
    if form.validate_on_submit():
        place = form.place.data
        date = form.date.data
        time = form.time.data

        # Retrieve the user ID from the session
        user_id = session.get('user_id')

        if user_id:
            # Connect to the database
            conn = get_db()
            cursor = conn.cursor()

            # Insert into the database
            cursor.execute('INSERT INTO booking_details (user_id, place, date, time) VALUES (?, ?, ?, ?)',
                           (user_id, place, date, time))
            conn.commit()
            conn.close()

            return render_template('success.html')
        else:
            # Handle case where user is not logged in
            pass

    return render_template('book_slot.html', form=form)



# @app.route('/dashboard/', methods=['GET', 'POST'])
# def dashboard():
    
#     try:
#         form = BookingForm()
#         user_id = session.get('user_id')
        
#         if user_id:
#             # Connect to the database
#             conn = get_db()
#             cursor = conn.cursor()
            
#             # Fetch user's bookings
#             cursor.execute('SELECT * FROM booking_details WHERE user_id = ?', (user_id,))
#             try:
#                 bookings = cursor.fetchall()
#             except:
#                 print("no previous saved data")
#             #print(bookings)
#             if form.validate_on_submit():
#                 # place = form.place.data
#                 # date = form.date.data
#                 # time = form.time.data
#                 # username = session.get('username')

#                 # # Convert datetime object to string
#                 # datetime_str = datetime.combine(date, time).strftime('%Y-%m-%d %H:%M:%S')

#                 # try:
#                 #     # Insert into the database
#                 #     cursor.execute('INSERT INTO booking_details (user_id, username, place, datetime) VALUES (?, ?, ?, ?)',
#                 #                    (user_id, username, place, datetime_str))
#                 #     conn.commit()

#                 #     flash("Success in booking slot")
#                 #     return redirect('/dashboard')
#                 try:
#                     place = form.place.data
                    
#                     from_date = form.from_date.data
#                     from_time = form.from_time.data
#                     to_date = form.to_date.data
#                     to_time = form.to_time.data
                    
#                     slot_no=form.slot_number.data
#                     username = session.get('username')
                
#                     from_datetime = datetime.combine(from_date, from_time).strftime('%Y-%m-%d %H:%M:%S')
#                     to_datetime = datetime.combine(to_date, to_time).strftime('%Y-%m-%d %H:%M:%S')
#                 except:
#                     print("ok")

#                 try:
                    
                    
#                     cursor.execute('INSERT INTO booking_details (user_id, username, place, slot_no, from_datetime, to_datetime) VALUES (?, ?, ?, ?, ?, ?)',
#                                    (user_id, username, place, slot_no,from_datetime, to_datetime))
#                     conn.commit()

#                     flash("Success in booking slot")
#                     return redirect('/dashboard')                
                
#                 except sqlite3.IntegrityError as e:
#                     print(e)
#                     if "UNIQUE constraint failed: booking_details.datetime" in str(e):
#                         flash("You cannot book at the same time and place. Please choose a different date or time.", "error")
#                     else:
                        
#                         flash("Error at storing data", "error")
#                     return redirect('/dashboard')

#             conn.close()
#             return render_template('dashboard.html', form=form, bookings=bookings)

#         else:
#             flash("Please log in to book a slot.", "error")
#             return redirect('/login')

#     except Exception as e:
#         print("Error:", str(e))
#         flash("Error at storing data", "error")
#         flash("Please log in to book a slot.", "error")
#         return redirect('/login')

#     return render_template('dashboard.html', form=form)


@app.route('/dashboard/', methods=['GET', 'POST'])
def dashboard():
    try:
        form = BookingForm()
        user_id = session.get('user_id')
        balance=0
        print(balance)
        if user_id:
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM booking_details WHERE user_id = ?', (user_id,))
            try:
                bookings = cursor.fetchall()
            except:
                print("no previous saved data")
            

            
            ##new edit
                        # Get the current time
            current_time = datetime.utcnow()

            # Count the number of booked slots for the current time
            cursor.execute('SELECT slot_no FROM booking_details WHERE ? BETWEEN from_datetime AND to_datetime', (current_time.strftime('%Y-%m-%d %H:%M:%S'),))
            booked_slots = [slot[0] for slot in cursor.fetchall()]
            
            slot_numbers = [1,2,3,4,5,6]
            print("booked slots")
            print(booked_slots)



            if form.validate_on_submit():
                try:
                    place = form.place.data
                    from_date = form.from_date.data
                    from_time = form.from_time.data
                    to_date = form.to_date.data
                    to_time = form.to_time.data
                    slot_no = form.slot_number.data
                    username = session.get('username')
                
                    # Combine date and time to create local datetimes
                    local_from_datetime = datetime.combine(from_date, from_time)
                    local_to_datetime = datetime.combine(to_date, to_time)
                    
                    # Define the local timezone
                    # local_timezone = pytz.timezone('YOUR_LOCAL_TIMEZONE')  # Replace with your local timezone
                    local_timezone = pytz.timezone('Asia/Kolkata')

                    
                    # Localize the datetime objects
                    local_from_datetime = local_timezone.localize(local_from_datetime)
                    local_to_datetime = local_timezone.localize(local_to_datetime)
                    
                    # Convert local datetimes to UTC
                    utc_timezone = pytz.timezone('UTC')
                    from_datetime = local_from_datetime.astimezone(utc_timezone).strftime('%Y-%m-%d %H:%M:%S')
                    to_datetime = local_to_datetime.astimezone(utc_timezone).strftime('%Y-%m-%d %H:%M:%S')
                    print("slot_no:", slot_no)
                    print("booked_slots:", booked_slots)

                    cursor.execute('SELECT slot_no FROM booking_details WHERE ? BETWEEN from_datetime AND to_datetime OR ? BETWEEN from_datetime AND to_datetime',
                                (from_datetime, to_datetime))
                    form_booked_slots = [slot[0] for slot in cursor.fetchall()]

                    if int(slot_no) in form_booked_slots:
                        flash("Slot already booked. Please choose a different slot.", "error")
                        return redirect('/dashboard')


                except Exception as e:
                    print("Error:", str(e))

                try:
                    cursor.execute('INSERT INTO booking_details (user_id, username, place, slot_no, from_datetime, to_datetime) VALUES (?, ?, ?, ?, ?, ?)',
                                   (user_id, username, place, slot_no, from_datetime, to_datetime))
                    conn.commit()

                    flash("Success in booking slot")
                    return redirect('/dashboard')                
                
                except sqlite3.IntegrityError as e:
                    if "UNIQUE constraint failed: booking_details.datetime" in str(e):
                        flash("You cannot book at the same time and place. Please choose a different date or time.", "error")
                    else:
                        flash("Error at storing data", "error")
                    return redirect('/dashboard')
                

            conn.close()
            return render_template('dashboard.html', form=form, bookings=bookings, slot_numbers=slot_numbers, booked_slots=booked_slots,balance=balance)
            return render_template('dashboard.html', form=form, bookings=bookings)
        else:
            flash("Please log in to book a slot.", "error")
            return redirect('/login')

    except Exception as e:
        print("Error:", str(e))
        flash("Error at storing data", "error")
        flash("Please log in to book a slot.", "error")
        return redirect('/login')

    return render_template('dashboard.html', form=form)



@app.route('/get_data_for_arduino/<int:user_id>')
def get_data_for_arduino(user_id):
    print("got request")
    
    # # Check if the requested user ID exists or has access
    # if user_id == session.get('user_id'):
    #     # Fetch bookings for the requested user ID from the database
    #     bookings = fetch_bookings(user_id)  # Implement this function
    #     send_to_arduino("testing")
    #     # Prepare data frame
    # # Prepare data frame to send to Arduino
    #     data_frame = ""
    #     for booking in bookings:
    #         slot_number = booking[3]  # Assuming slot number is at index 3 in the tuple
    #         from_datetime = booking[4]  # Assuming from_datetime is at index 4
    #         to_datetime = booking[5]  # Assuming to_datetime is at index 5
    #         # Construct the data frame based on your Arduino's expected format
    #         data_frame += f"{slot_number},{from_datetime},{to_datetime};"

    #     # Send the data to Arduino
    #     send_to_arduino(data_frame)
    #     print(data_frame)

    #     return "Data sent to Arduino successfully!"
    # else:
    #     return "Unauthorized access", 403  # Forbidden status code if unauthorized

    return f"Received request from Arduino for user ID: {user_id}"

# @app.route('/trigger_function/<action>')
# def trigger_function(action):
#     # Perform actions based on received data
#     if action == '1':
#         conn = get_db()
#         cursor = conn.cursor()
            
#         # Fetch user's time stamp
#         cursor.execute('SELECT * FROM booking_details WHERE user_id = ? AND datetime("now") BETWEEN from_datetime AND to_datetime', (action,))

#         bookings = cursor.fetchall()
#         conn.close()
#         print(bookings)
#         print(len(bookings))
#         # if len(bookings) > 0:
#         #     slot_number = bookings[0][3]  # Accessing slot number at index 3 of the first row (assuming bookings[0] is the first row)
#         #     to_datetime = bookings[0][5]  # Accessing to_datetime at index 5 of the first row (assuming bookings[0] is the first row)
#         #     return f"Slot Number: {slot_number}, To Time: {to_datetime}"
#         # else :
#         #     return f"no bookings"

#         # Assuming to_datetime is in UTC as a string in the format '%Y-%m-%d %H:%M:%S'
#         if len(bookings) > 0:
#             slot_number = bookings[0][3]  # Accessing slot number at index 3 of the first row (assuming bookings[0] is the first row)
#             to_datetime_utc_str = bookings[0][5]

#             # Parse the UTC string to a datetime object
#             to_datetime_utc = datetime.strptime(to_datetime_utc_str, '%Y-%m-%d %H:%M:%S')

#             # Define the UTC and IST time zones
#             utc_timezone = pytz.timezone('UTC')
#             ist_timezone = pytz.timezone('Asia/Kolkata')  # India Standard Time (IST)

#             # Convert the UTC datetime to IST
#             to_datetime_ist = utc_timezone.localize(to_datetime_utc).astimezone(ist_timezone)

#             # Format the IST datetime as a string in the desired format
#             to_datetime_ist_str = to_datetime_ist.strftime('%Y-%m-%d %H:%M:%S')
#             print(to_datetime_ist_str)

#             return f"Slot No: {slot_number},Time:{to_datetime_ist_str}"
#         else :
#              return f"no bookings"

#     elif action == 'stop':
#         # Code to stop your function
#         print("stopped")
#         return "Function stopped"
#     else:
#         print("invalid")
#         return "Invalid action"



@app.route('/trigger_function/<action>')
def trigger_function(action):
    # Perform actions based on received data
    try:
        conn = get_db()
        cursor = conn.cursor()
            
        # Fetch user's time stamp
        cursor.execute('SELECT * FROM booking_details WHERE user_id = ? AND datetime("now") BETWEEN from_datetime AND to_datetime', (action,))

        bookings = cursor.fetchall()
        if len(bookings) > 0:
            user_id=bookings[0][0]
            slot_number = bookings[0][3]  # Accessing slot number at index 3 of the first row (assuming bookings[0] is the first row)
            to_datetime_utc_str = bookings[0][5]

            # Parse the UTC string to a datetime object
            to_datetime_utc = datetime.strptime(to_datetime_utc_str, '%Y-%m-%d %H:%M:%S')

            # Define the UTC and IST time zones
            utc_timezone = pytz.timezone('UTC')
            ist_timezone = pytz.timezone('Asia/Kolkata')  # India Standard Time (IST)

            # Convert the UTC datetime to IST
            to_datetime_ist = utc_timezone.localize(to_datetime_utc).astimezone(ist_timezone)

            # Format the IST datetime as a string in the desired format
            to_datetime_ist_str = to_datetime_ist.strftime('%Y-%m-%d %H:%M:%S')
            to_time_ist_str = to_datetime_ist.strftime('%H:%M:%S')
            print(to_datetime_ist_str)
            print(to_time_ist_str)

            return f"Uid:{user_id}  SlotNo {slot_number} ToTime:{to_time_ist_str}"
        else :
             return f"no bookings"
    except:
        pass



if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
    #app.run(host='192.168.100.2', port=5000, debug=True)



