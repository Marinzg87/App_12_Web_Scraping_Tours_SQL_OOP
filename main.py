import requests
import selectorlib
import smtplib
import ssl
import os
import time
import sqlite3

PASSWORD = os.getenv("GMAIL_WEBCAM_MESSAGE")
SENDER = os.getenv("GMAIL_EMAIL_ADDRESS")
RECEIVER = os.getenv("GMAIL_EMAIL_ADDRESS")

URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                  '/AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/39.0.2171.95 /Safari/537.36'}


class Event:
    def scrape(self, url):
        """Scrape the page source from the URL"""
        response = requests.get(url, headers=HEADERS)
        source = response.text
        return source

    def extract(self, source):
        extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
        value = extractor.extract(source)["tours"]
        return value


class Email:
    def send(self, message):
        host = "smtp.gmail.com"
        port = 465

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(SENDER, PASSWORD)
            server.sendmail(SENDER, RECEIVER, message)
        print("Email was sent!")


class Database:
    def __init__(self, database_path):
        self.connection = sqlite3.connect(database_path)

    def store(self, extracted_local):
        row_local = extracted_local.split(",")
        row_local = [item.strip() for item in row_local]
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO events VALUES(?,?,?)", row_local)
        self.connection.commit()

    def read(self, extracted_local):
        row_local = extracted_local.split(",")
        row_local = [item.strip() for item in row_local]
        band, city, date = row_local
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND "
                       "date=?", (band, city, date))
        rows = cursor.fetchall()
        print(rows)
        return rows


if __name__ == "__main__":
    while True:
        event = Event()
        scraped = event.scrape(URL)
        extracted = event.extract(scraped)
        print(extracted)

        if extracted != "No upcoming tours":
            database = Database(database_path="data.db")
            row = database.read(extracted)
            if not row:
                database.store(extracted)
                email = Email()
                email.send(message="Hey, new event was found!")
        time.sleep(2)
