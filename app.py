import mysql.connector
from mysql.connector import Error
from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
from random import randint
from datetime import date ,datetime

app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = 'uploads/'

# root page
@app.route('/')
def index():
    return render_template('index.html')

# file uploading API endpoint
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

# login function
@app.route('/', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == 'admin' and password == 'admin':
        return redirect(url_for('admin'))
    elif username == 'user' and password == 'user':
        return redirect(url_for('user'))
    else:
        return render_template('index.html', login_failed=True)

# Ticket Confirmation Page
@app.route('/booking')
def orders():
    return render_template('booking.html')

# my bookings page
@app.route('/orders')
def bookings():
    # Delete expired reservations
    delete_query = """
    DELETE FROM reservations
    WHERE reservation_date < CURDATE();
    """
    # Execute the delete query
    runQuery(delete_query)
    today_date = datetime.now().date().isoformat()
    
    # show remaing reservations
    query = """
    SELECT
        r.id AS reservation_id,
        r.seat_row,
        r.seat_number,
        r.reservation_date,
        m.movie_id,
        m.movie_name,
        m.length,
        m.language,
        m.format,
        m.genre,
        m.poster_path,
        s.time AS schedule_time
    FROM
        reservations r
    JOIN
        movies m ON r.movie_id = m.movie_id
    JOIN
        schedules s ON r.movie_id = s.movie_id
    WHERE
        r.reservation_date >= '{}'
    ORDER BY
        r.reservation_date ASC;
    """.format(today_date)

    bookings = runQuery(query)
    return render_template('orders.html', bookings=bookings)

# schedule delete API end point
@app.route('/delete_schedule', methods=['POST'])
def delete_schedule():
    movie_id = request.form['movie_id']
    query = "DELETE FROM schedules WHERE movie_id = %s;"
    runQuery(query, (movie_id,))
    query = """
SELECT 
        movies.movie_id,
        movies.movie_name,
        movies.length,
        movies.language,
        movies.format,
        movies.genre,
        movies.poster_path,
        schedules.time
    FROM 
        movies
    JOIN 
        schedules
    ON 
        movies.movie_id = schedules.movie_id;
    """
    movies = runQuery(query)
    return render_template('admin.html', movies=movies)

# Admin page
@app.route('/admin')
def admin():
    query = """
SELECT 
        movies.movie_id,
        movies.movie_name,
        movies.length,
        movies.language,
        movies.format,
        movies.genre,
        movies.poster_path,
        schedules.time
    FROM 
        movies
    JOIN 
        schedules
    ON 
        movies.movie_id = schedules.movie_id;
    """
    movies = runQuery(query)
    return render_template('admin.html', movies=movies)

# user page
@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        movieid = request.form.get('movieid')
        if movieid:
            return redirect(url_for('reservation', movieId=movieid))
    query = """
    SELECT 
        movies.movie_id,
        movies.movie_name,
        movies.length,
        movies.language,
        movies.format,
        movies.genre,
        movies.poster_path,
        schedules.time
    FROM 
        movies
    JOIN 
        schedules
    ON 
        movies.movie_id = schedules.movie_id;
    """
    movies = runQuery(query)
    print(movies)
    return render_template('user.html', movies=movies)

# Seat booking / Reservation page
@app.route('/reservation/<movieId>', methods=['GET', 'POST'])
def reservation(movieId):
    if request.method == 'POST':
        # Handle seat reservation
        seat_row = request.form.get('seat_row')
        seat_number = request.form.get('seat_number')
        reservation_date = request.form.get('reservation_date')
        
        # Insert reservation into database
        query = "INSERT INTO reservations (movie_id, seat_row, seat_number, reservation_date) VALUES (%s, %s, %s, %s)"
        params = (movieId, seat_row, seat_number, reservation_date)
        runQuery(query, params)
        
        # Fetch schedule details of a movie
        query = "SELECT time FROM schedules WHERE movie_id=%s"
        params = (movieId,)
        timedata = runQuery(query, params)
        timedelta_obj = timedata[0][0]
        total_seconds = timedelta_obj.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        time_string = f"{hours:02}:{minutes:02}"
        
        # fetch all details of a particular movie
        query = "SELECT * FROM movies WHERE movie_id=%s"
        params = (movieId,)
        moviedata = runQuery(query, params)
        booking = [movieId, seat_row, seat_number,
                   reservation_date, time_string]
        return render_template('booking.html', booking=booking, moviedata=moviedata)

    # Fetch movie and schedule details
    query = """
        SELECT movies.*, schedules.time
        FROM movies
        JOIN schedules ON movies.movie_id = schedules.movie_id
        WHERE movies.movie_id = %s;
    """
    params = (movieId,)
    details = runQuery(query, params)
    gettime = details[0][7] if len(details[0]) > 7 else ""

    # Fetch booked seats for a specific date
    reservation_date = request.args.get(
        'reservation_date', date.today().strftime('%Y-%m-%d'))
    query = "SELECT seat_row, seat_number FROM reservations WHERE movie_id = %s AND reservation_date = %s"
    booked_seats = runQuery(query, (movieId, reservation_date))

    # Create a set of booked seats
    booked_seat_set = set()
    for seat in booked_seats:
        booked_seat_set.add((seat[0], seat[1]))

    seatrow = 10
    seatcol = 18
    rows = []
    for i in range(seatrow):
        row_data = {
            'row_id': f'row-{i}',
            'row_label': chr(65 + i),
            'seats': []
        }
        for j in range(seatcol):
            seat = {
                'number': j + 1,
                'booked': (chr(65 + i), j + 1) in booked_seat_set
            }
            row_data['seats'].append(seat)
        rows.append(row_data)

    return render_template('reservation.html', rows=rows, details=details, time=gettime, reservation_date=reservation_date)

# Function to check if movie already exists
def movie_exists(movie_name):
    query = "SELECT * FROM movies WHERE movie_name = %s"
    params = (movie_name,)
    result = runQuery(query, params)
    return len(result) > 0

# for adding a movie
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        movie_name = request.form.get('moviename')
        length = request.form.get('length')
        language = request.form.get('lang')
        format = request.form.get('format')
        genre = request.form.get('genre')
        # Use request.files.get to safely get file object
        file = request.files.get('poster')

        # Check if any field is empty or not selected
        if not movie_name or not length or not language or language == 'Select a Language' or not format or format == 'Select a format' or not genre or not (file and file.filename):
            return render_template('addmovie.html', error='Please fill out all fields before submitting the form.')

        movie_id = randint(0, 2147483646)

        # Handle file upload
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            poster_path = file_path  # Use the saved file path for the database
        else:
            return jsonify({'error': 'Invalid file type or no file selected'}), 400

        if movie_exists(movie_name):
            return jsonify({'error': 'Movie already exists in the database.'}), 400

        query = "INSERT INTO movies (movie_id, movie_name, length, language, format, genre, poster_path) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        params = (movie_id, movie_name, length,
                  language, format, genre, poster_path)
        runQuery(query, params)

        query = "SELECT * FROM `movies` WHERE movie_id=%s"
        params = (movie_id,)
        success = runQuery(query, params)

        return render_template('success.html', success=success)

    return render_template('addmovie.html')

