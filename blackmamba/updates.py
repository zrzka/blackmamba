#!python3

from objc_util import ObjCClass, on_main_thread
import blackmamba.settings as settings
import time
import os
import json
import requests
import console

_DEFAULTS_LAST_UPDATE_CHECK_KEY = 'BlackMambaLastUpdateCheck'
_ROOT_DIR = os.path.expanduser('~/Documents/site-packages-3/blackmamba')
_RELEASE_PATH = os.path.join(_ROOT_DIR, '.release.json')
_OWNER = 'zrzka'
_REPOSITORY = 'blackmamba'


def _user_defaults():
    NSUserDefaults = ObjCClass('NSUserDefaults')
    return NSUserDefaults.standardUserDefaults()


@on_main_thread
def _get_last_update_check():
    return _user_defaults().integerForKey_(_DEFAULTS_LAST_UPDATE_CHECK_KEY)


@on_main_thread
def _set_last_update_check(timestamp):
    _user_defaults().setInteger_forKey_(timestamp, _DEFAULTS_LAST_UPDATE_CHECK_KEY)


def _timestamp():
    return int(time.time())


def _get_local_release():
    try:
        with open(_RELEASE_PATH, 'rt') as input:
            return json.load(input)
    except:
        pass


def _url(command):
    return 'https://api.github.com/repos/{}/{}/{}'.format(_OWNER, _REPOSITORY, command)


def _request(method, command):
    url = _url(command)
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }

    return requests.request(method, url, headers=headers)


def _get(command):
    return _request('GET', command)


def _get_json(command):
    return _get(command).json()


def _get_latest_release():
    try:
        return _get_json('releases/latest')
    except:
        pass


def check_for_updates():
    if not settings.CHECK_FOR_UPDATES:
        return

    timestamp = _timestamp()
#     last_check = timestamp - settings.CHECK_FOR_UPDATES_INTERVAL
    last_check = _get_last_update_check() or timestamp
    if last_check + settings.CHECK_FOR_UPDATES_INTERVAL > timestamp:
        return
    _set_last_update_check(timestamp)

    print('Checking for Black Mamba updates...')

    local_release = _get_local_release()
    latest_release = _get_latest_release()

    if local_release:
        print('Installed version {} (tag {})'.format(local_release['name'], local_release['tag_name']))

        if local_release['tag_name'] == latest_release['tag_name']:
            print('No updates available')
            return
    else:
        print('Missing installed version info, update recommended')

    console.alert('Black Mamba',
                  'New version {} available.'.format(latest_release['tag_name']),
                  'Got it!', hide_cancel_button=True)
