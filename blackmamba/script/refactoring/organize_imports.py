#!python3
"""
Script name ``organize_imports.py``.

Organize imports.
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
            old_name
        )

        if not new_name:
            raise KeyboardInterrupt

        if not new_name == old_name:
            break

    return new_name


def main():
    from rope.base.project import Project
    from rope.base import libutils
    from rope.refactor.importutils import ImportOrganizer
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

        organizer = ImportOrganizer(project)
        change_set = organizer.organize_imports(resource)

        if not change_set:
            console.hud_alert('No changes required')
            return

        if refactoring.ask_if_apply_change_set(change_set):
            refactoring.apply_change_set(change_set, path, selection)
            console.hud_alert('Imports organized')

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
