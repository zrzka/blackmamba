#!python3

from objc_util import on_main_thread, ObjCClass, sel


_PASlidingContainerViewController = ObjCClass('PASlidingContainerViewController')
_PA2UniversalTextEditorViewController = ObjCClass('PA2UniversalTextEditorViewController')
_UIApplication = ObjCClass('UIApplication')


def _get_root_view_controller():
    key_window = _UIApplication.sharedApplication().keyWindow()
    return key_window.rootViewController()


def _get_tabs_view_controller():
    root = _get_root_view_controller()

    if not root.isKindOfClass_(_PASlidingContainerViewController):
        return None

    return root.detailViewController()


def _get_selected_tab_view_controller():
    tabs = _get_tabs_view_controller()

    if not tabs:
        return

    tab = tabs.selectedTabViewController()
    if not tab or not tab.isKindOfClass_(_PA2UniversalTextEditorViewController):
        return None

    return tab


def _get_tab_bar_view():
    tabs = _get_tabs_view_controller()
    return tabs.tabBarView() if tabs else None


def _get_tabs_count():
    tab_bar = _get_tab_bar_view()
    return len(tab_bar.tabViews()) if tab_bar else 0


def _get_selected_tab_index():
    tab_bar = _get_tab_bar_view()
    return tab_bar.selectedTabIndex() if tab_bar else -1


@on_main_thread
def select_tab(index):
    count = _get_tabs_count()

    if index < 0 or index >= count:
        return

    tab_bar = _get_tab_bar_view()
    tab_bar_views = tab_bar.tabViews()
    tab_bar.tabSelected_(tab_bar_views[index])

    tabs = _get_tabs_view_controller()
    tabs.switchToTabViewController_(tabs.tabViewControllers()[index])


@on_main_thread
def select_next_tab():
    index = _get_selected_tab_index()

    if index == -1:
        return

    select_tab((index + 1) % _get_tabs_count())


@on_main_thread
def select_previous_tab():
    index = _get_selected_tab_index()

    if index == -1:
        return

    select_tab((index - 1) % _get_tabs_count())


@on_main_thread
def save(all=False):
    tabs = _get_tabs_view_controller()

    if not tabs:
        return

    if all:
        tabs_to_save = tabs.tabViewControllers()
    else:
        tabs_to_save = [tabs.tabViewControllers()[_get_selected_tab_index()]]

    for tab in tabs_to_save:
        if tab.respondsToSelector(sel('saveData')):
            tab.saveData()


@on_main_thread
def close_tabs_except_current():
    tabs = _get_tabs_view_controller()

    if not tabs:
        return

    tabs.closeAllTabsExceptCurrent()


@on_main_thread
def close_selected_tab():
    tabs = _get_tabs_view_controller()

    if not tabs:
        return

    if len(tabs.tabViewControllers()) > 1:
        tabs.closeSelectedTab_(tabs.closeSelectedTabButtonItem().ptr)


@on_main_thread
def toggle_navigator():
    root = _get_root_view_controller()
    if not root:
        return

    if root.masterVisible():
        root.hideMasterWithAnimationDuration_(0.3)
    else:
        root.showMasterWithAnimationDuration_(0.3)


@on_main_thread
def new_tab():
    tabs = _get_tabs_view_controller()

    if not tabs:
        return

    tabs.addTab_(tabs.addTabButtonItem())


@on_main_thread
def new_file():
    tabs = _get_tabs_view_controller()

    if not tabs:
        return

    tabs.addTab_(tabs.addTabButtonItem())
    tab = tabs.tabViewControllers()[-1]
    tab.addNewFile_(tab.addNewFileButton())


@on_main_thread
def get_path():
    tab = _get_selected_tab_view_controller()

    if not tab:
        return None

    return str(tab.filePath())


@on_main_thread
def get_paths():
    tabs = _get_tabs_view_controller()

    if not tabs:
        return None

    return [str(tab.filePath()) for tab in tabs.tabViewControllers()]


def open_file(path, new_tab=True):
    index = None
    paths = get_paths()

    if paths:
        try:
            index = paths.index(path)
        except ValueError:
            pass

    if index is None:
        import editor
        editor.open_file(path, new_tab=new_tab)
    else:
        select_tab(index)
