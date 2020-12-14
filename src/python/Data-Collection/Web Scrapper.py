"""

Author: Arthur wesley, Gregory Ghiroli

https://github.com/ihabunek/twitch-dl/blob/master/twitchdl/download.py

"""

import m3u8
import requests
import re

import cv2

from src.python import constants

from twitchdl import twitch
from twitchdl import download

from twitchdl.commands import _parse_playlists, _get_playlist_by_name, _get_vod_paths


def get_base_url(video_id, access_token=None):
    """

    generates the URL of a video with a given ID

    :param access_token: access token for the video
    :param video_id: ID of the video
    :return: generated URL
    """

    if access_token is None:
        access_token = twitch.get_access_token(video_id)

    playlists_m3u8 = twitch.get_playlists(video_id, access_token)
    playlists = list(_parse_playlists(playlists_m3u8))
    playlist_uri = _get_playlist_by_name(playlists, constants.quality)

    return re.sub("/[^/]+$", "/", playlist_uri)


def get_vods(video_id, access_token=None):
    """

    generates a list of all the vods for the video

    :param access_token: access token for the video
    :param video_id: ID of the video
    :return: list of vods the video has
    """

    start = None
    end = None

    if access_token is None:
        access_token = twitch.get_access_token(video_id)

    playlists_m3u8 = twitch.get_playlists(video_id, access_token)
    playlists = list(_parse_playlists(playlists_m3u8))
    playlist_uri = _get_playlist_by_name(playlists, constants.quality)

    response = requests.get(playlist_uri)
    response.raise_for_status()
    playlist = m3u8.loads(response.text)

    return _get_vod_paths(playlist, start, end)


def get_video(url):
    """

    gets the video from a url

    :param url:
    :return: size of the video in bytes
    """

    response = requests.get(url, stream=True, timeout=download.CONNECT_TIMEOUT)

    size = 0

    with open("test.ts", "wb+") as target:

        for chunk in response.iter_content(chunk_size=download.CHUNK_SIZE):
            target.write(chunk)
            size += len(chunk)

    return size


def get_still_frame(url, output_file):
    """

    get a still frame from a video url

    :param output_file: output file
    :param url: URL to the video
    :return: None (saves still frame
    """

    vidObj = cv2.VideoCapture(url)

    success, image = vidObj.read()
    cv2.imwrite(output_file, image)


def get_training_data(video_id, sampling_rate=constants.sampling_rate):
    """

    generates a set of images from a video ID

    :param video_id: ID of the video
    :param sampling_rate: number of items to skip over
    :return: None
    """

    access_token = twitch.get_access_token(video_id)

    base_url = get_base_url(video_id, access_token)
    vods = get_vods(video_id, access_token)

    for i, vod in enumerate(vods):

        # only take 1 in ten frames
        if i % sampling_rate == 0:
            get_still_frame(base_url + vod, "Data/images/" + video_id + "-" + str(i) + ".jpg")


def main():
    """

    main method

    :return:
    """

    IDs = ["832831965", "826807014", "829611887", "834868121"]

    for ID in IDs:
        get_training_data(ID)


if __name__ == "__main__":
    main()
