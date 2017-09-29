#!python3

import shutil
import os
import console

_ROOT_FOLDER = os.path.expanduser('~/Documents/site-packages-3/blackmamba')
_BACKUP_FOLDER = os.path.expanduser('~/Documents/site-packages-3/bm-pip-backup')
_GIT_FOLDER = os.path.expanduser('~/Documents/WorkingCopy/blackmamba')
_GIT_MODULE_FOLDER = os.path.join(_GIT_FOLDER, 'blackmamba')


def switch_to_working_copy():
    print('Switching Black Mamba to Working Copy version')

    if not os.path.isdir(_ROOT_FOLDER):
        print('Failed, folder does not exist: {}'.format(_ROOT_FOLDER))
        return

    if not os.path.isdir(_GIT_FOLDER):
        print('Failed, checkout Black Mamba to: {}'.format(_GIT_FOLDER))
        return

    if os.path.isdir(_BACKUP_FOLDER):
        print('Failed, backup folder exists: {}'.format(_BACKUP_FOLDER))
        return

    shutil.move(_ROOT_FOLDER, _BACKUP_FOLDER)

    if os.path.isdir(_ROOT_FOLDER):
        print('Failed, folder still exists: {}'.format(_ROOT_FOLDER))
        return

    os.symlink(_GIT_MODULE_FOLDER, _ROOT_FOLDER)

    if not os.path.islink(_ROOT_FOLDER):
        print('Failed, folder is not a symlink: {}'.format(_ROOT_FOLDER))
        return

    print('Black Mamba switched to Working Copy version')


def switch_to_installer():
    print('Switching Black Mamba to installer version')

    if not os.path.islink(_ROOT_FOLDER):
        print('Failed, folder is not a symlink: {}'.format(_ROOT_FOLDER))
        return

    if not os.path.isdir(_BACKUP_FOLDER):
        print('Failed, PIP backup folder does not exist: {}'.format(_BACKUP_FOLDER))
        return

    os.remove(_ROOT_FOLDER)
    shutil.move(_BACKUP_FOLDER, _ROOT_FOLDER)

    if not os.path.isdir(_ROOT_FOLDER):
        print('Failed, folder does not exists: {}'.format(_ROOT_FOLDER))
        return

    if os.path.isdir(_BACKUP_FOLDER):
        print('Failed, backup folder still does exist: {}'.format(_BACKUP_FOLDER))
        return

    print('Black Mamba switched to installer version')


def toggle():
    try:
        if os.path.islink(_ROOT_FOLDER):
            console.alert('Black Mamba',
                          'Switch to installer version?',
                          'OK')
            switch_to_installer()
        else:
            console.alert('Black Mamba',
                          'Switch to Working Copy version?',
                          'OK')
            switch_to_working_copy()
    except:
        pass


if __name__ == '__main__':
    toggle()
