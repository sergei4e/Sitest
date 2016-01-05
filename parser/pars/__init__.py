from lxml import html


def html_chenger(li):

    if type(li) in [str, unicode, int, float]:
        return li

    if type(li) is html.HtmlElement:
        li = html.tostring(li)
        return li

    if type(li) is list and len(li) == 1:
        li = li[0]
        if type(li) is html.HtmlElement:
            li = html.tostring(li)
        return li

    if li == list():
        return ''

    if type(li) is list:
        for i, el in enumerate(li):
            if type(el) in [str, unicode, int, float]:
                continue
            elif type(el) is html.HtmlElement:
                li[i] = html.tostring(el)
        return '; '.join(li)
    return None