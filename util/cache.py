# -*- coding: utf-8 -*-
"""
cache module
文件缓存
"""

from __future__ import print_function
import logging as LOG
import os
import pickle
import time

try:
    from collections.abc import MutableMapping
except ImportError:
    # Python 2 imports
    from collections import MutableMapping


class Cache(MutableMapping):
    """
    using file to Cache data as dictionary
    """

    def __init__(self, path, sync=False):
        self.__data = {}
        self.__filename = path
        self.__sync = sync
        self.__time = time.time()
        self.__changed = False
        self.load()

    @property
    def time(self):
        """
        缓存修改时间
        """
        return self.__time

    def load(self, path=None):
        """
        load data from path
        """
        if not path:
            path = self.__filename

        LOG.debug('load cache data from %s', path)
        if os.path.isfile(path):
            with open(self.__filename, 'rb') as data:
                try:
                    self.__data = pickle.load(data)
                    self.__time = os.stat(path).st_mtime
                except ValueError:
                    self.__data = {}
                    self.__time = time.time()
                except Exception as e:
                    print(e)
                    self.__data = {}
                    self.__time = time.time()
        else:
            LOG.info('cache file not exist')
            self.__data = {}
            self.__time = time.time()
        return self

    def data(self, key=None, default=None):
        """
        获取当前字典或者制定得键值
        """
        if self.__sync:
            self.load()

        if key is None:
            return self.__data
        else:
            return self.__data.get(key, default)

    def sync(self):
        """Sync the write buffer with the cache files and clear the buffer.
        """
        if self.__changed:
            with open(self.__filename, 'wb') as data:
                pickle.dump(self.__data, data)
                LOG.debug('save cache data to %s', self.__filename)
            self.__time = time.time()
            self.__changed = False
        return self

    def close(self):
        """Sync the write buffer, then close the cache.
        If a closed :class:`FileCache` object's methods are called, a
        :exc:`ValueError` will be raised.
        """
        self.sync()
        del self.__data
        del self.__filename
        del self.__time
        self.__sync = False

    def __update(self):
        self.__changed = True
        if self.__sync:
            self.sync()
        else:
            self.__time = time.time()

    def clear(self):
        if self.data():
            self.__data = {}
            self.__update()

    def __setitem__(self, key, value):
        if self.data(key) != value:
            self.__data[key] = value
            self.__update()

    def __delitem__(self, key):
        if key in self.data():
            del self.__data[key]
            self.__update()

    def __getitem__(self, key):
        return self.data(key)

    def __iter__(self):
        for key in self.data():
            yield key

    def __len__(self):
        return len(self.data())

    def __contains__(self, key):
        return key in self.data()

    def __str__(self):
        return self.data().__str__()

    def __del__(self):
        self.close()


def main():
    """
    test
    """
    LOG.basicConfig(level=LOG.DEBUG)
    cache = Cache('test.txt')
    print(cache, cache.time)
    cache['s'] = 'a'
    print(cache['s'], cache.time)


if __name__ == '__main__':
    main()
