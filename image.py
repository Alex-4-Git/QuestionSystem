import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images


import jinja2
import webapp2

from Model import *
from question import *

class ImageHandler(webapp2.RequestHandler):
    def get(self, url):
	picture = Image.query(Image.url == url).get()
	#picture = Image.get_by_id(int(url))
	if picture.image:
	    self.response.headers['Content-Type'] = 'image/png'
	    self.response.out.write(picture.image)

class Uploader(webapp2.RequestHandler):
    def get(self):
	# # header(self)
	url,url_linktext = get_login_URL(self)
	template_values = {
		'current_user':users.get_current_user(),
		'url': url,
		'url_linktext': url_linktext,
	}
	template = JINJA_ENVIRONMENT.get_template('upload.html')
	self.response.write(template.render(template_values))

	
	# footer(self)
    def post(self):
	# header(self)
	if users.get_current_user():
		res = self.request.get('img')
		image = Image()
		image.image = res
		image.user = users.get_current_user()
		#image.url = image.user+"_"+self.request.params['img'].filename
		image_key = image.put()
		image = Image.get_by_id(image_key.id())
		image.url = str(image_key.id())+"_"+self.request.params['img'].filename
		image.put()
		self.redirect("/account")
	# self.response.write('<p class="main">Upload Success!</p>')

	# footer(self)

class DeleteImage(webapp2.RequestHandler):
    def get(self, key):
	# header(self)
	if users.get_current_user():
	    img = Image.get_by_id(int(key))
	    user = users.get_current_user()
	    if img.user == user:
		img.key.delete()
		self.redirect("/account")
	#     self.response.write('<p class="main"><b>Success!</b></p>')
	# else:
	#     self.response.write('''<p class="main">You don't have permission!</p>''')
	# # footer(self)


application = webapp2.WSGIApplication([
    ('/upload', Uploader),
    ('/img/delete/(.*)', DeleteImage),
    ('/img/(.*)', ImageHandler),
], debug=True)