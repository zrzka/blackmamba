import editor
from objc_util import ObjCClass, on_main_thread, UIApplication

PASlidingContainerViewController = ObjCClass('PASlidingContainerViewController')
PA2UniversalTextEditorViewController = ObjCClass('PA2UniversalTextEditorViewController')


def _root_view_controller():
	root = UIApplication.sharedApplication().keyWindow().rootViewController()
	if root.isKindOfClass_(PASlidingContainerViewController):
		return root
	return None


def _tabs_view_controller():
	root = _root_view_controller()
	if root:
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
	

@on_main_thread				
def toggle_navigator():
	root = _root_view_controller()
	if not root:
		return

	if root.masterVisible():
		root.hideMasterWithAnimationDuration_(0.3)
	else:
		root.showMasterWithAnimationDuration_(0.3)
		
		
@on_main_thread		
def new_tab():	
	tabs = _tabs_view_controller()
	
	if not tabs:
		return
		
	tabs.addTab_(tabs.addTabButtonItem())
	
	
@on_main_thread	
def new_file():
	tabs = _tabs_view_controller()
	
	if not tabs:
		return
		
	tabs.addTab_(tabs.addTabButtonItem())
	tab = tabs.tabViewControllers()[-1]
	tab.addNewFile_(tab.addNewFileButton())

