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

manager = m.Manager()

class SearchApi(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "application/json"
        user = users.get_current_user()
        if not user:
            jsonobj = {"status": "error", "msg": "Not authenticated", "code": 401}
            self.response.set_status(401)
            self.response.out.write(json.dumps(jsonobj))
        else:
            query = misc.unquoteParam(self.request.get("q"))
            if not query:
                jsonobj = {"status": "error", "msg": "Query is empty or undefined", "code": 400}
                self.response.set_status(400)
                self.response.out.write(json.dumps(jsonobj))
            else:
                res = manager.searchAlbum(query)
                self.response.set_status(res["code"])
                self.response.out.write(json.dumps(res))

class ExistsApi(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "application/json"
        user = users.get_current_user()
        if not user:
            jsonobj = {"status": "error", "msg": "Not authenticated", "code": 401}
            self.response.set_status(401)
            self.response.out.write(json.dumps(jsonobj))
        else:
            artist = misc.unquoteParam(self.request.get("artist"))
            album = misc.unquoteParam(self.request.get("album"))
            # check album and artist
            res = manager.exists(user.user_id(), artist, album)
            self.response.set_status(res["code"])
            self.response.out.write(json.dumps(res))

class LikeApi(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "application/json"
        user = users.get_current_user()
        if not user:
            jsonobj = {"status": "error", "msg": "Not authenticated", "code": 401}
            self.response.set_status(401)
            self.response.out.write(json.dumps(jsonobj))
        else:
            albumid = misc.unquoteParam(self.request.get("albumid"))
            # check album and artist
            res = manager.like(user.user_id(), albumid)
            self.response.set_status(res["code"])
            self.response.out.write(json.dumps(res))

class DislikeApi(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "application/json"
        user = users.get_current_user()
        if not user:
            jsonobj = {"status": "error", "msg": "Not authenticated", "code": 401}
            self.response.set_status(401)
            self.response.out.write(json.dumps(jsonobj))
        else:
            albumid = misc.unquoteParam(self.request.get("albumid"))
            # check album and artist
            res = manager.dislike(user.user_id(), albumid)
            self.response.set_status(res["code"])
            self.response.out.write(json.dumps(res))

application = webapp2.WSGIApplication([
    ('/api/search', SearchApi),
    ('/api/exists', ExistsApi),
    ('/api/like', LikeApi),
    ('/api/dislike', DislikeApi)
], debug=True)
