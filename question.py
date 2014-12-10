import os
import urllib
import cgi
import time

from Model import *
from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

#DEFAULT_GUESTBOOK_NAME = 'default_guestbook'


# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def get_current_date():
    import datetime
    return datetime.date.today().strftime("%d.%m.%Y")

def question_key(question_name,author,date):
    """Constructs a Datastore key for a answer entity with quesiton_name."""
    return ndb.Key('Question',question_name,'Author',author,'Date',date)


class MainPage(webapp2.RequestHandler):

    def get(self):

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        question_query=Question.query().order(-Question.date)
        questions = question_query.fetch()

        template_values = {
            'questions': questions,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class AddQuestion(webapp2.RequestHandler):

    def post(self):
  
        if not users.get_current_user():
           url = users.create_login_url(self.request.uri)
           self.redirect(url)
           return

        question = Question()

        if users.get_current_user():
            question.author = users.get_current_user()

        question.content = self.request.get('content')
        question.title = self.request.get('title')
        question.put()
        time.sleep(0.1)
 
        self.redirect('/')

    def get(self):
        # question = Question()
        # question.author = users.get_current_user()
        # question.content = self.request.get('content')
        # question.title = self.request.get('title')
        # question.put()
        # time.sleep(0.1)
        self.redirect('/')

class listAnswer(webapp2.RequestHandler):

    def get(self):
        question_id = self.request.get('question_id')
        question_key = ndb.Key('Question', int(question_id))
        question=question_key.get()
        answers=Answer.query(ancestor=question_key).order(-Answer.date).fetch()
        template_values = {
            'question': question,
            'answers': answers,
        }

        template = JINJA_ENVIRONMENT.get_template('answers.html')
        self.response.write(template.render(template_values))


class AddAnswer(webapp2.RequestHandler):
    def post(self):
        if not users.get_current_user():
           url = users.create_login_url(self.request.uri)
           self.redirect(url)
           return

        question_id=self.request.get('question_id')
        question_key = ndb.Key('Question', int(question_id))

        #initiallize instance answer
        answer = Answer(parent=question_key)
        answer.author = users.get_current_user()
        answer.content = self.request.get('content')
        answer.up=0
        answer.down=0

        answer.put()
        time.sleep(0.1)
        
        query_params = {'question_id': question_id}
        self.redirect('/answer?' + urllib.urlencode(query_params))

    def get(self):
        self.redirect('/')

class Vote(webapp2.RequestHandler):
    def post(self):
        if not users.get_current_user():
           url = users.create_login_url(self.request.uri)
           self.redirect(url)
           return

        question_id=self.request.get('question_id')
        # question_key = ndb.Key('Question', int(question_id))
        answer_id=self.request.get('answer_id')
        answer_key = ndb.Key(Question, int(question_id), Answer, int(answer_id))
        vote = self.request.get('name')
        #update answer
        answer=answer_key.get()
        if vote=="up":
            answer.up+=1
        else:
            answer.down+=1
        answer.put()
        time.sleep(0.1)
        
        query_params = {'question_id': question_id}
        self.redirect('/answer?' + urllib.urlencode(query_params))

    def get(self):
        self.redirect('/')


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/add', AddQuestion),
    ('/answer',listAnswer),
    ('/addA', AddAnswer),
    ('/vote', Vote)
], debug=True)