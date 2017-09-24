import requests
from bs4 import BeautifulSoup

_baseurl = "https://jog.fm/popular-workout-songs?page="


def get_page(page_number):
    url = _baseurl + str(page_number)
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
        else:
            title = ""

        image = songer.find_all("img", class_="song-artwork")
        if image:
            image= image[0]["src"]

        print(bpm, artist, title, image)


