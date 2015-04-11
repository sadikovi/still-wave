import local.scripts.misc as misc
import local.scripts.db as database
from local.scripts.music import Album, Song
import local.scripts.requests as req
from local.scripts.manager import Manager
from local.scripts.result import Error, Success


class RecommendationEngine(object):
    def __init__(self, db=database.r):
        self._processinglimit = 10
        self._topRatedResults = 7
        self.db = database.DB(db)
        self.manager = Manager(db)

    def songWeight(self, value):
        r = 1.2 # weight of the song
        n = value # number of same references
        return round((1 - (1/r)**n)*1.0 / (1 - (1/r)), 2)

    def getLikedAlbums(self, _userid):
        # get liked albums for user
        likes = self.db.getLikedAlbumIds(_userid)
        res = []
        for albumid in likes:
            album = self.db.getAlbum(albumid)
            res.append(album) if album and album.id() else None
        return res

    def getDislikedAlbums(self, _userid):
        # get liked albums for user
        dislikes = self.db.getDislikedAlbumIds(_userid)
        res = []
        for albumid in dislikes:
            album = self.db.getAlbum(albumid)
            res.append(album) if album and album.id() else None
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
                # limit on loading albums
                if len(sim_container) > self._processinglimit:
                    print "[!] Processing limit is reached. No download"
                    continue
                else:
                    print "[!] Similar songs absent. Load from Pandora"
                    # initialise to empty set
                    similarsongs = set()
                    # load song info
                    res = req.loadSongById(song.id())
                    if type(res) is Error:
                        print "[!] Request for similar songs for %s (%s-%s) failed" %(song.id(), album.name(), album.artist())
                    elif type(res) is Success and res.data():
                        # song is found, parse it
                        data = res.data()
                        similar = data["songExplorer"]["similar"]
                        for item in similar:
                            itemid = misc.getShareUrlId(item["@shareUrl"])
                            itempath = misc.getUrlPath(item["@trackDetailUrl"])
                            pathelems = [misc.unquoteParam(x) for x in itempath.split("/")]
                            if len(pathelems) > 2:
                                artist, album = pathelems[-3:-1]
                                sim_container.add((artist, album))
                                similarsongs.add(itemid)
                            else:
                                print "[!] Track detail url %s cant be parsed" %(item["@trackDetailUrl"])
                                print "[!] Song %s will be ignored" %(item["@shareUrl"])
                    # add similar songs to the song
                    self.db.addSimilarSongs(song.id(), similarsongs)
            # songs are found in Redis or found on Pandora / dont exist
            for x in similarsongs:
                totalsongs.append(x) if x else None
        # return total songs
        return totalsongs

    def getSimilarAlbumIds(self, _userid):
        albums = self.getLikedAlbums(_userid)
        # similar albums container to load, and total songs
        sim_container, totalsongs = set(), []
        # get similar songs for every album
        for album in albums:
            self.similarSongs(album, totalsongs, sim_container)
        # load from sim container (first 3 albums)
        for partist, palbum in list(sim_container)[:3]:
            _album = Album(None, palbum, partist)
            # add album to database
            try:
                self.manager.exists(_userid, _album, pandoraNames=True, saveIfNotFound=False)
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

    def getRecommendations(self, _userid):
        disliked = [x.id() for x in self.getDislikedAlbums(_userid)]
        liked = [x.id() for x in self.getLikedAlbums(_userid)]
        albumsmap, recommendations = self.getSimilarAlbumIds(_userid), []
        references = sorted(set(albumsmap.values()), reverse=True)
        for ref in references:
            # add recommendations only if rating is more than 1.0
            if ref > 1:
                for key, value in albumsmap.items():
                    if value == ref and key not in disliked and key not in liked:
                        album = self.db.getAlbum(key)
                        if not album:
                            print "[!] Recommended album for key %s was None" %(key)
                        elif len(recommendations) < self._topRatedResults:
                            recommendations.append({"rating": ref, "item": album.json()})
                        else:
                            print "More than limit. Top recommendations are selected"
                            return recommendations
        # return recommendations with {ref - album json}
        return recommendations

    def recommendationsForUser(self, _userid):
        try:
            return Success(self.getRecommendations(_userid))
        except BaseException as e:
            print "[!] Error during calculating recommendations: %s" %(str(e))
            return Error(500, str(e))
