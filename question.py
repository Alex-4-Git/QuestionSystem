import os
import urllib
import cgi
import time

from Model import *
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from sets import Set
# from jinja2.filters import *

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



class MainPage(webapp2.RequestHandler):

    def get(self):
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        #every page display 2 quesions
        pagesize=5
        curs=Cursor(urlsafe=self.request.get('cursor'))
        questions,next_page_url = show_page(curs,pagesize)

        template_values = {
            'current_user':users.get_current_user(),
            'questions': questions,
            'url': url,
            'url_linktext': url_linktext,
            'next_page_url':next_page_url,
        }

        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(template_values))


class AddQuestion(webapp2.RequestHandler):

    def post(self):
  
        if not users.get_current_user():
           url = users.create_login_url(self.request.uri)
           self.redirect(url)
           return

        question_id=self.request.get("question_id")
        if question_id:
            question_key=ndb.Key(Question,int(question_id))
            question=question_key.get()
            question.content=self.request.get('content')
            question.put()
            time.sleep(0.1)
            query_params = {'question_id': question_id}
            self.redirect('/answer?' + urllib.urlencode(query_params))
            

        else:
            question = Question()
            question.author = users.get_current_user()
            question.content = self.request.get('content')
            question.title = self.request.get('title')
            if self.request.get('tag'):
                question.tags = strip_tags(self.request.get('tag'))
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
        #answers=Answer.query(ancestor=question_key).order(-Answer.margin).fetch()

        pagesize=4
        curs=Cursor(urlsafe=self.request.get('cursor'))
        answers,next_page_url = show_answer_page(curs,pagesize,question_key,question_id)

        template_values = {
            'next_page_url':next_page_url,
            'question': question,
            'answers': answers,
            'current_user':users.get_current_user()
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
        answer_id=self.request.get('answer_id')
        #edit an existing answer
        if answer_id:
            answer_key = ndb.Key(Question,int(question_id),Answer,int(answer_id))
            answer=answer_key.get()
            answer.content=self.request.get('content')


        #initiallize instance answer
        else:
            answer = Answer(parent=question_key)
            answer.parent_id = int(question_id)
            answer.question_title = question_key.get().title
            answer.author = users.get_current_user()
            answer.content = self.request.get('content')
        # answer.up=0
        # answer.down=0

        answer.put()
        time.sleep(0.1)
        query_params = {'question_id': question_id}
        self.redirect('/answer?' + urllib.urlencode(query_params))

    def get(self):
        self.redirect('/')


class Vote(webapp2.RequestHandler):
    def goToQuestionPage(self,question_id):
        query_params = {'question_id': question_id}
        self.redirect('/answer?' + urllib.urlencode(query_params))

    def updateVote(self,vote,QorA,question_id,user_id):
        if vote=="up":
            if (user_id not in QorA.upList):
                QorA.upList.append(user_id)
            else:
                self.goToQuestionPage(question_id)
        if vote=="down":
            if (user_id not in QorA.downList):
                QorA.downList.append(user_id)
            else:
                self.goToQuestionPage(question_id)

        QorA.put()
        time.sleep(0.1)
        self.goToQuestionPage(question_id)


    def post(self):
        current_user = users.get_current_user()
        if not current_user:
           url = users.create_login_url(self.request.uri)
           self.redirect(url)
           return
        user_id=current_user.user_id()
        question_id=self.request.get('question_id')
        question_key=ndb.Key(Question,int(question_id))
        question=question_key.get()
        vote = self.request.get('name')
        answer_id=self.request.get('answer_id')
        
        #update question vote
        if not answer_id:
            self.updateVote(vote,question,question_id,user_id)
        #update answer vote 
        if answer_id:
            answer_key = ndb.Key(Question, int(question_id), Answer, int(answer_id))
            answer=answer_key.get()
            self.updateVote(vote,answer,question_id,user_id)

    def get(self):
        self.redirect('/')

class WWarning(webapp2.RequestHandler):
    def post(self):
        question_id=self.request.get("question_id")
        template_values = {
            'question_id': question_id
        }
        template = JINJA_ENVIRONMENT.get_template('warning.html')
        self.response.write(template.render(template_values))

class TagHandler(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        #every page display 2 quesions
        pagesize=5
        tag=self.request.get('tag')
        curs=Cursor(urlsafe=self.request.get('cursor'))
        questions,next_page_url = show_tag_page(curs,pagesize,tag)

        template_values = {
            'current_user':users.get_current_user(),
            'questions': questions,
            'url': url,
            'url_linktext': url_linktext,
            'next_page_url':next_page_url,
            # 'tags':tags
        }

        template = JINJA_ENVIRONMENT.get_template('tag.html')
        self.response.write(template.render(template_values))




application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/add', AddQuestion),
    ('/answer',listAnswer),
    ('/addA', AddAnswer),
    ('/vote', Vote),
    ('/warning',WWarning),
    ('/tag',TagHandler)
], debug=True)