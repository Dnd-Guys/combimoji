import requests
import os


DATES = ["20201001", "20210218", "20210521", "20210831"]


def download_image(date, code1, code2):
    url = ''.join(["https://www.gstatic.com/android/keyboard/emojikitchen/",
                   date, "/u", code1, "/u", code1, "_u", code2, ".png"])
    img_title = '/'.join([os.getcwd(), 'images', url.split('/')[-1]])

    if os.path.exists(img_title):  # return cached image
        return img_title

    try:  # try to connect
        img = requests.get(url)
        if not img.text.startswith('<!DOCTYPE html>'):  # check if url is an image link (won't have html in it)
            with open(img_title, 'wb') as handler:
                handler.write(img.content)
                return img_title
    except requests.ConnectionError:
        pass
    return None


def download_emoji_combo(emojis):
    codes = list(map(lambda x: str(x.encode('unicode-escape'))[-6:-1], emojis))
    for date in DATES:
        # try both ways
        img1 = download_image(date, codes[0], codes[1])
        img2 = download_image(date, codes[1], codes[0])
        if img1:
            return img1
        if img2:
            return img2
    return None