# Function to check if movie already schedules
def schedule_exists(movie_id):
    query = "SELECT * FROM schedules WHERE movie_id = %s"
    params = (movie_id,)
    result = runQuery(query, params)
    return len(result) > 0

# schedule time for a movie
@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    message = None
    error = None 

    if request.method == 'POST':
        movie_id = request.form.get('movieid')
        time = request.form.get('time')

        if schedule_exists(movie_id):
            error = 'Movie already hosted.'
        else:
            query = "INSERT INTO schedules (movie_id, time) VALUES (%s, %s)"
            params = (movie_id, time)
            runQuery(query, params)
            message = 'Movie hosted successfully!'

    # Update the query to fetch movies that are not scheduled
    query = """
            SELECT * 
            FROM movies 
            WHERE movie_id NOT IN (
                SELECT movie_id FROM schedules
            )
            """
    movies = runQuery(query)
    print(movies)
    return render_template('schedule.html', movies=movies, message=message, error=error)


# Movie added succesfully page
@app.route('/success', methods=['GET'])
def success():
    return render_template('success.html')

# sql connections
def runQuery(query, params=None):
    try:
        db = mysql.connector.connect(
            host='localhost',
            database='moviedatabase',
            user='root',
            password=''
        )

        if db.is_connected():
            print("Connected to MySQL, running query: ", query)
            cursor = db.cursor(buffered=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            db.commit()
            res = None
            try:
                res = cursor.fetchall()
            except Exception as e:
                print("Query returned nothing, ", e)
                return []
            return res

    except Exception as e:
        print(e)
        return e

    finally:
        db.close()

    print("Couldn't connect to MySQL Database")
    return None


if __name__ == "__main__":
    app.run(host='0.0.0.0')
