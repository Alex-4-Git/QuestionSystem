
from google.appengine.ext import ndb

def strip_tags(tags): # input is a list of tags separated by comma
  tags = tags.split(',')
  for x in range(len(tags)):
    tags[x] = tags[x].strip()
    if tags[x] == '':
        tags[x] = None
  tags = filter(None, tags)
  tags = list(set(tags))
  return tags


def show_page(curs,pagesize):
    if curs:
        entries,next_curs,more = Question.query().order(-Question.date).fetch_page(pagesize,start_cursor=curs)
    else:
        entries,next_curs,more = Question.query().order(-Question.date).fetch_page(pagesize)
    if more and next_curs:
         next_page_url="/?cursor=%s"%next_curs.urlsafe()
    else: next_page_url=""
    return entries,next_page_url

def show_tag_page(curs,pagesize,target_tag):
    if curs:
        entries,next_curs,more = Question.query(Question.tags == target_tag).order(-Question.date).fetch_page(pagesize,start_cursor=curs)
    else:
        entries,next_curs,more = Question.query(Question.tags == target_tag).order(-Question.date).fetch_page(pagesize)
    if more and next_curs:
         next_page_url="/tag?tag=%s&cursor=%s"%(target_tag,next_curs.urlsafe())
    else: next_page_url=""
    return entries,next_page_url

def show_answer_page(curs,pagesize,question_key,question_id):
    if curs:
        entries,next_curs,more = Answer.query(ancestor=question_key).order(-Answer.margin).fetch_page(pagesize,start_cursor=curs)
    else:
        entries,next_curs,more = Answer.query(ancestor=question_key).order(-Answer.margin).fetch_page(pagesize)
    if more and next_curs:
         next_page_url="/answer?question_id=%s&cursor=%s"%(question_id,next_curs.urlsafe())
    else: next_page_url=""
    return entries,next_page_url

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
    tags = ndb.StringProperty(repeated=True)

    # @classmethod
    # def get_tagged_question(cls, tag, page):
    #     q = Question.query(Question.tags == tag).order(-Question.margin)
    #     if int(page) > 0:
    #       p = int(page)*10 - 10
    #       return q.fetch(10, offset=p)
    #     else:
    #       return q.fetch(10)


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

class Tag(ndb.Model):
    name = ndb.StringProperty()
    questionList = ndb.IntegerProperty()
