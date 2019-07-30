from flask import Flask, render_template, request
import requests
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    overview = db.Column(db.String(250))
    poster_path = db.Column(db.String(50))
    vote_average = db.Column(db.Float)
    release_date = db.Column(db.String(50))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_movie = request.form.get('movie') #Data stored after user enters in text box

        if new_movie:
            new_movie_obj = Movie(title=new_movie)
            db.session.add(new_movie_obj)
            db.session.commit()

    movies = Movie.query.all()

    url = 'https://api.themoviedb.org/3/search/movie?api_key=24ede328d19cb1ddaad7df578750d0f3&query={}'

    movie_list = []

    for movie in movies:

        r = requests.get(url.format(movie.title)).json()

        movieData = {
            'title': movie.title,
            'overview': r['results'][0]['overview'],
            'poster_path': r['results'][0]['poster_path'],
            'vote_average': r['results'][0]['vote_average'],
            'release_date': r['results'][0]['release_date'],
        }

        movie_list.append(movieData)

    return render_template('Movies.html', movie_list=movie_list)




if __name__ == '__main__':
    app.run(debug=True)
