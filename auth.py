#!/usr/bin/env python

# import libs
from google.appengine.api import users
import webapp2


class Login(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_login_url('/'))


class Logout(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/'))


application = webapp2.WSGIApplication([
    ('/login', Login),
    ('/logout', Logout)
], debug=True)
