from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import requests
import os


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db = SQLAlchemy(app)

api_key = os.environ.get('API_KEY')


# Creating our database model
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    overview = db.Column(db.String(250))
    poster_path = db.Column(db.String(50))
    vote_average = db.Column(db.Float)
    release_date = db.Column(db.String(50))
    movie_id = db.Column(db.Integer)


# Getting our original searched movie through API request
def get_movie_data(movie):
    url = f'https://api.themoviedb.org/3/search/movie?api_key={ api_key }&query={ movie }'
    r = requests.get(url).json()
    return r


# Getting recommended movie suggestions through api request
def get_recommended_movie(movieid):
    url = f'https://api.themoviedb.org/3/movie/{ movieid }/recommendations'
    rec = requests.get(url).json()
    return rec


@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    # Data stored in new_movie after user enters in text box on front end
    new_movie = request.form.get('movie')

    # Logic to make sure the movie doesn't already exist
    if new_movie:
        existing_movie = Movie.query.filter_by(title=new_movie).first()

        if not existing_movie:
            new_movie_data = get_movie_data(new_movie)

            # make sure our api call is returning results
            if new_movie_data['total_results'] != 0:
                new_movie_obj = Movie(title=new_movie)

                db.session.add(new_movie_obj)
                db.session.commit()
            else:
                err_msg = 'Search Returned No Results'
        else:
            err_msg = 'Movie Already Added'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('Movie Added')

    return redirect(url_for('index_get'))


@app.route('/')
def index_get():
    movies = Movie.query.all()

    movie_list = []
    rec_list = []

    # iterating through our database movies
    for movie in movies:

        # storing our api requests to r / rec
        r = get_movie_data(movie.title)

        # storing our api call data in a dictionary
        moviedata = {
            'movie_id': r['results'][0]['id'],
            'title': movie.title,
            'overview': r['results'][0]['overview'],
            'poster_path': r['results'][0]['poster_path'],
            'vote_average': r['results'][0]['vote_average'],
            'release_date': r['results'][0]['release_date'],
        }

        rec = get_recommended_movie(moviedata['movie_id'])
        rec_movie_data = {
            'title': rec['results'][0]['title'],
            'poster_path': rec['results'][0]['poster_path']
        }

        movie_list.append(moviedata)
        rec_list.append(rec_movie_data)

    return render_template('Index.html', movie_list=movie_list)


@app.route('/delete/<title>')
def delete_movie(title):
    movie = Movie.query.filter_by(title=title).first()
    db.session.delete(movie)
    db.session.commit()

    flash(f'Successfully deleted { movie.title }', 'success')
    return redirect(url_for('index_get'))


if __name__ == '__main__':
    app.run()


