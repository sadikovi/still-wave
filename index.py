import api
import misc
import db

ALBUMS = []
userid = "user@test"

def flow():
    print "Hello to bitter-glitter"
    while True:
        command = raw_input(">>> ")
        if command == "search":
            s = raw_input("type album name to search: ").strip()
            if len(s) == 0:
                print "Album name cannot be empty"
            else:
                res = api.searchAlbum(s)
                if res["status"] == "error":
                    print "Error: " + res["msg"]
                else:
                    results = res["data"]["results"]
                    numberOfResults = int(results["opensearch:totalResults"])
                    if numberOfResults > 0:
                        albums = results["albummatches"]["album"]
                        for i, album in enumerate(albums):
                            print str(i)+": "+album["artist"]+" - "+album["name"]
                        ALBUMS = albums
                    else:
                        print "Nothing found for %s" %(s)
        elif command == "pandora":
            s = raw_input("type number of the album: ").strip()
            try:
                index = int(s)
                if not 0<=index<len(ALBUMS):
                    raise ValueError("out of range")
            except ValueError as valueerror:
                print "Wrong album number"
            else:
                album = ALBUMS[index]
                print "Loading information about album..."
                res = api.loadAlbumInfo(album["artist"], album["name"])
                if res["status"] == "error":
                    print "Error: " + res["msg"]
                else:
                    palbum = res["data"]
                    if len(palbum) > 0:
                        album = palbum["albumExplorer"]
                        print "Found: "+album["@artistName"]+" - "+album["@albumTitle"]
                        print "Processing tracks..."
                        tracks = album["tracks"]
                        while True:
                            like = raw_input("Do you like this album? Y/N ")
                            if like.lower() == "n":
                                print "You do not like this album"
                                for track in tracks:
                                    shareurl = track["@shareUrl"]
                                    songid = misc.getSharUrlId(shareurl)
                                    db.dislikeSong(userid, songid)
                                break
                            elif like.lower() == "y":
                                for track in tracks:
                                    shareurl = track["@shareUrl"]
                                    songid = misc.getSharUrlId(shareurl)
                                    db.likeSong(userid, songid)
                                    res = api.loadSongById(songid)
                                    if res["status"] == "error":
                                        print "Error: " + res["msg"]
                                    else:
                                        results = res["data"]
                                        if len(results) == 0:
                                            print songid + ": Nothing to process"
                                        else:
                                            song = results["songExplorer"]
                                            similar = song["similar"]
                                            db.addSimilarSongs(songid, [misc.getSharUrlId(x["@shareUrl"]) for x in similar])
                                            print songid + ": Similar songs = ", [x["@shareUrl"] for x in similar]
                                break
                    else:
                        print "Nothing found for album %d" %(index)
        elif command == "exit":
            return False
        else:
            continue
    print "Bye, bye"
# run flow
flow()
