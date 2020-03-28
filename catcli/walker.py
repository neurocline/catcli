"""
author: deadc0de6 (https://github.com/deadc0de6)
Copyright (c) 2017, deadc0de6

Catcli filesystem indexer
"""

import os

# local imports
from catcli.logger import Logger


class Walker:

    MAXLINE = 80 - 15

    def __init__(self, noder, nohash=False, debug=False):
        self.noder = noder
        self.nohash = nohash
        self.noder.set_hashing(not self.nohash)
        self.debug = debug

    def index(self, path, parent, name, storagepath=''):
        '''index a directory and store in tree'''
        self._debug('indexing starting at {}'.format(path))
        if not parent:
            parent = self.noder.dir_node(name, path, parent)

        cnt = 0
        for (root, dirs, files) in os.walk(path):
            for f in files:
                self._debug('found file {} under {}'.format(f, path))
                sub = os.path.join(root, f)
                self._log(f)
                self._debug('index file {}'.format(sub))
                self.noder.file_node(os.path.basename(f), sub,
                                     parent, storagepath)
                cnt += 1
            for d in dirs:
                self._debug('found dir {} under {}'.format(d, path))
                base = os.path.basename(d)
                sub = os.path.join(root, d)
                self._debug('index directory {}'.format(sub))
                dummy = self.noder.dir_node(base, sub, parent, storagepath)
                cnt += 1
                nstoragepath = os.sep.join([storagepath, base])
                if not storagepath:
                    nstoragepath = base
                _, cnt2 = self.index(sub, dummy, base, nstoragepath)
                cnt += cnt2
            break
        self._log(None)
        return parent, cnt

    def reindex(self, path, parent, top):
        '''reindex a directory and store in tree'''
        cnt = self._reindex(path, parent, top)
        cnt += self.noder.clean_not_flagged(parent)
        return cnt

    def _reindex(self, path, parent, top, storagepath=''):
        '''
        reindex a directory and store in tree
        @path: directory path to re-index
        @top: top node (storage)
        @storagepath: rel path relative to indexed directory
        '''
        self._debug('reindexing starting at {}'.format(path))
        cnt = 0
        for (root, dirs, files) in os.walk(path):
            for f in files:
                self._debug('found file \"{}\" under {}'.format(f, path))
                sub = os.path.join(root, f)
                treepath = os.path.join(storagepath, f)
                reindex, n = self._need_reindex(parent, sub, treepath)
                if not reindex:
                    self._debug('\tskip file {}'.format(sub))
                    self.noder.flag(n)
                    continue
                Logger.out('- new file \"{}\"'.format(sub))
                n = self.noder.file_node(os.path.basename(f), sub,
                                         parent, storagepath)
                self.noder.flag(n)
                cnt += 1
            for d in dirs:
                self._debug('found dir \"{}\" under {}'.format(d, path))
                base = os.path.basename(d)
                sub = os.path.join(root, d)
                treepath = os.path.join(storagepath, d)
                reindex, dummy = self._need_reindex(parent, sub, treepath)
                if reindex:
                    Logger.out('- new directory \"{}\"'.format(sub))
                    dummy = self.noder.dir_node(base, sub, parent, storagepath)
                    cnt += 1
                self.noder.flag(dummy)
                self._debug('reindexing deeper under {}'.format(sub))
                nstoragepath = os.sep.join([storagepath, base])
                if not storagepath:
                    nstoragepath = base
                cnt2 = self._reindex(sub, dummy, top, nstoragepath)
                cnt += cnt2
            break
        self._log(None)
        return cnt

    def _need_reindex(self, top, path, treepath):
        '''
        test if node needs re-indexing
        @top: top node (storage)
        @path: abs path to file
        @treepath: rel path from indexed directory
        '''
        cnode, changed = self.noder.get_node_if_changed(top, path, treepath)
        if not cnode:
            self._debug('\t{} does not exist'.format(path))
            return True, cnode
        if cnode and not changed:
            # ignore this node
            self._debug('\t{} has not changed'.format(path))
            return False, cnode
        if cnode and changed:
            # remove this node and re-add
            self._debug('\t{} has changed'.format(path))
            self._debug('\tremoving node {} for {}'.format(cnode.name, path))
            cnode.parent = None
        Logger.out('- update \"{}\"'.format(path))
        return True, cnode

    def _debug(self, string):
        if not self.debug:
            return
        Logger.debug(string)

    def _log(self, string):
        if self.debug:
            return
        if not string:
            # clean
            Logger.progr('{:80}'.format(' '))
            return
        if len(string) > self.MAXLINE:
            string = string[:self.MAXLINE] + '...'
        Logger.progr('indexing: {:80}'.format(string))
