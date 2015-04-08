# search
searchBox = document.getElementById "sw-search-box"
searchInput = document.getElementById "sw-search-box-input"
searchResults = document.getElementById "sw-search-results"
throw "No binding elements found" unless searchBox and searchInput and searchResults

lock = -> searchInput.setAttribute "disabled", "true"
unlock = -> searchInput.removeAttribute "disabled"
clear = (elem) -> elem.innerHTML = ""
setLoading = (elem) -> @util.addClass elem, "loading"
unsetLoading = (elem) ->@util.removeClass elem, "loading"

searchQuery = (query) ->
    setLoading searchBox
    lock searchInput
    clear searchResults
    @loader.sendrequest "get", "/api/search?q=#{@util.quote(query)}", {}, null, (status, result) ->
        unsetLoading searchBox
        unlock searchInput
        albums = JSON.parse(result)["data"]
        if albums.length == 0
            # nothing is found
            map =
                type: "div"
                cls: "pl-text-center"
                children:
                    type: "div"
                    cls: "pl-text-large"
                    title: "Nothing was found. Try again :-("
        else
            map =
                type: "div"
                cls: "ui divided items"
            items = []
            for album in albums
                item =
                    type: "div"
                    cls: "item"
                    children: [
                        img =
                            type: "div"
                            cls: "ui tiny image"
                            children:
                                type: "img"
                                src: "#{album.arturl}"
                        content =
                            type: "div"
                            id: "#{album.id}"
                            cls: "middle aligned content"
                            children: [
                                header =
                                    type: "div"
                                    cls: "header pl-text-thin"
                                    title: "#{album.name}"
                                meta =
                                    type: "div"
                                    cls: "meta"
                                    children:
                                        type: "span"
                                        cls: "artist"
                                        title: "#{album.artist}"
                                extra =
                                    type: "div"
                                    cls: "extra"
                                    children: [
                                        loader =
                                            type: "div"
                                            cls: "ui active small loader"
                                    ]
                            ]
                    ]
                    #like =
                    #    type: "div"
                    #    cls: "ui toggle blue tiny button"
                    #    title: "I like it"
                    #dislike =
                    #    type: "div"
                    #    cls: "ui toggle tiny button"
                    #    title: "I dont like it"
                items.push item
                # send request if exists
                artistname = @util.quote album.artist
                albumname = @util.quote album.name
                """
                @loader.sendrequest "get", "/api/exists?artist=#{artistname}&album=#{albumname}", {}, null,
                (code, res) ->
                    console.log res
                , (code, res) ->
                    console.log res
                """
            # assign all items to map
            map.children = items
        @mapper.parseMapForParent map, searchResults
    , (status, result) ->
        # error happened
        unsetLoading searchBox
        unlock searchInput
        # build map
        map =
            type: "div"
            cls: "ui pl-container-center compact basic segment"
            children:
                type: "div"
                cls: "ui header pl-text-thin"
                children: [
                    img =
                        type: "i"
                        cls: "trophy icon"
                    content =
                        type: "div"
                        cls: "content"
                        title: "Achievement unlocked"
                        children:
                            type: "div"
                            cls: "sub header"
                            title: "Your \"#{query}\" just set our server on fire. Thanks"
                ]

        @mapper.parseMapForParent map, searchResults

# add event listener on input box
util.addEventListener searchInput, "keypress", (e) ->
    searchQuery e.target.value if e.which == 13 or e.keyCode == 13
