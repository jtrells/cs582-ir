import json
from collections import OrderedDict


def jsonDefault(OrderedDict):
  return OrderedDict.__dict__


class Headline():
  def __init__(self, title, link, author, category, breadcrumb, publication_date, summary, source):
    self.category = category
    self.breadcrumb = breadcrumb
    self.pub_date = publication_date
    self.title = title
    self.link = link
    self.summary = summary
    self.author = author
    self.source = source

  def __repr__(self):
    return json.dumps(self, default=jsonDefault, indent=4)

  def print(self):
    print("-----------------------------------------")
    print("Title: %s" % self.title)
    print("Link: %s" % self.link)
    print("Breadcrumb: %s " % self.breadcrumb)
    print("Category: %s" % self.category)
    print("Publication Date: %s" % self.pub_date)
    print("Author: %s" % self.author)
    print("Summary: %s" % self.summary)
    print()

