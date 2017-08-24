from objc_util import ObjCClass, on_main_thread, UIApplication
import os
import urllib.parse
import webbrowser
import blackmamba.action_picker

PASlidingContainerViewController = ObjCClass('PASlidingContainerViewController')
PA2UniversalTextEditorViewController = ObjCClass('PA2UniversalTextEditorViewController')


def root_view_controller():
    root = UIApplication.sharedApplication().keyWindow().rootViewController()
    if root.isKindOfClass_(PASlidingContainerViewController):
        return root
    return None


def tabs_view_controller():
    root = root_view_controller()
    if root:
        return root.detailViewController()
    return None


@on_main_thread
def close_all_tabs_except_current_one():
    tabs = tabs_view_controller()
    if tabs:
        tabs.closeAllTabsExceptCurrent()


@on_main_thread
def close_current_tab():
    tabs = tabs_view_controller()

    # TODO Do not close last tab, crashes
    if len(tabs.tabViewControllers()) > 1:
        tabs.closeSelectedTab_(tabs.closeSelectedTabButtonItem().ptr)


@on_main_thread
def toggle_navigator():
    root = root_view_controller()
    if not root:
        return

    if root.masterVisible():
        root.hideMasterWithAnimationDuration_(0.3)
    else:
        root.showMasterWithAnimationDuration_(0.3)


@on_main_thread
def new_tab():
    tabs = tabs_view_controller()

    if not tabs:
        return

    tabs.addTab_(tabs.addTabButtonItem())


@on_main_thread
def new_file():
    tabs = tabs_view_controller()

    if not tabs:
        return

    tabs.addTab_(tabs.addTabButtonItem())
    tab = tabs.tabViewControllers()[-1]
    tab.addNewFile_(tab.addNewFileButton())


def script_exists(script_name, full_path=False):
    if not full_path:
        script_name = os.path.join(os.path.expanduser('~/Documents'), script_name)
    return os.path.exists(script_name)


def run_script(script_name, full_path=False):
    if not script_exists(script_name, full_path):
        print('run_script: script does not exist {}'.format(script_name))
        return

    if full_path:
        docs_root = os.path.expanduser('~/Documents/')
        script_name = script_name[len(docs_root):]

    encoded_name = urllib.parse.quote_plus(script_name, safe='', encoding=None, errors=None)
    url = 'pythonista://{}?action=run'.format(encoded_name)
    webbrowser.open(url)

#    docs = os.path.expanduser('~/Documents')
#    file_path = os.path.join(docs, script_name)
#    runpy.run_path(file_path, run_name='__main__')


def _load_action(title):
    actions = [a for a in blackmamba.action_picker.load_editor_actions() if a.title == title]
    return actions[0] if len(actions) == 1 else None


def action_exists(title):
    return _load_action(title) is not None


@on_main_thread
def run_action(title):
    action = _load_action(title)
    if not action:
        print('run_action: action does not exist {}'.format(title))
        return

    run_script(action.script_name)
