import mysql.connector
from mysql.connector import Error
from flask import Flask, request, jsonify, render_template ,redirect ,url_for
from random import randint

app = Flask(__name__)
app.debug=True

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


@app.route('/user',methods=['GET', 'POST'])
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

@app.route('/reservation/<movieId>')
def reservation(movieId):
    seatrow = 10  # Number of rows (example value)
    seatcol = 18  # Number of columns (example value)
    rows = []

    for i in range(seatrow):
        row_data = {
            'row_id': f'row-{i}',
            'row_label': chr(65 + i),  # Generating row labels like A, B, C, ...
            'seats': []
        }
        for j in range(seatcol):
            row_data['seats'].append(j + 1)
        rows.append(row_data)
    # Process reservation logic if needed
    print(movieId)
    return render_template('reservation.html',rows=rows)

# Function to check if movie already exists
def movie_exists(movie_name):
    query = "SELECT * FROM movies WHERE movie_name = %s"
    params = (movie_name,)
    result = runQuery(query, params)
    return len(result) > 0

# for adding a movie
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        movie_name = request.form.get('moviename')
        length = request.form.get('length')
        language = request.form.get('lang')
        format = request.form.get('format')
        genre = request.form.get('genre')
        movie_id = randint(0, 2147483646)
        
        if movie_exists(movie_name):
            return jsonify({'error': 'Movie already exists in the database.'}), 400
        
        query = "INSERT INTO movies (movie_id, movie_name, length, language, format, genre) VALUES (%s, %s, %s, %s, %s, %s)"
        params = (movie_id, movie_name, length, language, format, genre)
        runQuery(query, params)
        return jsonify({'message': 'Movie added successfully!'})

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
    return render_template('schedule.html',movies=movies)


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
    

	