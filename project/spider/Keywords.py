import requests
import pymongo
from datetime import datetime
from bson.objectid import ObjectId
from AbstractProcessor import tokenize, TextProcessor

MONGO_CLIENT = pymongo.MongoClient("mongodb://runachay.evl.uic.edu:27080/")
db = MONGO_CLIENT["IR_NEWS"]
db.authenticate('ir', 'ir')
col = db.headlines

doc = col.find_one({})

# force 10
def ranks_to_obj(n_grams, scores, sorted_idx, n):
  rank = {"n": n, "ranks": []}
  l = min(10, len(n_grams))
  for i in range(l):
    rank["ranks"].append(
      {
        "key": n_grams[sorted_idx[i]],
        "val": scores[sorted_idx[i]]
      })
  return rank

def update_article(doc, ranks):
  col.update_one({
    '_id': ObjectId(doc['_id'])
  }, {
    '$set': {
      'e_keys': ranks,
      'last_update': datetime.now(),
    }
  }, upsert=False)


d1 = datetime(2018, 10, 1)
d2 = datetime(2018, 11, 1)

docs = col.find({"pub_time": {"$gt": d1, "$lt": d2}})
#docs = col.find({"pub_time": {"$gt": d1}})
print(docs.count())

total_found = 0
for doc in docs:
  found = False
  curated_tags = [d.lower() for d in doc['tags']]
  top_5_keywords = [d['key'] for d in doc['e_keys'][2]['ranks'][:5]]

  for k in top_5_keywords:
    for ck in curated_tags:
      if k in ck:
        found = True
        break
    if found:
      break
  if found:
    total_found += 1

print(total_found/docs.count())

# for doc in docs:
#   t = TextProcessor(doc)
#   rank = {}
#   ranks = []
#   for i in range(3):
#     n_grams, scores, sorted_idx = t.rank_n_grams(i + 1)
#     ranks.append(ranks_to_obj(n_grams, scores, sorted_idx, i + 1))
#   rank = {
#     "1": ranks[0],
#     "2": ranks[1],
#     "3": ranks[2]
#   }
#   update_article(doc, ranks)
#   print(doc['title'])

print('a')