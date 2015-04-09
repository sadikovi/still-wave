from types import DictType
import config
import local.scripts.requests as req
import local.scripts.misc as misc
import local.scripts.db as database


class Manager(object):
    def __init__(self):
        self.db = database.DB(database.r)

    def searchAlbum(self, _userid_, query, page):
        if len(query) == 0:
            return {"status": "success", "code": 200, "data": []}
        else:
            # set limit of results per page
            limit, totalpages, offset = 10, 1, 2
            # clean page
            page = misc.toUnsignedInt(page) or 1
            page = page if page > 0 else 1
            res = req.searchAlbum(query, page, limit)
            if res["status"] == "success":
                data = res["data"]["results"]
                # reset page if necessary
                total = misc.toUnsignedInt(data["opensearch:totalResults"])
                # total pages and current page
                maxpage = 1 if total is None else misc.ceilDivison(total, limit)
                page = 1 if page is None or maxpage < page else page
                print page, maxpage
                pages = misc.pages(page, maxpage, 5)
                # create albums and jsonobj
                albums = data["albummatches"]["album"] if "album" in data["albummatches"] else []
                albums = [albums] if type(albums) is DictType else albums
                jsonobj = []
                for _i, album in enumerate(albums):
                    images = album["image"]
                    arturl = images[-1]["#text"] if len(images) > 0 else config.DEFAULT_ALBUM
                    obj = {
                        "name": album["name"],
                        "artist": album["artist"],
                        "arturl": arturl
                    }
                    # perform search in database / Pandora
                    ex = self.exists(_userid_, album["artist"], album["name"])
                    obj["exists"] = ex
                    jsonobj.append(obj)
                # merge data
                res["data"] = {"page": page, "maxpage": maxpage, "pages": pages, "results": jsonobj}
            return res

    def exists(self, _userid_, artist, album):
        # result
        res = {"status": "", "code": -1, "data": {}}
        try:
            # look up album id in database
            albumid = self.db.lookupAlbumId(album, artist)
            if albumid is None:
                print "Loading from Pandora: %s - %s" %(album, artist)
                raw = req.loadAlbumInfo(artist, album)
                if raw["status"] == "success":
                    if len(raw["data"]) == 0:
                        raise StandardError("Album not found")
                    explorer = raw["data"]["albumExplorer"]
                    # remove weird last Data_track from album
                    tracks = [x for x in explorer["tracks"] if x["@songTitle"] != "Data_track"]
                    # extract album id
                    albumid = misc.getSharUrlId(explorer["@shareUrl"])
                    info = {
                        "id": albumid,
                        "artist": explorer["@artistName"],
                        "album": explorer["@albumTitle"],
                        "arturl": explorer["@albumArtUrl"],
                        "tracks": len(tracks)
                    }
                    # store info in database
                    self.db.addAlbumInfo(albumid, info)
                    self.db.setAlbumLookup(albumid, album, artist)
                    for song in tracks:
                        songid = misc.getSharUrlId(song["@shareUrl"])
                        self.db.addSongToAlbum(albumid, songid)
                    # consolidate data and return
                    like = self.db.userLikesAlbum(_userid_, albumid)
                    raw["data"] = {"albumid": albumid, "exists": True, "likedByUser": like}
                # reassign updated raw to res
                res = raw
            else:
                print "Loading from Redis: %s - %s" %(album, artist)
                like = self.db.userLikesAlbum(_userid_, albumid)
                [res["status"], res["code"]] = ["success", 200]
                res["data"] = {"albumid": albumid, "exists": True, "likedByUser": like}
        except BaseException as e:
            # TODO: log error
            [res["status"], res["code"], res["msg"]] = ["error", 400, str(e)]
        finally:
            return res

    def like(self, _userid_, albumid):
        # like album
        res = {"status": "", "code": -1, "data": {}}
        try:
            self.db.likeAlbum(_userid_, albumid)
            res["status"], res["code"], res["data"] = ["success", 200, True]
        except BaseException as e:
            # TODO: log error
            res["status"], res["code"], res["msg"] = ["error", 400, str(e)]
        finally:
            return res

    def dislike(self, _userid_, albumid):
        # dislike album
        res = {"status": "", "code": -1, "data": {}}
        try:
            self.db.dislikeAlbum(_userid_, albumid)
            res["status"], res["code"], res["data"] = ["success", 200, True]
        except BaseException as e:
            # TODO: log error
            res["status"], res["code"], res["msg"] = ["error", 400, str(e)]
        finally:
            return res

    def reset(self, _userid_, albumid):
        # reset album
        res = {"status": "", "code": -1, "data": {}}
        try:
            self.db.resetAlbum(_userid_, albumid)
            res["status"], res["code"], res["data"] = ["success", 200, True]
        except BaseException as e:
            # TODO: log error
            res["status"], res["code"], res["msg"] = ["error", 400, str(e)]
        finally:
            return res
