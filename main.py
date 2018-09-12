from pytube import YouTube
import subprocess
from bs4 import BeautifulSoup
import requests
import os
import threading
import re


DOWNLOAD_PATH = os.path.expanduser("~") + "\\Music\\"
FFMPEG_PATH = "C:\\Users\\Jernej\\Documents\\Other\\ffmpeg\\bin\\ffmpeg.exe"

g_playlist_title = ""


def get_playlist_links(url):
    source_code = requests.get(url).text
    soup = BeautifulSoup(source_code, 'html.parser')

    playlist_title = soup.find("title").contents[0]
    playlist_title = re.sub(r'- YouTube$', "", playlist_title).strip()

    domain = 'https://www.youtube.com'
    playlist_links = []
    print("Playlist items:")
    i = 1
    for link in soup.find_all("a", {"dir": "ltr"}):
        href = link.get('href')
        if href.startswith('/watch?'):
            print("    " + str(i) + ". " + link.string.strip())
            playlist_links.append(domain + href)
            i += 1
    print("")
    return playlist_links, playlist_title


def download_playlist(uri):
    playlist, playlist_title = get_playlist_links(uri.strip())
    global g_playlist_title
    g_playlist_title = playlist_title
    if not os.path.exists(DOWNLOAD_PATH + playlist_title):
        print("Download directory does not exist, making one")
        os.makedirs(DOWNLOAD_PATH + playlist_title)
    howmany = input('End index (press Enter to download all): ')
    if howmany != "":
        playlist = playlist[:int(howmany)]
    threads = []
    for uri in playlist:
        t = threading.Thread(target=download_video, args=(uri, playlist_title))
        threads.append(t)
        t.start()


def download_video(uri, playlist_title):
    yt = YouTube(uri.strip())
    yt.register_on_complete_callback(extract_mp3)
    stream = yt.streams.get_by_itag(22)
    if stream is None:
        stream = yt.streams.get_by_itag(18)

    if os.path.isfile(DOWNLOAD_PATH + playlist_title + "\\" + stream.default_filename.rpartition(".")[0] + ".mp3"):
        print("Item \"{}\" already exists, skipping download".format(yt.title))
    else:
        print("Starting download: " + yt.title)
        stream.download()


def extract_mp3(stream, file_handle):
    input_name = file_handle.name
    output_name = DOWNLOAD_PATH + g_playlist_title + "\\" + stream.default_filename.rpartition(".")[0] + ".mp3"
    artist_title = stream.default_filename.rpartition(".")[0].split("-")
    artist = ""
    if len(artist_title) == 2:
        artist = artist_title[0]
        title = artist_title[1]
        artist = artist.strip()
    else:
        title = artist_title[0]

    title = title.split(" ft. ")[0]
    title = title.split(" ft ")[0]
    title = title.split(" feat ")[0]
    title = re.sub(r'\(.*\)', "", title)
    title = re.sub(r'\[.*\]', "", title)
    title = title.strip()

    print("Done downloading {0}".format(input_name.split("\\")[-1]))
    print("Extracting mp3 for {}".format(input_name.split("\\")[-1]))
    instruction = \
        "\"{ffmpeg}\" -loglevel panic -i \"{input}\" -vn -ar 44100 -ac 2 -ab 192k -f mp3 -metadata title=\"{title}\" -metadata artist=\"{artist}\" \"{output}\"".format(
            ffmpeg=FFMPEG_PATH,
            input=input_name,
            output=output_name,
            title=title,
            artist=artist)
    extraction = subprocess.Popen(instruction)
    extraction.wait()

    print("Done extracting {0}".format(format(input_name.split("\\")[-1])))
    print("")
    file_handle.close()
    try:
        os.remove(input_name)
    except Exception as e:
        print("{}".format(e))


def main():
    uri = input('Link: ')
    if uri == "":
        return
    if "playlist?" in uri:
        download_playlist(uri)
    else:
        if not os.path.exists(DOWNLOAD_PATH + "YT Downloader"):
            print("Download directory does not exist, making one")
            os.makedirs(DOWNLOAD_PATH + "YT Downloader")
            global g_playlist_title
            g_playlist_title = "YT Downloader"
        download_video(uri, "YT Downloader")


if __name__ == "__main__":
    main()
