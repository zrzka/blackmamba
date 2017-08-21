#!python3

from objc_util import on_main_thread, ObjCClass
from ui import TableViewCell, Image
import ui
from blackmamba.picker import load_picker_view, PickerItem, PickerDataSource
from blackmamba.uikit import UITableViewCellStyleSubtitle
import blackmamba.ide
import os
        
                
class ActionPickerItem(PickerItem):
    def __init__(self, action_info):
        script_name = str(action_info['scriptName'])

        if action_info['title']:
            title = str(action_info['title'])
        else:
            _, tail = os.path.split(script_name)
            title, _ = os.path.splitext(tail)
        
        subtitle = ' • '.join(script_name.split(os.sep))
                
        super().__init__(title, subtitle)
        
        self.icon_name = str(action_info['iconName'])
        
        if action_info['iconColor']:
            self.icon_color = '#{}'.format(action_info['iconColor'])
        else:
            self.icon_color = '#FFFFFF'
        self.script_name = script_name
        
    @property
    def image(self):
        # TODO - Find a way how get the right icon, because there's
        #        lot of prefixes like iob:, different sizes, ...
        image = Image.named('iob:play_32')
        return image


class ActionPickerDataSource(PickerDataSource):
    def __init__(self):
        super().__init__()
        
        NSUserDefaults = ObjCClass('NSUserDefaults')
        defaults = NSUserDefaults.standardUserDefaults()
        actions = defaults.objectForKey_('EditorActionInfos')
        self.items = [ActionPickerItem(ai) for ai in actions]
        
    def tableview_cell_for_row(self, tv, section, row):
        item = self.filtered_items[row]
        cell = TableViewCell(UITableViewCellStyleSubtitle)
        cell.text_label.number_of_lines = 1
        cell.text_label.text = item.title
        cell.detail_text_label.text = item.subtitle
        cell.detail_text_label.text_color = (0, 0, 0, 0.5)
        
#        cell.image_view.content_mode = ui.CONTENT_SCALE_ASPECT_FILL
#        cell.image_view.background_color = item.icon_color
#        cell.image_view.image = item.image
#        cell.image_view.alpha = 0.5
        
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

