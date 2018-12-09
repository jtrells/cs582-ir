import requests
import pymongo
import json
from bs4 import BeautifulSoup
from NewsHeadline import Headline

# For ElComercio
COMERCIO_BASE = 'https://elcomercio.pe/archivo/todas/'
LOG_FILE = 'scrapping_el_comercio'

MONGO_CLIENT = pymongo.MongoClient("mongodb://localhost:27017/")
DB = MONGO_CLIENT["IR_NEWS"]
DB.authenticate('ir', 'ir')
HEADLINE_COLLECTION = DB["headlines"]


def get_headlines(date):
  url = "%s%d-%d-%d" % (COMERCIO_BASE, date.year, date.month, date.day)
  response = requests.get(url)
  hub = []

  # If there is a redirect, there are no news for that day
  if not response.history:
    soup = BeautifulSoup(response.text, 'html.parser')
    for article in soup.find_all("article", class_="section-flow"):
      headline = extract_headline_info(article)

      json_headline = json.loads(headline.__repr__())
      HEADLINE_COLLECTION.insert_one(json_headline)
      hub.append(headline)
    return hub
  else:
    return None


def extract_headline_info(article):
  html_category = article.find('h3', class_="flow-category")
  html_date = article.find('time', class_="flow-date")
  html_title = article.find('h2', class_="flow-title")
  html_summary = article.find('p', class_="flow-summary")
  html_author = article.find('span', class_="flow-author")

  category = html_category.get_text() if html_category else None
  breadcrumb = html_category.find('a')['href']
  publication_date = html_date.get_text().strip() if html_date else None

  a_title = html_title.find('a') if html_title else None
  title = a_title.get_text().strip() if a_title else None
  link = a_title['href'] if a_title else None

  summary = html_summary.get_text().strip() if html_summary else None
  author = html_author.get_text() if html_author else None

  headline = Headline(title, link, author, category, breadcrumb, publication_date, summary, 'El Comercio')
  return headline


def log_scrapping(date, count):
  with open(LOG_FILE, "a") as f:
    f.write("%s,%d\n" % (date.strftime("%Y-%m-%d"), count))


import datetime as dt
today = dt.datetime.today()

while True:
  print(today)
  headlines = get_headlines(today)
  if headlines:
    log_scrapping(today, len(headlines))
    yesterday = today - dt.timedelta(days=1)
    today = yesterday
  else:
    log_scrapping(today, -1)
    break
