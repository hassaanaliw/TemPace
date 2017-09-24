import os
import random

import requests
from bs4 import BeautifulSoup
from flask import Flask, g, jsonify, render_template, request, json
from flask_sqlalchemy import SQLAlchemy
from process_csv import get_chain_readings

from database_file import get_song

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'd290909uy9gY6g7v66v'

if 'DYNO' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///songs.db'
    app.config['DEBUG'] = True
app.config['DEBUG'] = True

db = SQLAlchemy(app)

_url = "https://jog.fm/popular-workout-songs?page="


class Songs(db.Model):
    __tablename__ = 'Songs'
    id = db.Column('id', db.Integer, primary_key=True)
    title = db.Column('title', db.String)
    artist = db.Column('artist', db.String)
    tid = db.Column('tid', db.String)
    uri = db.Column('uri', db.String)
    bpm = db.Column('bpm', db.Integer)
    image = db.Column('image', db.String)

    def __init__(self, title, artist, bpm, image):
        self.title = str(title)
        self.artist = str(artist)
        self.get_spotify_link()
        try:
            self.bpm = int(bpm)
        except:
            self.bpm = 0
        self.image = str(image)

    def get_spotify_link(self):
        query = str(self.artist) + " " + str(self.title)
        res = get_song(query)
        if res:
            (uri, tid) = res
            self.tid = tid
            self.uri = uri

    def __repr__(self):
        return "%s %s" % (self.title, self.artist)


class Data(db.Model):
    __tablename__ = 'Data'
    id = db.Column('id', db.Integer, primary_key=True)
    json_data = db.Column('json_data', db.String)
    unique = db.Column('unique', db.String)

    def __init__(self, json_data):
        self.json_data = json_data

    def __repr__(self):
        return "%d" % (self.id)


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")


@app.route('/choose', methods=["GET", "POST"])
def choose():
    if request.method == "GET":
        return render_template("choose.html")
    data = request.files['f']
    csv_data = get_chain_readings(data)
    final_data = []

    for row in csv_data:
        sums = 0
        start_date = row[0]['start']
        end_date = row[-1]['end']
        duration = end_date - start_date
        for r in row:
            sums += (float(r["distance"]))
        store = json.dumps({
            'data': row,
            'start_date': start_date,
            'end_date': end_date,
            'distance': sums,
            'duration': duration
        }, indent=4, sort_keys=True, default=str)
        new_store = Data(store)
        db.session.add(new_store)
        db.session.flush()

        final_data.append(
            {
                'data': row,
                'id': new_store.id,
                'start_date': start_date,
                'end_date': end_date,
                'distance': sums,
                'duration': duration
            }
        )
    print(final_data)
    db.session.commit()

    return render_template("choose.html", final_data=final_data)


def get_page(page_number):
    url = _url + str(page_number)
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')

    songs_list = soup.find_all("div", class_="song list-item")
    for songer in songs_list:
        bpm = songer.find_all("div", class_="side-box fixed")
        if bpm:
            bpm = bpm[0].select('a')[-1].text

        artist = songer.find_all("div", class_="top")
        if artist:
            artist = artist[0].select('a')[0].text

        title = songer.find_all("div", class_="title")
        if title:
            title = title[0].select('a')[0].text

        image = songer.find_all("img", class_="song-artwork")
        if image:
            image = image[0]["src"]

        song_object = Songs(title, artist, bpm, image)
        print(song_object)
        db.session.add(song_object)

    db.session.commit()


def get_songs():
    songs_lists = Songs.query.all()
    json = []
    for s in songs_lists:
        json.append({
            'name': s.title,
            'artist': s.artist,
            'bpm': s.bpm,
            'uri': s.uri,
            'tid': s.tid,
            'image': s.image
        })


@app.route("/analyze/<id>")
def analyze(id):
    data = json.loads(Data.query.get(id).json_data)



    first = data["data"][0]
    first_speed = float(first["distance"]) * (1.66666667)
    minimum = get_bpm_min_speed(first_speed * 2)

    first_song = Songs.query.filter(Songs.bpm < (minimum + 20)).all()
    first_song = random.sample(set(first_song), 2)

    last = data["data"][-1]
    last_speed = float(last["distance"]) * (1.66667777)
    minimum = get_bpm_min_speed(last_speed * 3)


    last_song = Songs.query.filter(Songs.bpm < (minimum + 20)).all()
    last_song = random.sample(set(last_song), 2)


    middle_songs = []

    middle_items = data["data"][1:-1]
    for item in middle_items:
        speed = float(item["distance"]) * (1.66666667)
        minimum = get_bpm_min_speed(speed * 5)
        if minimum == 80:
            minimum = 100
        middle_song = Songs.query.filter(Songs.bpm < (minimum + 20)).all()
        middle_song = random.choice(middle_song)
        middle_songs.append(middle_song)

    return render_template("analyze.html", data=data,first_song=first_song, last_song=last_song, middle_songs = middle_songs)


def get_bpm_min_speed(speed):
    if speed < 2.23:
        return 80
    elif (speed > 2.23) and (speed < 2.43):
        return 80
    elif (speed > 2.43) and (speed < 2.68):
        return 100
    elif (speed > 2.68) and (speed < 2.98):
        return 120
    elif (speed > 2.98) and (speed < 3.35):
        return 140
    elif (speed > 3.35) and (speed < 3.83):
        return 160
    elif (speed > 3.83) and (speed < 4.47):
        return 180
    else:
        return 180




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
