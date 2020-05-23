import re
import urllib.request
import ssl
from bs4 import BeautifulSoup


def get_lyrics(artist, song_title):
    """get lyrics from artist name and song title"""
    artist = artist.lower()
    song_title = song_title.lower()
    # remove all except alphanumeric characters from artist and song_title
    artist = re.sub('[^A-Za-z0-9]+', "", artist)
    song_title = re.sub('[^A-Za-z0-9]+', "", song_title)
    if artist.startswith("the"):
        # remove starting 'the' from artist e.g. the who -> who
        artist = artist[3:]
    url = "http://azlyrics.com/lyrics/" + artist + "/" + song_title + ".html"

    try:
        gcontext = ssl.SSLContext()
        content = urllib.request.urlopen(url, context=gcontext).read()
        soup = BeautifulSoup(content, 'html.parser')
        lyrics = str(soup)
        # lyrics lies between up_partition and down_partition
        up_partition = '<!-- Usage of azlyrics.com content' \
                       ' by any third-party lyrics provider' \
                       ' is prohibited by our licensing agreement.' \
                       ' Sorry about that. -->'
        down_partition = '<!-- MxM banner -->'
        lyrics = lyrics.split(up_partition)[1]
        lyrics = lyrics.split(down_partition)[0]
        lyrics = lyrics.replace('<br>', '').replace('</br>', '')\
                       .replace('</div>', '').strip()
        lyrics = lyrics.strip('\n\n<br/><br/>').split('<br/>\n')
        lyrics = [lyric for lyric in lyrics if lyric]
        return lyrics
    except Exception as e:
        return "error"
