#!/usr/bin/env python

# import libs
from google.appengine.api import users
from google.appengine.ext.webapp import template
import os
import webapp2


class Search(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Hello world!")
        

application = webapp2.WSGIApplication([
    ('/.*', Search)
], debug=True)
