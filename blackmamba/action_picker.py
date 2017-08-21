#!python3

from objc_util import on_main_thread, ObjCClass
from ui import TableViewCell
from blackmamba.picker import load_picker_view, PickerItem, PickerDataSource
from blackmamba.uikit import UITableViewCellStyleDefault
import blackmamba.ide
        
                
class ActionPickerItem(PickerItem):
    def __init__(self, action_info):
        super().__init__(str(action_info['title'] or action_info['scriptName']))
        self.icon_name = str(action_info['iconName'])
        self.icon_color = str(action_info['iconColor'])
        self.script_name = str(action_info['scriptName'])


class ActionPickerDataSource(PickerDataSource):
    def __init__(self):
        super().__init__()
        
        NSUserDefaults = ObjCClass('NSUserDefaults')
        defaults = NSUserDefaults.standardUserDefaults()
        actions = defaults.objectForKey_('EditorActionInfos')
        self.items = [ActionPickerItem(ai) for ai in actions]
        
    def tableview_cell_for_row(self, tv, section, row):
        item = self.filtered_items[row]
        cell = TableViewCell(UITableViewCellStyleDefault)
        cell.text_label.number_of_lines = 1
        cell.text_label.text = item.title

        # TODO - Fix this to display image
#        image = Image.named('iob:{}_32'.format(item.icon_name))
#        if not image:
#            image = Image.named('python')

        return cell
                        

@on_main_thread
def action_quickly():
    def run_wrench_item(item, shift_enter):
        blackmamba.ide.run_script(item.script_name)
                                                            
    v = load_picker_view()
    v.datasource = ActionPickerDataSource()
    v.shift_enter_enabled = False
    v.title_label.text = 'Action Quickly...'
    v.help_label.text = (
        '⇅ - select • Enter - run action item'
        '\n'
        'Esc - close • Ctrl [ - close with Apple smart keyboard'
    )
    v.textfield.placeholder = 'Start typing to filter wrench items...'
    v.did_select_item_action = run_wrench_item
    v.present('sheet', hide_title_bar=True)
    v.wait_modal()
    

if __name__ == '__main__':
    action_quickly()

