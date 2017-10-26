#!python3

import requests
import os
import sys
import console
import zipfile
import shutil
import json

_OWNER = 'zrzka'
_REPOSITORY = 'blackmamba'

_TMP_DIR = os.environ.get('TMPDIR', os.environ.get('TMP'))
_TMP_TARGET_DIR = os.path.expanduser('~/Documents/site-packages-3/.blackmamba-install')
_TARGET_DIR = os.path.expanduser('~/Documents/site-packages-3/blackmamba')
_RELEASE_INFO_FILE = os.path.join(_TARGET_DIR, '.release.json')


_cleanup_paths = []


def _get_version(release):
    version = release['tag_name']
    if version.startswith('v'):
        version = version[1:]
    return version


def _cleanup():
    global _cleanup_paths

    if _cleanup_paths:
        for path in _cleanup_paths:
            if not os.path.exists(path):
                continue

            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception:
                pass

    _cleanup_paths = None


def _info(message):
    print(message)


def _error(message):
    sys.stderr.write('{}\n'.format(message))


def _terminate(message):
    _error(message)
    _cleanup()
    sys.exit(1)


def _url(command):
    return 'https://api.github.com/repos/{}/{}/{}'.format(_OWNER, _REPOSITORY, command)


def _request(method, command):
    url = _url(command)

    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.request(method, url, headers=headers)

    if not response.ok:
        _terminate('GitHub command {} failed with status code {}'.format(command, response.status_code))

    return response


def _get(command):
    return _request('GET', command)


def _get_json(command):
    try:
        return _get(command).json()

    except Exception as e:
        _error('{}\n'.format(e))
        _terminate('Failed to parse JSON from GitHub response')


def _get_latest_release(prerelease=False):
    # GitHub doesn't return drafts / prereleases, we just get
    # the latest release
    _info('Checking latest Black Mamba release...')
    if prerelease:
        releases = _get_json('releases')
        if not releases:
            return None
        release = releases[0]
    else:
        release = _get_json('releases/latest')
    _info('Latest release {} (tag {}) found'.format(release['name'], release['tag_name']))
    return release


def _download_release_zip(release):
    _info('Downloading ZIP...')

    name = release['name']
    path = os.path.join(_TMP_DIR, '{}-{}.zip'.format(_REPOSITORY, name))

    _cleanup_paths.append(path)

    response = requests.get(release['zipball_url'], stream=True)

    console.show_activity()
    if not response.ok:
        console.hide_activity()
        _terminate('GitHub ZIP ball request failed with {}'.format(response.status_code))

    try:
        with open(path, 'wb') as output:
            for data in response.iter_content(8192):
                output.write(data)
    except Exception as e:
        console.hide_activity()
        _error(e)
        _terminate('Failed to save ZIP file')

    console.hide_activity()
    return path


def _prepare_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)

    os.makedirs(path)


def _extract_file(zip_file, zip_file_name, file_name):
    if file_name.endswith('/'):
        if not os.path.exists(file_name):
            os.makedirs(file_name)
    else:
        data = zip_file.read(zip_file_name)
        with open(file_name, 'wb') as output:
            output.write(data)


def _extract_release(release, path):
    _info('Extracting ZIP archive...')

    _cleanup_paths.append(_TMP_TARGET_DIR)

    try:
        _prepare_dir(_TMP_TARGET_DIR)

        with open(path, 'rb') as input:
            zf = zipfile.ZipFile(input)

            top_level_dir = None
            for name in zf.namelist():
                if not top_level_dir and name.endswith('/'):
                    top_level_dir = name
                    continue

                if not top_level_dir:
                    continue

                # Strip top level ZIP directory
                stripped_name = name[len(top_level_dir):]

                if not stripped_name.startswith('blackmamba/'):
                    continue

                # Strip blackmamba/ directory
                stripped_name = stripped_name[len('blackmamba/'):]

                file_name = os.path.join(_TMP_TARGET_DIR, stripped_name)
                _extract_file(zf, name, file_name)

            if not top_level_dir:
                _terminate('Failed to extract ZIP file')

    except Exception as e:
        _error(e)
        _terminate('Failed to extract ZIP file')

    return _TMP_TARGET_DIR


def _move_to_site_packages(extracted_zip_dir):
    _info('Moving to site-packages-3 {}...'.format(_TARGET_DIR))

    try:
        if os.path.exists(_TARGET_DIR):
            shutil.rmtree(_TARGET_DIR)
        shutil.move(extracted_zip_dir, _TARGET_DIR)
    except Exception as e:
        _error(e)
        _terminate('Failed to move Black Mamba to site-packages-3')


def _local_installation_exists(release):
    _info('Checking Black Mamba installation...')

    if os.path.islink(_TARGET_DIR):
        _terminate('Skipping, Black Mamba symlinked to site-packages-3')

    local_version = None
    try:
        import blackmamba
        local_version = blackmamba.__version__
        _info('Black Mamba {} installed'.format(local_version))

    except ModuleNotFoundError:
        _info('Black Mamba not installed')

    if local_version is not None:
        remote_version = _get_version(release)

        try:
            if remote_version == local_version:
                console.alert(
                    'Black Mamba Installer',
                    'Black Mamba {} installed. Do you want to replace it with {}?'.format(local_version, remote_version),
                    'Replace'
                )
            else:
                console.alert(
                    'Black Mamba Installer',
                    'Black Mamba {} installed. Do you want to update it to {}?'.format(local_version, remote_version),
                    'Update'
                )

        except KeyboardInterrupt:
            _terminate('Cancelling installation on user request')


def _save_release_info(release):
    _info('Saving installed version release info')

    try:
        with open(_RELEASE_INFO_FILE, 'w') as output:
            json.dump(release, output)
    except Exception as e:
        _error(e)
        _terminate('Failed to save installed version release info')


def _install(prerelease=False):
    release = _get_latest_release(prerelease)
    if not release:
        _error('Unable to find latest release')
        return
    _local_installation_exists(release)
    path = _download_release_zip(release)
    extracted_zip_dir = _extract_release(release, path)
    _move_to_site_packages(extracted_zip_dir)
    _save_release_info(release)
    _cleanup()
    _info('Black Mamba {} installed'.format(_get_version(release)))

    console.alert(
        'Black Mamba {} Installed'.format(_get_version(release)),
        'Pythonista RESTART is required for changes to take effect.',
        'Got it!', hide_cancel_button=True
    )


if __name__ == '__main__':
    _install()
