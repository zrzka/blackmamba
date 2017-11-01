#!python3
"""
Script name ``rename.py``.

Rename identifier.
"""
import console
import os

import blackmamba.ide.refactoring as refactoring
import blackmamba.ide.tab as tab
import editor


def _ask_for_new_name(old_name):
    while True:
        new_name = console.input_alert(
            'Rename identifier',
            'Preview of all changes will be available in the next step.',
            old_name,
            'Rename'
        )

        if not new_name:
            raise KeyboardInterrupt

        if not new_name == old_name:
            break

    return new_name


def main():
    from rope.base.project import Project
    from rope.base import libutils
    from rope.refactor.rename import Rename
    from rope.base.exceptions import RopeError

    path = editor.get_path()
    selection = editor.get_selection()

    if not path or not selection:
        console.hud_alert('Not a Python file', 'error')
        return

    tab.save()

    project = None
    try:
        project = Project(os.path.dirname(path), ropefolder=None)
        resource = libutils.path_to_resource(project, path)
        if not libutils.is_python_file(project, resource):
            console.hud_alert('Not a Python file', 'error')
            return

        renamer = Rename(project, resource, selection[0])
        old_name = renamer.get_old_name()

        if not old_name:
            console.hud_alert('Unable to get identifier name', 'error')
            return

        new_name = _ask_for_new_name(old_name)

        change_set = renamer.get_changes(new_name, docs=True, resources=[resource])
        if not change_set:
            console.hud_alert('No changes required')
            return

        if refactoring.ask_if_apply_change_set(change_set):
            refactoring.apply_change_set(change_set, path, selection)
            console.hud_alert('Identifier renamed')

    except RopeError as e:
        console.hud_alert(str(e), 'error')

    except KeyboardInterrupt:
        pass

    finally:
        if project:
            project.close()


if __name__ == '__main__':
    from blackmamba.bundle import bundle
    with bundle('refactoring'):
        main()
