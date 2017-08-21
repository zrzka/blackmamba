import editor
from objc_util import ObjCClass, on_main_thread, UIApplication, ns
import runpy
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
    
    
def run_script(script_name):
    encoded_name = urllib.parse.quote_plus(script_name, safe='', encoding=None, errors=None)
    url = 'pythonista://{}?action=run'.format(encoded_name)
    webbrowser.open(url)
    
#    docs = os.path.expanduser('~/Documents')
#    file_path = os.path.join(docs, script_name)
#    runpy.run_path(file_path, run_name='__main__')


@on_main_thread
def run_action(title):
    actions = [a for a in blackmamba.action_picker.load_editor_actions() if a.title == title]
    
    if len(actions) == 0:
        print('Unable to find action with title: {}'.format(title))
        return
        
    if len(actions) > 1:
        print('Multiple actions found with title: {}'.format(title))
        return
        
    run_script(actions[0].script_name)

