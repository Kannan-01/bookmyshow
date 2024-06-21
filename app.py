import mysql.connector
from mysql.connector import Error
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
from random import randint
from datetime import date, datetime, timedelta

app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = 'uploads/'


@app.route('/')
def index():
    return render_template('index.html')


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


@app.route('/bookings')
def bookings():
    return render_template('bookings.html')


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
        schedules.time
    FROM 
        movies
    JOIN 
        schedules
    ON 
        movies.movie_id = schedules.movie_id;
    """
    movies = runQuery(query)
    return render_template('user.html', movies=movies)


@app.route('/select-seat', methods=['POST'])
def select_seat():
    row_label = request.form.get('row_label')
    row_id = request.form.get('row_id')
    seat_number = request.form.get('seat_number')
    print(row_label, row_id, seat_number)
    # Process the seat selection as needed

    return jsonify(status='success', message='Seat selected successfully')


@app.route('/reservation/<movieId>', methods=['GET', 'POST'])
def reservation(movieId):
    if request.method == 'POST':
        # Handle seat reservation
        seat_row = request.form.get('seat_row')
        seat_number = request.form.get('seat_number')
        reservation_date = request.form.get('reservation_date')
        query = "INSERT INTO reservations (movie_id, seat_row, seat_number, reservation_date) VALUES (%s, %s, %s, %s)"
        params = (movieId, seat_row, seat_number, reservation_date)
        runQuery(query, params)

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
        # Assuming seat[0] is seat_row and seat[1] is seat_number
        booked_seat_set.add((seat[0], seat[1]))

    seatrow = 10  # Number of rows (example value)
    seatcol = 18  # Number of columns (example value)
    rows = []
    for i in range(seatrow):
        row_data = {
            'row_id': f'row-{i}',
            # Generating row labels like A, B, C, ...
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
        movie_id = randint(0, 2147483646)

        # Handle file upload
        if 'poster' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['poster']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            poster_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            return jsonify({'error': 'Invalid file type'}), 400

        if movie_exists(movie_name):
            return jsonify({'error': 'Movie already exists in the database.'}), 400

        query = "INSERT INTO movies (movie_id, movie_name, length, language, format, genre, poster_path) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        params = (movie_id, movie_name, length,
                  language, format, genre, poster_path)
        runQuery(query, params)

        query = "SELECT * FROM movies WHERE movie_id = %s"
        params = (movie_id,)
        uploadData = runQuery(query, params)
        print(uploadData)
        return render_template('addmovie.html', uploadData=uploadData)

    return render_template('addmovie.html')

# Function to check if movie already exists


def schedule_exists(movie_id):
    query = "SELECT * FROM schedules WHERE movie_id = %s"
    params = (movie_id,)
    result = runQuery(query, params)
    return len(result) > 0

# schedule time for a movie


@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == 'POST':
        movie_id = request.form.get('movieid')
        time = request.form.get('time')

        if schedule_exists(movie_id):
            return jsonify({'error': 'Movie already exists in the database.'}), 400

        query = "INSERT INTO schedules (movie_id, time) VALUES (%s, %s)"
        params = (movie_id, time)
        runQuery(query, params)
        return jsonify({'message': 'Movie Hosted successfully!'})

    query = "SELECT * FROM movies"
    movies = runQuery(query)
    return render_template('schedule.html', movies=movies)


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
