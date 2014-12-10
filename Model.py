
from google.appengine.ext import ndb

class Question(ndb.Model):
    author = ndb.UserProperty()
    title = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    edit_date=ndb.DateTimeProperty(auto_now=True)

class Answer(ndb.Model):
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    up = ndb.IntegerProperty()
    down = ndb.IntegerProperty()
