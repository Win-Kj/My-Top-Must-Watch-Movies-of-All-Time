from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
import os
import requests
from dotenv import load_dotenv
from wtforms.fields.numeric import FloatField

load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
url_search_movie = "https://api.themoviedb.org/3/search/movie"
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CREATE DB
class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///my_Top-movies.db"
db.init_app(app)


# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False,)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String, nullable=False)

# Wtforms class to create a quick form
class MyForm(FlaskForm):
    rating_updated = FloatField('Your rating out of 10 e.g 7.5', validators=[validators.optional(), validators.NumberRange(max=10)])
    review_updated = StringField('Your review', validators=[validators.optional()])
    submit = SubmitField('Done')

# Adding new movies form
class New_movie(FlaskForm):
    new_movie = StringField('Movie Title', validators=[validators.input_required()])
    submit = SubmitField('Add movie')


@app.route("/")
def home():
    first_result = db.session.execute(db.select(Movie).order_by(Movie.rating))
    all_movies_1 = first_result.scalars().all()

    for movie in all_movies_1:
        new_ranking = len(all_movies_1) - all_movies_1.index(movie)
        movie.ranking = new_ranking
    db.session.commit()

    result_2 = db.session.execute(db.select(Movie).order_by(Movie.rating))
    all_movies_2 = result_2.scalars().all()

    return render_template("index.html", movies=all_movies_2)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = New_movie()
    if form.validate_on_submit() and request.method == 'POST':
        new_movie_title = form.new_movie.data
        return redirect(url_for('select', title=new_movie_title))

    return render_template('add.html', form=form)


@app.route('/select', methods=['GET', 'POST'])
def select():
    new_movie_title = request.args.get('title')
    params = {
        "query": f'{new_movie_title}',
        "include_adult": "false",
        "language": "en-US",
        "page": 1
    }
    response = requests.get(url_search_movie, headers=headers, params=params)
    data = response.json()['results']
    return render_template('select.html', data=data)


@app.route('/find')
def find_movie_details():
    id = request.args.get('id')
    url_movie_detail = f"https://api.themoviedb.org/3/movie/{id}"
    params = {
        'movie_id':id,
        'language':'en-US'
    }
    response = requests.get(url_movie_detail, headers=headers, params=params)
    data = response.json()
    with app.app_context():
        new_movie = Movie(
            title=data['original_title'],
            year=data['release_date'].split('-')[0],
            description=data['overview'],
            rating=0,
            ranking=0,
            review="None",
            img_url=f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
        )
        db.session.add(new_movie)
        db.session.commit()
        new_movie_id = (db.session.execute(db.select(Movie).where(Movie.title == data['original_title'])).scalar()).id
    return redirect(url_for('edit', id=new_movie_id))


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    form = MyForm()
    id = request.args.get('id')
    if form.validate_on_submit():
        with app.app_context():
            movie_to_update = db.get_or_404(Movie, id)
            movie_to_update.rating = form.rating_updated.data
            movie_to_update.review = form.review_updated.data
            db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form)

@app.route('/delete')
def delete():
    id = request.args.get('id')
    movie_to_delete = db.get_or_404(Movie, id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)

#################### Line 150 "I am just adding it to show my satisfaction😂"