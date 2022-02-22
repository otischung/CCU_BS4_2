import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import data
import time

session = requests.session()
session_id = ""
content = ""
try_times = 1

fake_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}


def login():
    login_r = session.post("https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/bookmark.php", data=data.login_data, headers=fake_headers)

    # print(login_r.history)  # 302
    # print(login_r.url)  # The URL contents session ID.

    # Reference: https://stackoverflow.com/questions/5074803/retrieving-parameters-from-a-url
    if not login_r.history:
        print("Login failed: Please check your account or your password.")
        quit(1)
    ssid = parse_qs(urlparse(login_r.url).query)["session_id"][0]
    return ssid


def choose(ssid):
    # c = session.get(f"https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Add_Course00.cgi?session_id={ssid}", headers=fake_headers)  # choose
    # print(c.content.decode("utf-8"))

    data.choose["session_id"] = ssid
    c2 = session.post("https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Add_Course01.cgi", data=data.choose, headers=fake_headers)
    # print(c2.content.decode("utf-8"))
    # input()
    return c2.content.decode("utf-8")


def check(choose_content):
    soup = BeautifulSoup(choose_content, "html.parser")
    chk_box = soup.select(data.value)  # CSS Selector
    if len(chk_box) == 0:
        print("already selected!")
        exit(0)
    chk_box = chk_box[0]
    l = int(chk_box.parent.parent.select("th")[2].get_text())  # left
    return l


def select(ssid):
    data.select["session_id"] = ssid
    r = session.post("https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Add_Course01.cgi", data=data.select, headers=fake_headers)
    print(r.content.decode("utf-8"))
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
