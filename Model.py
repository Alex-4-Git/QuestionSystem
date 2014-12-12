
from google.appengine.ext import ndb


class Question(ndb.Model):
    author = ndb.UserProperty()
    title = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    edit_date=ndb.DateTimeProperty(auto_now=True)
    up = ndb.ComputedProperty(lambda self: len(self.upList))
    down = ndb.ComputedProperty(lambda self: len(self.downList))
    upList = ndb.StringProperty(repeated=True)
    downList = ndb.StringProperty(repeated=True)
    margin = ndb.ComputedProperty(lambda self: self.up-self.down)

class Answer(ndb.Model):
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    edit_date=ndb.DateTimeProperty(auto_now=True)
    # up = ndb.IntegerProperty()
    # down = ndb.IntegerProperty()
    up = ndb.ComputedProperty(lambda self: len(self.upList))
    down = ndb.ComputedProperty(lambda self: len(self.downList))
    upList = ndb.StringProperty(repeated=True)
    downList = ndb.StringProperty(repeated=True)
    margin = ndb.ComputedProperty(lambda self: self.up-self.down)
