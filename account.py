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


class Account(webapp2.RequestHandler):

	def get(self):
		current_user = users.get_current_user()
		if not current_user:
			url = users.create_login_url(self.request.uri)
			self.redirect(url)
			return
		question_query=Question.query(Question.author == users.get_current_user()).order(-Question.date)
		questions = question_query.fetch()
		answer_query=Answer.query(Answer.author == users.get_current_user()).order(-Answer.date)
		answers = answer_query.fetch()
		images = Image.get_author(current_user)
		template_values = {
			'questions' : questions,
			'answers' : answers,
			'images' : images
		}
		template = JINJA_ENVIRONMENT.get_template('account.html')
		self.response.write(template.render(template_values))




application = webapp2.WSGIApplication([
    ('/account', Account)
], debug=True)