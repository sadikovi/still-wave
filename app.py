#!/usr/bin/env python

# import libs
from google.appengine.api import users
from google.appengine.ext.webapp import template
import webapp2
import json
import os
# import local
import projectpaths
import config
import local.scripts.manager as m
import local.scripts.misc as misc
from local.scripts.result import Error, Success
from local.scripts.suggestions import RecommendationEngine
from local.scripts.collabfiltering import CollaborationEngine


manager = m.Manager()
rengine = RecommendationEngine()
filtering = CollaborationEngine()

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            # create template values
            template_values = {
                "username": user.nickname(),
                "logouturl": "/logout",
                "personalurl": "/personal"
            }
            # load template
            path = os.path.join(os.path.dirname(__file__), "static", "index.html")
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect("/login")


class PersonalPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            # create template values
            template_values = {
                "username": user.nickname(),
                "logouturl": "/logout",
                "searchurl": "/"
            }
            # load template
            path = os.path.join(os.path.dirname(__file__), "static", "personal.html")
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect("/login")


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

class RecommendationsApi(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "application/json"
        user = users.get_current_user()
        if not user:
            res = Error(401, "Not authenticated")
            self.response.set_status(res.code())
            self.response.out.write(json.dumps(res.json()))
        else:
            # check album and artist
            res = rengine.recommendationsForUser(user.user_id())
            self.response.set_status(res.code())
            self.response.out.write(json.dumps(res.json()))


class FilteringApi(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "application/json"
        user = users.get_current_user()
        if not user:
            res = Error(401, "Not authenticated")
            self.response.set_status(res.code())
            self.response.out.write(json.dumps(res.json()))
        else:
            # check album and artist
            res = filtering.recommendationsForUser(user.user_id())
            self.response.set_status(res.code())
            self.response.out.write(json.dumps(res.json()))


class MyAlbumsApi(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "application/json"
        user = users.get_current_user()
        if not user:
            res = Error(401, "Not authenticated")
            self.response.set_status(res.code())
            self.response.out.write(json.dumps(res.json()))
        else:
            # check album and artist
            res = manager.getMyAlbums(user.user_id())
            self.response.set_status(res.code())
            self.response.out.write(json.dumps(res.json()))

application = webapp2.WSGIApplication([
    ('/api/search', SearchApi),
    ('/api/like', LikeApi),
    ('/api/dislike', DislikeApi),
    ('/api/reset', ResetApi),
    ('/api/recommendations', RecommendationsApi),
    ('/api/filtering', FilteringApi),
    ('/api/myalbums', MyAlbumsApi),
    ('/personal', PersonalPage),
    ('/.*', MainPage)
], debug=True)
