#!python3

import blackmamba.ide.script as script


class ActionInfo(object):
    def __init__(self, action_info):
        self.script_name = str(action_info['scriptName'])
        self.icon_name = str(action_info['iconName'])

        if action_info['title']:
            self.title = str(action_info['title'])
        else:
            self.title = None

        if action_info['iconColor']:
            self.icon_color = '#{}'.format(action_info['iconColor'])
        else:
            self.icon_color = '#FFFFFF'

    def run(self, delay=None):
        script.run_script(self.script_name, delay=delay)


def get_actions():
    from objc_util import ObjCClass
    defaults = ObjCClass('NSUserDefaults').standardUserDefaults()
    return [ActionInfo(ai) for ai in defaults.objectForKey_('EditorActionInfos')]


def get_action(title):
    for action in get_actions():
        if action.title == title:
            return action
    return None


def run_action(title, delay=None):
    action = get_action(title)

    if not action:
        return

    action.run(delay)
