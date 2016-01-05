def empty_string(string):
    if string is None:
        return ''
    else:
        return string


def difference(string1, string2):

    string1, string2 = empty_string(string1), empty_string(string2)

    string1, string2 = string1.replace(u'\n', ''), string2.replace(u'\n', '')
    string1, string2 = string1.replace(u'<', u'&lt;'), string2.replace(u'>', u'&gt;')
    string1, string2 = string1.replace(u'>', u'&gt;'), string2.replace(u'<', u'&lt;')

    start = u'<span style="background-color: red">'
    end = u'</span>'

    if len(string1) > len(string2):
        a = string2
    else:
        a = string1

    for i in range(len(a)):
        if string1[i:i+1:] != string2[i:i+1:]:
            string1 = string1[:i] + start + string1[i:]
            string2 = string2[:i] + start + string2[i:]
            break

    for i in range(len(a)):
        if string1[::-1][i:i+1:] != string2[::-1][i:i+1:]:
            string1 = (string1[::-1][:i] + end[::-1] + string1[::-1][i:])[::-1]
            string2 = (string2[::-1][:i] + end[::-1] + string2[::-1][i:])[::-1]
            break

    return string1, string2

'''
a = 'asdasdadsasdasdasd'
b = 'asdasdasdasdqwrwqrqwr'

print difference(a, b)
'''