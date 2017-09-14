#!python3

import os
from blackmamba.project.index import Index
from blackmamba.config import get_config_value
import blackmamba.log as log
import blackmamba.ide as ide


class Project:
    _projects = {}

    def __init__(self, root):
        self._root = root
        self._project_folder = os.path.join(root, '.blackmamba')
        os.makedirs(self._project_folder, exist_ok=True)
        self._index = Index(self._project_folder)
        self._index.ignore_folders = ['.git', '.blackmamba']

    @classmethod
    def _find_root_folder(cls, path):
        while True:
            folder = os.path.dirname(path)

            if not folder or folder == '/':
                return None

            if os.path.isdir(os.path.join(folder, '.git')) or os.path.isdir(os.path.join(folder, '.blackmamba')):
                return folder

            path = folder

    @classmethod
    def by_path(cls, path):
        root = cls._find_root_folder(path)
        if not root:
            log.error('Unable to find project ({})'.format(path))
            return None

        project = cls._projects.get(root, None)
        if not project:
            project = Project(root)
            cls._projects[root] = project

        return project

    def reindex(self, force=False):
        self._index.index(force)
        if get_config_value('project.index.auto_save', True):
            self._index.save()

    def find_symbol_definition(self, name):
        ide.save()
        self.reindex()
        return self._index.find_symbol_locations(name)
