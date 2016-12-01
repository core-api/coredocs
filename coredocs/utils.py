def link_sort(link_item):
    key, link = link_item
    action_priority = {
        '': 0, 'get': 0,
        'post': 1,
        'put': 2,
        'patch': 3,
        'delete': 4
    }.get(link.action, 5)
    return (link.url, action_priority)


def get_sections(node):
    return sorted(node.data.iteritems(), key=lambda item: item[0])


def get_links(node):
    return sorted(node.links.iteritems(), key=link_sort)
