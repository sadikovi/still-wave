import local.scripts.misc as misc
import local.scripts.db as database
from local.scripts.music import Album, Song
import local.scripts.requests as req
from local.scripts.manager import Manager
from local.scripts.result import Error, Success


class RecommendationEngine(object):
    def __init__(self, _userid_):
        self._userid = _userid_
        self._processinglimit = 10
        self.db = database.DB(database.r)
        self.manager = Manager()

    def songWeight(self, value):
        r = 1.2 # weight of the song
        n = value # number of same references
        return round((1 - (1/r)**n)*1.0 / (1 - (1/r)), 2)

    def getLikedAlbums(self):
        # get liked albums for user
        raw = self.db.getLikedAlbumIds(self._userid)
        # convert into list
        likes, res = list(raw or []), []
        for like in likes:
            album = self.db.getAlbum(id=like)
            if album and album.id():
                res.append(album)
        return res

    def getDislikedAlbums(self):
        # get liked albums for user
        raw = self.db.getDislikedAlbumIds(self._userid)
        # convert into list
        dislikes, res = list(raw or []), []
        for dislike in dislikes:
            album = self.db.getAlbum(id=dislike)
            if album and album.id():
                res.append(album)
        return res

    def similarSongs(self, album, totalsongs=[], sim_container=set()):
        # fetch songs that similar to liked albums
        # limits are used
        for song in album.songs():
            # get similar songs
            similarsongs = self.db.getSimilarSongs(song.id())
            if similarsongs:
                print "[!] Similar songs found in Redis"
            else:
                print "[!] Similar songs absent. Load from Pandora"
                res = req.loadSongById(song.id())
                if type(res) is Error:
                    print "[!] Request for similar songs for %s (%s-%s) failed" %(song.id(), album.name(), album.artist())
                    print "[!] Similar songs will be set to empty set"
                    similarsongs = set()
                else:
                    # container for similar songs
                    similarsongs = set()
                    # parse song
                    data = res.data()
                    explorer = data["songExplorer"]
                    similar = explorer["similar"]
                    for sim in similar:
                        _simid = misc.getSharUrlId(sim["@shareUrl"])
                        _path = misc.getUrlPath(sim["@trackDetailUrl"])
                        _elems = [misc.unquoteParam(x) for x in _path.split("/")]
                        if len(_elems) > 2:
                            artist, album = _elems[-3:-1]
                            sim_container.add((artist, album))
                            similarsongs.add(_simid)
                        else:
                            print "[!] Track detail url %s cant be parsed" %(sim["@trackDetailUrl"])
                            print "[!] Song %s will be ignored" %(sim["@shareUrl"])
                # add similar songs to the song
                self.db.addSimilarSongs(song.id(), similarsongs)
            # songs are found in Redis or found on Pandora / dont exist
            for x in similarsongs:
                totalsongs.append(x)
        # return total songs
        return totalsongs

    def getSimilarAlbumIds(self):
        albums = self.getLikedAlbums()
        # similar albums container to load
        sim_container = set()
        # total songs
        totalsongs = []
        # get similar songs for every album
        for album in albums:
            self.similarSongs(album, totalsongs, sim_container)
        # load from sim container (first 3 albums)
        for partist, palbum in list(sim_container)[:3]:
            _album = Album(None, palbum, partist)
            # add album to database
            try:
                t = self.manager.exists(self._userid, _album, pandoraNames=True, saveIfNotFound=False)
            except BaseException as e:
                print "[!] Fatal: @exists error: %s" %(str(e))
        # build count map for songs
        songsmap = {}
        for song in totalsongs:
            songsmap[song] = 1 + (songsmap[song] if song in songsmap else 0)
        # get albums for songs
        albumsmap = {}
        for key, value in songsmap.items():
            albumid = self.db.getAlbumForSong(key) or None
            if albumid and albumid in albumsmap:
                albumsmap[albumid] += self.songWeight(value)
            else:
                albumsmap[albumid] = self.songWeight(value)
        # return map with album ids and references
        return albumsmap

    def getRecommendations(self):
        disliked = [x.id() for x in self.getDislikedAlbums()]
        albumsmap, recommendations = self.getSimilarAlbumIds(), {}
        for albumid, ref in albumsmap.items():
            if ref not in recommendations:
                recommendations[ref] = []
            album = self.db.getAlbum(albumid)
            # remove albums that are None or disliked
            if album and album.id() not in disliked:
                recommendations[ref].append(album)
        # return recommendations with {ref - album}
        return recommendations

    def getRecommendationsResult(self):
        try:
            recoms = self.getRecommendations()
            sortedkeys = sorted(recoms.keys(), reverse=True)
            result = []
            for key in sortedkeys:
                result.append({"rating": key, "items": [x.json() for x in recoms[key]]})
            return Success(result)
        except BaseException as e:
            print "[!] Error during calculating recommendations: %s" %(str(e))
            return Error(500, str(e))
