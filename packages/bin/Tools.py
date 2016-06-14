__author__ = 'prologic'


class AttrIteration(object):
    def __iter__(self):
        for attr, value in self.__dict__.iteritems():
            yield attr, value