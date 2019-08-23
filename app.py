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


# Database 
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    overview = db.Column(db.String(250))
    poster_path = db.Column(db.String(50))
    vote_average = db.Column(db.Float)
    release_date = db.Column(db.String(50))

#Putting togeather API to make request 'r' and return 'r'
def get_movie_data(movie):
    url = f'https://api.themoviedb.org/3/search/movie?api_key={ api_key }&query={ movie }'
    r = requests.get(url).json()
    return r


@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    #Data stored after user enters in text box on front end
    new_movie = request.form.get('movie') #
   
#Logic to make sure the movie is not already in the watchlist
    if new_movie:
        existing_movie = Movie.query.filter_by(title=new_movie).first()

        if not existing_movie:
            new_movie_data = get_movie_data(new_movie)
            #make sure movie that you searched exists/returned results
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

    for movie in movies:

        r = get_movie_data(movie.title)

        moviedata = {
            'title': movie.title,
            'overview': r['results'][0]['overview'],
            'poster_path': r['results'][0]['poster_path'],
            'vote_average': r['results'][0]['vote_average'],
            'release_date': r['results'][0]['release_date'],
        }

        movie_list.append(moviedata)

    return render_template('index.html', movie_list=movie_list)


@app.route('/delete/<title>')
def delete_movie(title):
    #Delete movie from the database
    movie = Movie.query.filter_by(title=title).first()
    db.session.delete(movie)
    db.session.commit()

    flash(f'Successfully deleted { movie.title }', 'success')
    return redirect(url_for('index_get'))


if __name__ == '__main__':
    app.run()


