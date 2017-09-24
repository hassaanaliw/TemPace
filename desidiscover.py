import random
import pylast
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from database_file import get_song

import requests
from bs4 import BeautifulSoup

_url = "https://jog.fm/popular-workout-songs?page="

Base = declarative_base()


class Song(Base):
    __tablename__ = 'Song'
    id = Column('id', Integer, primary_key=True)
    title = Column('title', String)
    artist = Column('artist', String)
    tid = Column('tid', String)
    uri = Column('uri', String)
    bpm = Column('bpm', String)
    image = Column('image', String)

    def __init__(self, title, artist, bpm, image):
        self.title = str(title)
        self.artist = str(artist)
        self.get_spotify_link()
        self.bpm = str(bpm)
        self.image = str(image)

    def get_spotify_link(self):
        query = str(self.artist) + " " + str(self.title)
        res = get_song(query)
        if res:
            (uri,tid) = res
            self.tid = tid
            self.uri = uri

    def __repr__(self):
        return "%s %s" % (self.title, self.artist)


engine = create_engine('sqlite:///songs.db')
Base.metadata.create_all(engine)

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


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
            image= image[0]["src"]

        song_object = Song(title,artist,bpm,image)
        print(song_object)
        session.add(song_object)


    session.commit()

