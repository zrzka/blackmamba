import editor
from objc_util import ObjCClass, on_main_thread, UIApplication

PASlidingContainerViewController = ObjCClass('PASlidingContainerViewController')
PA2UniversalTextEditorViewController = ObjCClass('PA2UniversalTextEditorViewController')

def _tabs_view_controller():
	root = UIApplication.sharedApplication().keyWindow().rootViewController()
	if root.isKindOfClass_(PASlidingContainerViewController):
		return root.detailViewController()
	return None


def _tab_view_controller():
	tabs = _tabs_view_controller()
	if tabs:
		tab = tabs.selectedTabViewController()
		if tab.isKindOfClass_(PA2UniversalTextEditorViewController):
			return tab
	return None
	

@on_main_thread																		
def close_all_tabs_except_current_one():
	tabs = _tabs_view_controller()
	if tabs:
		tabs.closeAllTabsExceptCurrent()						
		
						
@on_main_thread
def close_current_tab():
	tabs = _tabs_view_controller()
	
	# TODO Do not close last tab, crashes
	if len(tabs.tabViewControllers()) > 1:
		tabs.closeSelectedTab_(tabs.closeSelectedTabButtonItem().ptr)

