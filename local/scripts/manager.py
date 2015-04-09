from types import DictType
import local.scripts.requests as req
import local.scripts.misc as misc
import local.scripts.db as database
from local.scripts.result import Success, Error
from local.scripts.music import Album, Song


class Manager(object):
    def __init__(self):
        self.db = database.DB(database.r)

    def searchAlbum(self, _userid_, query, page):
        if not self.db.ping():
            return Error(500, "DB connection refused")
        if len(query) == 0:
            return Success([])
        else:
            # set limit of results per page
            limit, maxpage, offset = 10, 1, 2
            # clean page
            page = misc.toUnsignedInt(page) or 1
            page = page if page > 0 else 1
            res = req.searchAlbum(query, page, limit)
            if type(res) is Success:
                data = res.data()["results"]
                # reset page if necessary
                total = misc.toUnsignedInt(data["opensearch:totalResults"])
                # total pages and current page
                maxpage = 1 if total is None else misc.ceilDivison(total, limit)
                page = 1 if page is None or maxpage < page else page
                pages = misc.pages(page, maxpage, frame=5)
                # create albums and jsonobj
                items = data["albummatches"]["album"] if "album" in data["albummatches"] else []
                items = [items] if type(items) is DictType else items
                albums = []
                for item in items:
                    images = item["image"]
                    arturl = images[-1]["#text"] if len(images) > 0 else None
                    # build album
                    _album = Album(None, item["name"], item["artist"], arturl)
                    # perform search in database / Pandora
                    try:
                        _album = self.exists(_userid_, _album)
                    except BaseException as e:
                        print "[!] @exists error: %s" %(str(e))
                    albums.append(_album.json())
                # merge data
                res.setData({"page": page, "maxpage": maxpage, "pages": pages, "results": albums})
            return res

    def exists(self, _userid_, album=None):
        _album = album or Album(None, "", "")
        print "[!] Try loading from Redis: %s - %s" %(_album.artist(), _album.name())
        _album = self.db.getAlbum(album=_album)
        if not _album or not _album.id():
            print "[!] Not found in Redis, loading from Pandora: %s - %s" %(_album.artist(), _album.name())
            # send request to Pandora
            res = req.loadAlbumInfo(_album.name(), _album.artist())
            if not res.data() or len(res.data()) == 0:
                # not found on Pandora
                print "Not found on Pandora"
            else:
                explorer = res.data()["albumExplorer"]
                # remove weird last Data_track from album
                tracks = [x for x in explorer["tracks"] if x["@songTitle"] != "Data_track"]
                # extract album id
                albumid = misc.getSharUrlId(explorer["@shareUrl"])
                # update album
                _album.update(albumid, None, len(tracks), None)
                for track in tracks:
                    songid = misc.getSharUrlId(track["@shareUrl"])
                    _album.addSong(Song(songid))
                # add album to database
                self.db.addAlbum(_album)
        # like album
        _album.setLiked(self.db.userLikesAlbum(_userid_, _album.id()))
        # return updated album
        return _album

    def like(self, _userid_, albumid):
        # like album
        try:
            self.db.likeAlbum(_userid_, albumid)
            return Success(True)
        except BaseException as e:
            # TODO: log error
            return Error(400, str(e))

    def dislike(self, _userid_, albumid):
        # dislike album
        try:
            self.db.dislikeAlbum(_userid_, albumid)
            return Success(True)
        except BaseException as e:
            # TODO: log error
            return Error(400, str(e))

    def reset(self, _userid_, albumid):
        # reset album
        try:
            self.db.resetAlbum(_userid_, albumid)
            return Success(True)
        except BaseException as e:
            # TODO: log error
            return Error(400, str(e))
