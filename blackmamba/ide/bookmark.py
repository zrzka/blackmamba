#!python3

import plistlib
import os
from objc_util import ns, NSURL
import blackmamba.system as system

_BOOKMARKS_FILE = os.path.expanduser('~/Bookmarks.plist')


@system.iOS('11.0')
def get_bookmark_paths():
    if not os.path.isfile(_BOOKMARKS_FILE):
        return None

    with open(_BOOKMARKS_FILE, 'rb') as input:
        content = plistlib.readPlist(input)

        if not content:
            return None

        paths = []
        for data in content:
            url = NSURL.URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_(
                ns(data.data), 1 << 8, None, None, None
            )
            if url and url.isFileURL():
                paths.append(str(url.path()))

        return paths
