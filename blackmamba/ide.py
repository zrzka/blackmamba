#!python3

from objc_util import ObjCClass, on_main_thread, UIApplication, sel
import os
import urllib.parse
import webbrowser
import blackmamba.action_picker
from blackmamba.log import error
import editor
import console
from blackmamba.config import get_config_value

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


def _tabs_count():
    return len(tabs_view_controller().tabBarView().tabViews())


def _selected_tab_index():
    return tabs_view_controller().tabBarView().selectedTabIndex()


@on_main_thread
def save(all=False):
    tabs = tabs_view_controller()

    if all:
        tabs_to_save = tabs.tabViewControllers()
    else:
        tabs_to_save = [tabs.tabViewControllers()[_selected_tab_index()]]

    for tab in tabs_to_save:
        if tab.respondsToSelector(sel('saveData')):
            tab.saveData()


@on_main_thread
def select_tab(index):
    tabs = tabs_view_controller()
    tab_views = tabs.tabBarView().tabViews()

    if index >= len(tab_views):
        return

    tabs.tabBarView().tabSelected_(tab_views[index])
    tabs.switchToTabViewController_(tabs.tabViewControllers()[index])


@on_main_thread
def select_next_tab():
    select_tab((_selected_tab_index() + 1) % _tabs_count())


@on_main_thread
def select_previous_tab():
    select_tab((_selected_tab_index() - 1) % _tabs_count())


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


def run_script(script_name, full_path=False, delay=None):
    if not full_path and script_name.startswith('/'):
        script_name = script_name[1:]

    if not script_exists(script_name, full_path):
        error('run_script: script does not exist {}'.format(script_name))
        return

    if full_path:
        docs_root = os.path.expanduser('~/Documents/')
        script_name = script_name[len(docs_root):]

    encoded_name = urllib.parse.quote_plus(script_name, safe='', encoding=None, errors=None)
    url = 'pythonista://{}?action=run'.format(encoded_name)

    if delay:
        import ui

        def make_open_url(url):
            def open():
                webbrowser.open(url)
            return open

        ui.delay(make_open_url(url), 1.0)
    else:
        webbrowser.open(url)


def _load_action(title):
    actions = [a for a in blackmamba.action_picker.load_editor_actions() if a.title == title]
    return actions[0] if len(actions) == 1 else None


def action_exists(title):
    return _load_action(title) is not None


def run_action(title, delay=None):
    action = _load_action(title)
    if not action:
        error('run_action: action does not exist {}'.format(title))
        return

    run_script(action.script_name, delay)


def scroll_to_line(line_number):
    text = editor.get_text()
    if not text:
        return

    # https://github.com/omz/Pythonista-Issues/issues/365
    start = 0
    for index, line in enumerate(text.splitlines(True)):
        if index == line_number - 1:
            editor.set_selection(start)
            return
        start += len(line)
    editor.set_selection(start)


def jump_to_line():
    try:
        input = console.input_alert('Jump to line...', 'Empty (or invalid) value  to dismiss.')
        scroll_to_line(int(input))
    except ValueError:
        # Invalid input value (not int)
        pass
    except KeyboardInterrupt:
        # Cancel button
        pass


def _page(line_count):
    text = editor.get_text()
    if not text:
        return

    start, end = editor.get_line_selection()

    current_line = text.count('\n', 0, start if line_count < 0 else end) + 1

    line = max(1, current_line + line_count)
    scroll_to_line(line)


def page_up():
    _page(-get_config_value('general.page_line_count', 40))


def page_down():
    _page(get_config_value('general.page_line_count', 40))
