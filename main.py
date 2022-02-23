import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import data
import os
import time

session = requests.session()
session_id = ""
content = ""
try_times = 1

fake_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}


def login():
    login_r = session.post("https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/bookmark.php", data=data.login_data,
                           headers=fake_headers)

    if os.getenv("DEBUG"):
        print("login_r.history: " + str(login_r.history))  # Should be 302.
        print("login_r.url:")  # The URL contents session ID.
        print(login_r.url)

    # Reference: https://stackoverflow.com/questions/5074803/retrieving-parameters-from-a-url
    if not login_r.history:
        print("Login failed: Please check your account or your password.")
        quit(1)

    ssid = parse_qs(urlparse(login_r.url).query)["session_id"][0]
    if os.getenv("DEBUG"):
        print("login_r.url: " + login_r.url)
        print("urlparse: " + str(urlparse(login_r.url)))
        print("query: " + str(urlparse(login_r.url).query))
        print("parse_qs: " + str(parse_qs(urlparse(login_r.url).query)))
        print("ssid: " + ssid)

    login_r.encoding = "utf-8"
    user = str(BeautifulSoup(login_r.text, "html.parser").select("TD")[0].get_text()).split(' ')[0]
    if os.getenv("DEBUG"):
        print("Login as " + user)
    return ssid


def choose(ssid):
    # c = session.get(f"https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Add_Course00.cgi?session_id={ssid}", headers=fake_headers)  # choose
    # print(c.content.decode("utf-8"))

    data.choose["session_id"] = ssid
    c2 = session.post("https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Add_Course01.cgi", data=data.choose, headers=fake_headers)
    return c2.content.decode("utf-8")


def check(choose_content):
    soup = BeautifulSoup(choose_content, "html.parser")
    chk_box = soup.select(data.value)  # CSS Selector
    if len(chk_box) == 0:
        print("already selected!")
        exit(0)
    chk_box = chk_box[0]
    if os.getenv("DEBUG"):
        print("Course Information:")
        print("Course: " + chk_box.parent.parent.select("th")[3].get_text())
        print("Class: " + chk_box.parent.parent.select("th")[5].get_text())
        print("Professor: " + chk_box.parent.parent.select("th")[4].get_text())
    l = int(chk_box.parent.parent.select("th")[2].get_text())  # left
    return l


def select(ssid):
    data.select["session_id"] = ssid
    r = session.post("https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Add_Course01.cgi", data=data.select, headers=fake_headers)
    # print(r.content.decode("utf-8"))
    print(f"\nTry {try_times} times.")
    print("Success.")
    return True


while True:
    try:
        session_id = login()
        success = False
        for i in range(500):
            content = choose(session_id)
            left = check(content)
            if left > 0:
                success = select(session_id)
                break
            else:
                try_times += 1
                print(f"\rTry {try_times} times.", flush=True, end="")
                # time.sleep(0.1)
                continue
        if success:
            break
    except Exception as e:
        print("something went wrong!", e)
        continue
