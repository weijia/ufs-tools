# -*- coding: utf8 -*-
import os
try:
    import urllib2
except:
    import urllib.parse as urllib2
import sys
import re

try:
    a = unicode("")
except:
    unicode = str


# noinspection PyMethodMayBeStatic
class SpecialEncoder(object):
    def encode(self, unicode_str):
        if unicode != type(unicode_str):
            raise 'Only support unicode string'
        return unicode_str.replace(u"\\", u"\\\\").replace(u"&", u"\\x%02x" % ord('&')).replace("?",
                                                                                                "\\x%02x" % ord('?'))

    def decode(self, unicode_str):
        if unicode != type(unicode_str):
            raise 'Only support unicode string'
        return unicode_str.replace(u"\\x%02x" % ord('&'), u"&").replace("\\x%02x" % ord('?'), u'?').replace(u"\\",
                                                                                                            u"\\\\")


def quote_unicode(unicode_str):
    if unicode != type(unicode_str):
        raise "Only support unicode string"
    res = urllib2.quote(unicode_str.encode('utf8'))
    # cl("input:", unicode_str, "output:", res)
    return res


def unquote_unicode(quoted_str):
    # cl(urllib2.unquote(quoted_str))
    # cl("input:", quoted_str)
    # We must encode the quoted_str to utf8 so urllib2.unquote will return utf8. Otherwise, it will return
    # unicode and unicode can not be decoded as utf8.
    if unicode == type(quoted_str):
        quoted_str = quoted_str.encode('utf8')
    result = urllib2.unquote(quoted_str)
    # cl(type(result))
    # cl(result.encode('gbk'))
    result = result.decode('utf8')
    # cl("output:", result)
    return result


def split_with_chars(s, separator_list):
    """
    Separate string with multiple chars, such as ",\r\n\t" etc
    """
    r = [s]
    for i in separator_list:
        t = []
        for j in r:
            t.extend(j.split(i))
        r = t
    return r


class SpecialEncodingError(Exception):
    pass


class NonUnicodeError(Exception):
    pass


'''
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
If there is a number that following the removing Char will cause problem if the length of the numbers for the escaped char.

For exsample: ":" is the removing char, "\\" is the escapeChar, then ":12" will cause problem. Solution is to use fixed length of number for escaped char.
'''


def decodeChar(matchobj):
    v = matchobj.group(0)
    print >> sys.stderr, "--------" + matchobj
    return unichr(int(v[1:]))


def l(s):
    # print >>sys.stderr, s
    # print s
    pass


class SpecialEncoding:
    def __init__(self, removingChars, escapeChar):
        '''
        All removing chars should be unicode
        '''
        if type(removingChars) != list:
            raise SpecialEncodingError
        for i in removingChars:
            if type(i) != unicode:
                raise NonUnicodeError
        if type(escapeChar) != unicode:
            raise NonUnicodeError
        self.removingChars = removingChars
        self.escapeChar = escapeChar
        self.escapeCharNumLen = (len(removingChars) / 20) + 1

    def en(self, s):
        """
        \\a->\\\\a
        b->\98#b's ascii is 98
        """
        if type(s) != unicode:
            raise NonUnicodeError
        s = s.replace(self.escapeChar, self.escapeChar + self.escapeChar)
        cnt = 0
        for i in self.removingChars:
            # print s
            s = s.replace(i, self.escapeChar + u'0' * (self.escapeCharNumLen - len(str(cnt))) + unicode(str(cnt)))
            # print 'after replace:%s, %s'%(i, s)
            cnt += 1
        return s

    def de(self, s):
        if type(s) != unicode:
            raise NonUnicodeError
            # s = re.sub("\\[0-9]+", decodeChar, s)
        state = 0  # 0: normal, 1: one escapeChar received, 2: number received
        r = u""
        num = u""
        for i in s:
            l(u"processing char:" + i)
            if state == 0:
                if i == self.escapeChar:
                    l(u"i is escapeChar")
                    state = 1
                    continue
                else:
                    r += i
                    continue
            if state == 1:
                if i == self.escapeChar:
                    r += self.escapeChar
                    state = 0
                    continue
                else:
                    l("current length:" + str(len(num)))
                    l(u"collecting:" + i)
                    num += i
                    if len(num) == self.escapeCharNumLen:
                        l(u"generating:" + num)
                        r += self.removingChars[int(num)]
                        num = u""
                        state = 0

        # print >>sys.stderr, s
        # s = s.replace(self.escapeChar+self.escapeChar, self.escapeChar)
        return r


# Jquery does not support ":","\"?
# Python 2.7 does not support param with '/'
gEscaping = [u":", u"/"]

'''
def jsIdEncoding(s):
    #####################
    #This function is used to encode the item id of jstree as jstree can not manipulate id with ":" correctly
    #
    #return s
    l = s.split(u":", 1)
    if len(l[0]) == 1:
        s = "_".join(l)
    return s

'''


def jsIdEncoding(s):
    """
    This function is used to encode the item id of jstree as jstree can not manipulate id with ":" correctly
    """
    e = SpecialEncoding(gEscaping, u"_")
    return e.en(s)


def jsIdDecoding(s):
    e = SpecialEncoding(gEscaping, u"_")
    # print e.de(s)
    return e.de(s)


if __name__ == '__main__':
    v = u"hello\rgoodmorning\thi,,"
    # print 'separating:', v
    print(split_with_chars(v, u"\r\t\n,"))
    v = u"go\\\\od:ba/d"
    s = SpecialEncoding([u":", u"/"], u"\\")
    print(v)
    print(s.en(v))
    print(s.de(v))
    v = u"D:/"
    print('---------------------------------')
    s = SpecialEncoding([u":", u"/"], u"\\")
    print(v)
    print(s.en(v))
    print(s.de(v))
    print('--------------------------------')
    print(jsIdEncoding(u"local_filesystem://D:/"))
    print('--------------------------------')
    print(jsIdDecoding(u"ufsFs\\0//q19420-01/D\\0/"))

    # encoded_str = quote_unicode(u"中文")
    # res = unquote_unicode('system_rest/%3Ffull_path%3DE%3A%5C%E5%BF%AB%E7%9B%98')
    res = unquote_unicode('local_filesystem%3A//E%3A%5C%E5%BF%AB%E7%9B%98')
    print(type(res))
    # print os.path.exists(res.split('=')[1])
    print(os.path.exists(res.split('//')[1]))


def class_name_to_low_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def is_none_or_empty(input_str):
    if input_str is None or input_str == '':
        return True

    return False
