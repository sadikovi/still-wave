# just collection of objects to map as DOM elements
class Collection
    constructor: ->

    searchUnauthorised: ->
        map =
            type: "div"
            cls: "ui pl-container-center compact basic segment"
            children:
                type: "div"
                cls: "ui header pl-text-thin"
                children: [
                    img =
                        type: "i"
                        cls: "lock icon"
                    content =
                        type: "div"
                        cls: "content"
                        title: "Not authorised"
                        children:
                            type: "div"
                            cls: "sub header"
                            title: "You are not authorised. "
                            children:
                                type: "a"
                                title: "Authorise"
                                href: "/login"
                ]

    searchFailed: (query) ->
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

    searchNothing: ->
        map =
            type: "div"
            cls: "pl-text-center"
            children:
                type: "div"
                cls: "pl-text-large"
                title: "Nothing was found. Try again :-("


    controlPanel: ->
        extra =
            type: "div"
            cls: "extra"
            children:[]

    notFoundLabel: ->
        label =
            type: "span"
            cls: "ui red label"
            title: "Not found on Pandora"


    itemContent: (header, meta) ->
        content =
            type: "div"
            cls: "middle aligned content"
            children: [
                header =
                    type: "div"
                    cls: "header pl-text-thin"
                    title: "#{header}"
                meta =
                    type: "div"
                    cls: "meta"
                    children:
                        type: "span"
                        cls: "artist"
                        title: "#{meta}"
            ]
    itemImage: (imageurl) ->
        img =
            type: "div"
            cls: "ui tiny image"
            children:
                type: "img"
                src: "#{imageurl}"

    item: ->
        item =
            type: "div"
            cls: "item"
            children: []

    like: (title) ->
        like =
            type: "div"
            cls: "ui tiny toggle button"
            title: title

    dislike: (title) ->
        like =
            type: "div"
            cls: "ui tiny toggle button"
            title: title

    statusLabel: (title) ->
        label =
            type: "span"
            cls: "ui label"
            title: title

    pagesContainer: (pages) ->
        container =
            type: "div"
            cls: "ui breadcrumb"
            children: pages ? []

    page: (num, isactive) ->
        page =
            type: if isactive then "div" else "a"
            cls: if isactive then "active section" else "section"
            title: "#{num}"

    divider: (sym) ->
        divider =
            type: "div"
            cls: "divider"
            title: "#{sym}"


@collection ?= new Collection
