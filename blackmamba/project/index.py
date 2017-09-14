#!python3

import os
import blackmamba.log as log
from blackmamba.config import get_config_value
from enum import IntEnum
import ast
import pickle
import time


class SymbolType(IntEnum):
    class_definition = 1 << 0
    function_definition = 1 << 1

    @classmethod
    def from_ast_instance(cls, o):
        if isinstance(o, ast.ClassDef):
            return SymbolType.class_definition
        elif isinstance(o, ast.FunctionDef):
            return SymbolType.function_definition
        return None


class Symbol:
    def __init__(self, type_, name, line, column):
        self.type_ = type_
        self.name = name
        self.line = line
        self.column = column

    def __repr__(self):
        return '<Symbol {}:{}:{}:{}>'.format(self.type_, self.name, self.line, self.column)


class FileIndex:
    def __init__(self, path, symbols, last_modification):
        self._path = path
        self._symbols = symbols
        self._last_modification = last_modification

    @property
    def path(self):
        return self._path

    @property
    def symbols(self):
        return self._symbols

    @property
    def last_modification(self):
        return self._last_modification

    def update(self, symbols, last_modification):
        self._symbols = symbols
        self._last_modification = last_modification


class Indexer:
    supported_extensions = None

    def index_file(self, path):
        raise NotImplementedError

    def can_index_file(self, path):
        _, ext = os.path.splitext(path)
        return ext.lower() in self.supported_extensions


class PythonIndexer(Indexer):
    supported_extensions = ['.py']

    def index_file(self, path):
        log.debug('Indexing file: {}'.format(path))

        try:
            text = open(path, "r").read()
            return self._generate_symbols(ast.parse(text))
        except Exception:
            log.debug('Failed to read file: {}'.format(path))

        return None

    def _generate_symbols(self, parent):
        symbols = []

        for child in parent.body:
            type_ = SymbolType.from_ast_instance(child)

            if not type_:
                continue

            symbol = Symbol(type_, child.name, child.lineno, child.col_offset)
            symbols.append(symbol)

            child_symbols = self._generate_symbols(child)
            if child_symbols:
                symbols.extend(child_symbols)

        return symbols


class Index:
    _indexer = None

    def __init__(self, project_folder):
        self._project_folder = project_folder
        self._root = os.path.dirname(self._project_folder)
        self._index = self._load_index(self._project_folder) or {}
        self._last_update = time.time() if self._index else 0
        self.ignore_folders = None

    @classmethod
    def _index_cache_path(cls, project_folder):
        return os.path.join(project_folder, 'index.pickle')

    @classmethod
    def _load_index(cls, project_folder):
        path = cls._index_cache_path(project_folder)
        log.debug('Loading index ({})'.format(path))

        if not os.path.isfile(path):
            log.debug('Skipping, index file does not exist')
            return None

        try:
            with open(path, 'rb') as input:
                return pickle.load(input)
        except Exception:
            log.error('Failed to load index, removing it')
            os.remove(path)

        return None

    def save(self):
        path = self._index_cache_path(self._project_folder)
        log.debug('Saving index ({})'.format(path))

        os.makedirs(self._project_folder, exist_ok=True)

        try:
            with open(path, 'wb') as output:
                pickle.dump(self._index, output)
        except Exception as e:
            log.error('Failed to save index')
            log.error(e)

    def _find_indexer(self, path):
        if not self._indexer:
            self._indexer = PythonIndexer()

        if self._indexer.can_index_file(path):
            return self._indexer

        return None

    def _is_project_file(self, path):
        return path.startswith(self._root)

    def index_file(self, path):
        if not self._is_project_file(path):
            raise ValueError('File outside of project root is not supported')

        indexer = self._find_indexer(path)

        if not indexer:
            log.debug('Unable to find indexer for file: {}'.format(path))
            return

        symbols = indexer.index_file(path)

        if not symbols:
            self._index.pop(path, None)
        else:
            index = self._index.get(path, None)
            if not index:
                index = FileIndex(path, symbols, os.path.getmtime(path))
            else:
                index.update(symbols, os.path.getmtime(path))
            self._index[path] = index

    def index(self, force=False):
        now = time.time()
        if not force and self._last_update + get_config_value('project.index.rate', 60) > now:
            log.debug('Skipping indexing, index too young')
            return

        log.debug('Indexing project ...')
        self._last_update = now

        for path in list(self._index.keys()):
            if not os.path.isfile(path):
                log.debug('Removing file, no longer exists ({})'.format(path))
                self._index.pop(path, None)

        for root, subdirs, files in os.walk(self._root, topdown=True, followlinks=True):
            if self.ignore_folders:
                subdirs[:] = [sd for sd in subdirs if sd not in self.ignore_folders]

            for file in files:
                path = os.path.join(root, file)

                should_index = force

                if not should_index:
                    file_index = self._index.get(path, None)
                    if file_index:
                        should_index = not os.path.getmtime(path) == file_index.last_modification
                    else:
                        should_index = True

                if not should_index:
                    log.debug('Skipping file, not modified ({})'.format(path))
                    continue

                self.index_file(os.path.join(root, file))
        log.debug('Indexing finished')

    def find_symbol_locations(self, name):
        locations = []

        for path, file_index in self._index.items():
            for symbol in file_index.symbols:
                if symbol.name == name:
                    locations.append((path, symbol.line))

        return locations
