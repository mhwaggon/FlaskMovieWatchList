from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'thisisasecret'

db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    overview = db.Column(db.String(250))
    poster_path = db.Column(db.String(50))
    vote_average = db.Column(db.Float)
    release_date = db.Column(db.String(50))


def get_movie_data(movie):
    url = f'https://api.themoviedb.org/3/search/movie?api_key=INSERTAPIKEY&query={ movie }'
    r = requests.get(url).json()
    return r


@app.route('/')
def index_get():
    movies = Movie.query.all()

    movie_list = []

    for movie in movies:

        r = get_movie_data(movie.title)
        print(r)

        movieData = {
            'title': movie.title,
            'overview': r['results'][0]['overview'],
            'poster_path': r['results'][0]['poster_path'],
            'vote_average': r['results'][0]['vote_average'],
            'release_date': r['results'][0]['release_date'],
        }

        movie_list.append(movieData)

    return render_template('index.html', movie_list=movie_list)


@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    new_movie = request.form.get('movie') #Data stored after user enters in text box

    if new_movie:
        existing_movie = Movie.query.filter_by(title=new_movie).first()

        if not existing_movie:
            new_movie_data = get_movie_data(new_movie)

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


@app.route('/delete/<title>')
def delete_movie(title):
    movie = Movie.query.filter_by(title=title).first()
    db.session.delete(movie)
    db.session.commit()

    flash(f'Successfully deleted { movie.title }', 'success')
    return redirect(url_for('index_get'))


if __name__ == '__main__':
    app.run(debug=True)

