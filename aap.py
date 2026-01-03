#!/usr/bin/env python3
# ALL-IN-ONE FACEBOOK MESSENGER WEB BOT
# Created for: Alex
# Mode: Flask Web + Selenium (Single File)

import os
import time
import threading
from datetime import datetime

from flask import Flask, request, render_template_string

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ================= FLASK APP =================

app = Flask(__name__)

# ================= BOT CLASS =================

class FacebookMessenger:
    def __init__(self, cookie, uid, msg_file, haters, speed):
        self.cookie = cookie
        self.uid = uid
        self.msg_file = msg_file
        self.haters = haters
        self.speed = speed
        self.driver = None
        self.wait = None
        self.messages = []

    def find_firefox(self):
        paths = [
            "/data/data/com.termux/files/usr/bin/firefox",
            "firefox"
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        return "firefox"

    def find_geckodriver(self):
        paths = [
            "/data/data/com.termux/files/usr/bin/geckodriver",
            "geckodriver"
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        return "geckodriver"

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.binary_location = self.find_firefox()

        service = Service(self.find_geckodriver())
        self.driver = webdriver.Firefox(service=service, options=options)

        self.driver.set_page_load_timeout(120)
        self.wait = WebDriverWait(self.driver, 30)

    def load_messages(self):
        with open(self.msg_file, "r", encoding="utf-8") as f:
            self.messages = [i.strip() for i in f if i.strip()]

    def parse_cookies(self):
        cookies = []
        for pair in self.cookie.split(";"):
            if "=" in pair:
                k, v = pair.strip().split("=", 1)
                cookies.append({
                    "name": k,
                    "value": v,
                    "domain": ".facebook.com",
                    "path": "/"
                })
        return cookies

    def login(self):
        self.driver.get("https://www.facebook.com")
        time.sleep(3)

        for c in self.parse_cookies():
            try:
                self.driver.add_cookie(c)
            except:
                pass

        self.driver.refresh()
        time.sleep(5)

    def send_message(self, text):
        box = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@contenteditable='true']")
            )
        )
        box.click()
        box.send_keys(text)
        box.send_keys(Keys.ENTER)

    def start(self):
        try:
            self.setup_driver()
            self.login()
            self.load_messages()

            self.driver.get(f"https://www.facebook.com/messages/e2ee/t/{self.uid}")
            time.sleep(5)

            i = 0
            while True:
                msg = self.messages[i % len(self.messages)]
                if self.haters:
                    msg = self.haters + " " + msg

                self.send_message(msg)
                print(f"[{datetime.now()}] SENT → {msg}")

                time.sleep(self.speed)
                i += 1

        except Exception as e:
            print("ERROR:", e)

        finally:
            try:
                self.driver.quit()
            except:
                pass

# ================= WEB THREAD STARTER =================

def start_bot_thread(cookie, uid, msg_file, haters, speed):
    bot = FacebookMessenger(cookie, uid, msg_file, haters, speed)
    bot.start()

# ================= WEB PAGE =================

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Messenger Bot Panel</title>
<style>
body{
 background:#020617;
 color:white;
 font-family:Arial;
 padding:30px;
}
h2{color:#22c55e}
input,textarea,button{
 width:100%;
 padding:12px;
 margin:8px 0;
 background:#020617;
 color:white;
 border:1px solid #334155;
}
button{
 background:#22c55e;
 font-weight:bold;
 cursor:pointer;
}
</style>
</head>
<body>

<h2>🔥 Facebook Messenger Automation</h2>

<form method="POST">
<textarea name="cookie" placeholder="Facebook Cookies" required></textarea>
<input name="uid" placeholder="Target UID" required>
<input name="msg_file" placeholder="Message File Path (e.g. msgs.txt)" required>
<input name="haters" placeholder="Haters Name (optional)">
<input name="speed" value="10" placeholder="Delay Seconds">
<button type="submit">START BOT</button>
</form>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        cookie = request.form["cookie"]
        uid = request.form["uid"]
        msg_file = request.form["msg_file"]
        haters = request.form["haters"]
        speed = int(request.form["speed"])

        t = threading.Thread(
            target=start_bot_thread,
            args=(cookie, uid, msg_file, haters, speed)
        )
        t.daemon = True
        t.start()

        return "<h2 style='color:lime'>BOT STARTED ✔️ (Check terminal)</h2>"

    return render_template_string(HTML_PAGE)

# ================= RUN SERVER =================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
