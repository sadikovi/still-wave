#!/usr/bin/env python

# import libs
from google.appengine.api import users
from google.appengine.ext.webapp import template
import webapp2
import json
# import local
import projectpaths
import config
import local.scripts.manager as m
import local.scripts.misc as misc
from local.scripts.result import Error, Success

manager = m.Manager()

class SearchApi(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "application/json"
        user = users.get_current_user()
        if not user:
            res = Error(401, "Not authenticated")
            self.response.set_status(res.code())
            self.response.out.write(json.dumps(res.json()))
        else:
            query = misc.unquoteParam(self.request.get("q"))
            page = misc.unquoteParam(self.request.get("p"))
            if not query:
                res = Error(400, "Query is empty or undefined")
                self.response.set_status(res.code())
                self.response.out.write(json.dumps(res.json()))
            else:
                res = manager.searchAlbum(user.user_id(), query, page)
                self.response.set_status(res.code())
                self.response.out.write(json.dumps(res.json()))

class ExistsApi(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "application/json"
        user = users.get_current_user()
        if not user:
            res = Error(401, "Not authenticated")
            self.response.set_status(res.code())
            self.response.out.write(json.dumps(res.json()))
        else:
            artist = misc.unquoteParam(self.request.get("artist"))
            album = misc.unquoteParam(self.request.get("album"))
            # check album and artist
            res = manager.exists(user.user_id(), artist, album)
            self.response.set_status(res.code())
            self.response.out.write(json.dumps(res.json()))

class LikeApi(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "application/json"
        user = users.get_current_user()
        if not user:
            res = Error(401, "Not authenticated")
            self.response.set_status(res.code())
            self.response.out.write(json.dumps(res.json()))
        else:
            albumid = misc.unquoteParam(self.request.get("albumid"))
            # check album and artist
            uid = user.user_id()
            res = manager.like(uid, albumid)
            self.response.set_status(res.code())
            self.response.out.write(json.dumps(res.json()))

class DislikeApi(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "application/json"
        user = users.get_current_user()
        if not user:
            res = Error(401, "Not authenticated")
            self.response.set_status(res.code())
            self.response.out.write(json.dumps(res.json()))
        else:
            albumid = misc.unquoteParam(self.request.get("albumid"))
            # check album and artist
            res = manager.dislike(user.user_id(), albumid)
            self.response.set_status(res.code())
            self.response.out.write(json.dumps(res.json()))

class ResetApi(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "application/json"
        user = users.get_current_user()
        if not user:
            res = Error(401, "Not authenticated")
            self.response.set_status(res.code())
            self.response.out.write(json.dumps(res.json()))
        else:
            albumid = misc.unquoteParam(self.request.get("albumid"))
            # check album and artist
            res = manager.reset(user.user_id(), albumid)
            self.response.set_status(res.code())
            self.response.out.write(json.dumps(res.json()))

application = webapp2.WSGIApplication([
    ('/api/search', SearchApi),
    ('/api/exists', ExistsApi),
    ('/api/like', LikeApi),
    ('/api/dislike', DislikeApi),
    ('/api/reset', ResetApi)
], debug=True)
