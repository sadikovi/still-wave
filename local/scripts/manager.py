from types import DictType
import local.scripts.requests as req
import local.scripts.misc as misc
import local.scripts.db as database
from local.scripts.result import Success, Error
from local.scripts.music import Album, Song


class Manager(object):
    def __init__(self, db=database.r):
        self.db = database.DB(db)

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
                    _album = Album(None, item["name"], item["artist"], arturl, mbid=item["mbid"])
                    # perform search in database / Pandora
                    try:
                        _album = self.exists(_userid_, _album, pandoraNames=True)
                    except BaseException as e:
                        print "[!] Fatal: @exists error: %s" %(str(e))
                    albums.append(_album.json())
                # merge data
                res.setData({"page": page, "maxpage": maxpage, "pages": pages, "results": albums})
            return res

    def exists(self, _userid_, album=None, pandoraNames=False, saveIfNotFound=True):
        if not album:
            print "[!] Undefined album was passed. It will be skipped"
            return None
        # album is not None
        albumid, lookupname, lookupartist = album.id(), album.name(), album.artist()
        if not albumid:
            # perform lookup
            albumid = self.db.lookupAlbum(lookupname, lookupartist)
        print "[!] Try loading from Redis: %s - %s" %(album.artist(), album.name())
        _album = self.db.getAlbum(albumid) or album
        if not _album.id():
            print "[!] Not found in Redis, loading from Pandora"
            # send request to Pandora
            res = req.loadAlbumInfo(_album.name().lower(), _album.artist().lower())
            if not res.data() or len(res.data()) == 0:
                # not found on Pandora
                print "[!] Not found on Pandora, loading from Last.fm"
                res = req.loadAlbumInfo(_album.name().lower(), _album.artist().lower(), ispandora=False)
                if type(res) is Success:
                    # parse data and load album
                    explorer = res.data()["album"]
                    albumid = misc.newId()
                    tracksinfo = explorer["tracks"]["track"] if "track" in explorer else []
                    tracks = [tracksinfo] if type(tracksinfo) is DictType else tracksinfo
                    for track in tracks:
                        songid = track["mbid"]
                        _album.addSong(Song(songid))
                    _album.update(albumid, None, len(tracks), None, ispandora=False)
                else:
                    print "Not found on Pandora and Last.fm"
                    if saveIfNotFound:
                        print "Saving not found album anyway..."
                        # generate fake id and push it to db
                        albumid = "%s#%s" %("SW", misc.newId())
                        _album.update(albumid, None, 0, None, ispandora=False, hassource=False)
            else:
                explorer = res.data()["albumExplorer"]
                # remove weird last Data_track from album
                tracks = [x for x in explorer["tracks"] if x["@songTitle"] != "Data_track"]
                # extract album id
                albumid = misc.getShareUrlId(explorer["@shareUrl"])
                # arturl Pandora
                arturl = explorer["@albumArtUrl"] if "@albumArtUrl" in explorer else None
                # update album
                if pandoraNames:
                    # it means we require Pandora data (album name and artist)
                    _album.setName(explorer["@albumTitle"])
                    _album.setArtist(explorer["@artistName"])
                _album.update(albumid, arturl, len(tracks), None)
                # add songs to album
                for track in tracks:
                    songid = misc.getShareUrlId(track["@shareUrl"])
                    _album.addSong(Song(songid))
            # add lookup on old values
            self.db.addLookup(_album.id(), lookupname, lookupartist)
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
            self.db.likeUserByAlbum(albumid, _userid_)
            return Success(True)
        except BaseException as e:
            # TODO: log error
            return Error(400, str(e))

    def dislike(self, _userid_, albumid):
        # dislike album
        try:
            self.db.dislikeAlbum(_userid_, albumid)
            self.db.dislikeUserByAlbum(albumid, _userid_)
            return Success(True)
        except BaseException as e:
            # TODO: log error
            return Error(400, str(e))

    def reset(self, _userid_, albumid):
        # reset album
        try:
            self.db.resetAlbum(_userid_, albumid)
            self.db.resetUserByAlbum(albumid, _userid_)
            return Success(True)
        except BaseException as e:
            # TODO: log error
            return Error(400, str(e))

    def getMyAlbums(self, _userid_):
        try:
            liked = self.db.getLikedAlbumIds(_userid_)
            disliked = self.db.getDislikedAlbumIds(_userid_)
            albums = []
            for _id in liked | disliked:
                _album = self.db.getAlbum(_id)
                _album.setLiked(self.db.userLikesAlbum(_userid_, _album.id()))
                albums.append(_album.json())
            return Success(albums)
        except BaseException as e:
            return Error(500, str(e))
