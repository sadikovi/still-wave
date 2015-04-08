class Mapper
    constructor: ->

    # just creates element and assigns to parent
    createElement: (type, parent) ->
        t = document.createElement type
        parent.appendChild t

    # parses map for parent specified
    # does not do anything, if map or parent is undefined
    parseMapForParent: (map, parent, assign=false) ->
        # mappers
        mprs =
            type: 'type'
            cls: 'cls'
            id: 'id'
            title: 'title'
            href: 'href'
            src: 'src'
            inputvalue: 'inputvalue'
            inputtype: 'inputtype'
            optionselected: 'optionselected'
            children: 'children'
        # return of something is wrong
        return false unless map and parent
        # map can be object or array
        if mprs.type of map
            # create object and add to parent
            c = @.createElement map[mprs.type], parent
            c.id = map[mprs.id] if mprs.id of map
            c.className = map[mprs.cls] if mprs.cls of map
            c.innerHTML = map[mprs.title] if mprs.title of map
            c.href = map[mprs.href] if mprs.href of map
            c.src = map[mprs.src] if mprs.src of map
            # input parameters
            c.value = map[mprs.inputvalue] if mprs.inputvalue of map
            c.type = map[mprs.inputtype] if mprs.inputtype of map
            c.selected = map[mprs.optionselected] if mprs.optionselected of map
            # assign element back to map if permitted
            map._element_ = c if assign
            @parseMapForParent map[mprs.children], c if mprs.children of map
        else
            @parseMapForParent item, parent for item in map

# create global mapper
@mapper ?= new Mapper
