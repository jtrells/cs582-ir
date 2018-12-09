import requests
import pymongo
from bs4 import BeautifulSoup
from datetime import datetime
from bson.objectid import ObjectId

COMERCIO_BASE = 'https://elcomercio.pe'
MONGO_CLIENT = pymongo.MongoClient("mongodb://runachay.evl.uic.edu:27080/")
db = MONGO_CLIENT["IR_NEWS"]
db.authenticate('ir', 'ir')
col = db.headlines


# For ElComercio, every news tag is most likely included as an anchor.

def parse_content(link):
  url = "%s%s" % (COMERCIO_BASE, link)
  try:
    response = requests.get(url)
  except requests.ConnectionError as error:
    error = "New Connection Error"
    return error, "", [], [], [], None, []

  soup = BeautifulSoup(response.text, 'html.parser')

  _paragraphs = soup.find_all("p", class_="parrafo")
  _captions = soup.find_all("p", class_="foto-description")
  _related_content = soup.find("div", class_="news-related")
  _pub_time = soup.find("time", class_="news-date")
  _embedded_content = soup.find_all("div", class_="html_libre")
  _tags = soup.find_all("h2", class_="tags-item")

  paragraph = ""
  external_links = []

  for p in _paragraphs:
    paragraph = "%s %s" % (paragraph, p.text)

  captions = [c.text for c in _captions if len(c) > 0]
  tags = [t.text for t in _tags]

  publication_datetime = None
  if _pub_time and _pub_time.find("span"):
    publication_datetime = datetime.strptime(_pub_time.find("span").text, "%d.%m.%Y / %I:%M %p")

  if _related_content:
    _related_articles = _related_content.find_all("article", class_="flow")
    rel_news = [ra.find("a")['href'] for ra in _related_articles]
  else:
    rel_news = []

  for ec in _embedded_content:
    content = ec.find("iframe")
    if content:
      # ads do not have src
      if 'src' in content:
        external_links.append(content['src'])
    else:
      _links = ec.find_all("a")
      for l in _links:
        external_links.append(l['href'])

  return None, paragraph, external_links, captions, tags, publication_datetime, rel_news


def add_last_update():
  docs = col.update_many({}, {'$set': {"last_update": None}}, False)


def update_article(headline):
  error, paragraph, external_links, captions, tags, pub_time, rel_news = parse_content(headline['link'])
  col.update_one({
    '_id': ObjectId(headline['_id'])
  }, {
    '$set': {
      'paragraph': paragraph,
      'ext_links': external_links,
      'captions': captions,
      'tags': tags,
      'pub_time': pub_time,
      'rel_news': rel_news,
      'last_update': datetime.now(),
      'error': error
    }
  }, upsert=False)


d1 = datetime(2013, 12, 31)
d2 = datetime(2013, 1, 1)
#docs = col.find({"$and": [{"pub_date": {"$lt": d1}}, {"pub_date": {"$gt": d2}}, {"last_update": None}]})

docs = col.find({'last_update': None})
print("Found %d articles" % docs.count())

i = 0
for doc in docs:
  try:
    update_article(doc)
    i += 1
    print(i)
  except Exception as e:
    print(e)
    print('error')


# for doc in docs:
#   print(doc['pub_date'])
#   new_date = datetime.strptime(doc['pub_date'], "%d/%m/%y")
#   col.update_one({
#     '_id': ObjectId(doc['_id'])
#   }, {
#     '$set': {
#       'pub_date': new_date
#     }
#   }, upsert=False)
# print("end")


link = "mundo/mexico/toma-protesta-amlo-vivo-andres-manuel-lopez-obrador-asume-primer-presidente-izquierda-mexico-noticia-583132"
#link =
#parse_content(link)