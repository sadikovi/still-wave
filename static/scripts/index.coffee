# search
searchBox = document.getElementById "sw-search-box"
searchInput = document.getElementById "sw-search-box-input"
searchResults = document.getElementById "sw-search-results"
searchPages = document.getElementById "sw-search-pages"
throw "No binding elements found" unless searchBox and searchInput and searchResults and searchPages

lock = (elem) -> elem.setAttribute "disabled", "true"
unlock = (elem) -> elem.removeAttribute "disabled"
clear = (elem) -> elem.innerHTML = ""
setLoading = (elem) -> @util.addClass elem, "loading"
unsetLoading = (elem) ->@util.removeClass elem, "loading"

# status messages
_statusReset = _statusLike = _statusDislike = "Like it?"
_statusError = "Error! No panic, we deal with it"
# like messages
_likeTitle = _likeActiveTitle = ":-)"
# dislike messages
_dislikeTitle = _dislikeActiveTitle = ":-("

makeActive = (activebtn, disabledbtn, activeText, disabledText, isLoading) ->
    return false if @util.hasClass activebtn, "active"
    # otherwise remove active class and add disabled class
    @util.removeClass activebtn, "active", "loading"
    @util.addClass activebtn, "disabled"
    @util.removeClass disabledbtn, "active", "loading"
    @util.addClass disabledbtn, "disabled"
    activebtn.innerHTML = activeText if activeText
    disabledbtn.innerHTML = disabledText if disabledText
    # set active button as loading or active
    @util.removeClass activebtn, "disabled"
    @util.removeClass disabledbtn, "disabled" if not isLoading
    @util.addClass activebtn, if isLoading then "loading" else "active"
    return true

reset = (btn, text) ->
    @util.removeClass btn, "active", "loading", "disabled"
    btn.innerHTML = text if text

lockButton = (btn, text) ->
    reset btn, text
    @util.addClass btn, "disabled"
    btn.innerHTML = text if text

controlPanelErrorLock = (controlpanel) ->
    lockButton controlpanel._like
    lockButton controlpanel._dislike
    controlpanel._status.innerHTML = _statusError
    @util.addClass controlpanel._status, "red"

searchQuery = (query, page=1) ->
    setLoading searchBox
    lock searchInput
    clear searchResults
    clear searchPages
    @api.search @loader, @util.quote(query), @util.quote(page), (status, result) ->
        unsetLoading searchBox
        unlock searchInput
        data = JSON.parse(result).data
        [albums, page, pages, maxpage] = [data.results, data.page, data.pages, data.maxpage]
        # build albums
        if not @util.isArray(albums)
            @mapper.parseMapForParent @collection.searchFailed(query), searchResults
        else if albums.length == 0
            # nothing is found
            @mapper.parseMapForParent @collection.searchNothing(), searchResults
        else
            map =
                type: "div"
                cls: "ui divided items"
            items = []
            for album in albums
                # build control panel
                controlPanel = @collection.controlPanel()
                if not album.id or not album.ispandora
                    # return label "Not found on Pandora"
                    label = @collection.notFoundLabel()
                    controlPanel.children.push label
                else
                    # build control panel
                    like = @mapper.parseMapForParent @collection.like(_likeTitle), null
                    dislike = @mapper.parseMapForParent @collection.dislike(_dislikeTitle), null
                    status = @mapper.parseMapForParent @collection.statusLabel(_statusReset), null
                    controlPanel.children.push status, like, dislike
                    # creating DOM control panel
                    controlPanel = @mapper.parseMapForParent controlPanel, null
                    # adding albumid as attribute
                    controlPanel._albumid = album.id
                    # like and dislike buttons, status
                    [controlPanel._like, controlPanel._dislike, controlPanel._status] = [like, dislike, status]
                    like._controlPanel = dislike._controlPanel = status._controlPanel = controlPanel
                    # make them liked or disliked once they are loaded
                    if album.liked == true
                        makeActive controlPanel._like, controlPanel._dislike, _likeActiveTitle, _dislikeTitle, false
                    if album.liked == false
                        makeActive controlPanel._dislike, controlPanel._like, _dislikeActiveTitle, _likeTitle, false
                    # add event listeners
                    @util.addEventListener like, "click", (e)=>
                        controlpanel = e.target._controlPanel
                        fl = makeActive controlpanel._like, controlpanel._dislike, _likeActiveTitle, _dislikeTitle, true
                        if not fl
                            @api.reset @loader, @util.quote(controlpanel._albumid), (status, result) -> reset controlpanel._like, _likeTitle
                            , (status, result) -> controlPanelErrorLock controlpanel
                        else
                            @api.like @loader, @util.quote(controlpanel._albumid), (status, result) ->
                                controlpanel._status.innerHTML = _statusLike
                                makeActive controlpanel._like, controlpanel._dislike, _likeActiveTitle, _dislikeTitle, false
                            , (status, result) -> controlPanelErrorLock controlpanel

                    @util.addEventListener dislike, "click", (e)=>
                        controlpanel = e.target._controlPanel
                        fl = makeActive controlpanel._dislike, controlpanel._like, _dislikeActiveTitle, _likeTitle, true
                        if not fl
                            @api.reset @loader, @util.quote(controlpanel._albumid), (status, result) ->
                                controlpanel._status.innerHTML = _statusReset
                                reset controlpanel._dislike, _dislikeTitle
                            , (status, result) -> controlPanelErrorLock controlpanel
                        else
                            @api.dislike @loader, @util.quote(controlpanel._albumid), (status, result) ->
                                controlpanel._status.innerHTML = _statusDislike
                                makeActive controlpanel._dislike, controlpanel._like, _dislikeActiveTitle, _likeTitle, false
                            , (status, result) -> controlPanelErrorLock controlpanel
                # content
                itemContent = @collection.itemContent(album.name, album.artist)
                itemContent.children.push controlPanel
                item = @collection.item()
                item.children.push @collection.itemImage(album.arturl), itemContent
                items.push item
            # assign all items to map
            map.children = items
        @mapper.parseMapForParent map, searchResults
        # build pages navigation
        return false if maxpage == 0
        brpages = []
        for pg, i in pages
            tdom = @mapper.parseMapForParent @collection.page(pg, page==pg), null
            tdom._page = pg
            @util.addEventListener tdom, "click", (e) -> searchQuery(query, @_page)
            brpages.push tdom, @collection.divider(if i < pages.length-1 then "-" else "")
        @mapper.parseMapForParent @collection.pagesContainer(brpages), searchPages
    , (status, result) ->
        # error happened
        unsetLoading searchBox
        unlock searchInput
        # build map
        @mapper.parseMapForParent @collection.searchFailed(query), searchResults

# add event listener on input box
util.addEventListener searchInput, "keypress", (e) ->
    searchQuery e.target.value if e.which == 13 or e.keyCode == 13
