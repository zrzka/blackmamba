# Pythonista packages

Packages for Pythonista which should be place into `site-packages-3`. Why
`site-packages-3`? I do use Python 3 only and didn't test any of these
packages with Python 2.

## Packages

* [blackmamba](#blackmamba)
* [external_screen](#external_screen)

### blackmamba

This package goal is to provide Pythonista on steroids. Check sample
`pythonista_startup.py` to see what's going on here. It contains HW keyboard
shortcuts for example, associated with following functions:

| Scope  | Shortcut       | Assigned Function                               |
|--------|----------------|-------------------------------------------------|
| Editor | `Cmd /`        | `toggle_comments.toggle_comments`               |
| Editor | `Cmd W`        | `tabs.close_current_tab`                        |
| Editor | `Cmd Shift W`  | `tabs.close_all_tabs_except_current_one`        |
| Editor | `Cmd N`        | `tabs.new_file`                                 |
| Editor | `Cmd Shift N`  | `tabs.new_tab`                                  |
| Editor | `Cmd 0`        | `tabs.toggle_navigator`                         |

### external_screen

This module allows you to use external screen to present different view on
iPad and on TV for example. Experiment based on question in the Pythonista
forum.

Sample usage:

```python
import external_screen as es
import ui
import logging

# View to present on external screen
red_view = ui.View()
red_view.background_color = 'red'

# Optional handler for external screen connection
def connected():
    print('Screen connected, lets display red_view again')
    es.present(red_view)

# Optional handler for external screen disconnection
def disconnected():
    print('Ouch, screen disconnected')

# Start external screen notification listener, setup logging, ...
es.init(log_level=logging.DEBUG)
# Present view on external screen
es.present(red_view)
# Register optional handlers
es.register_connected_handler(connected)
es.register_disconnected_handler(disconnected)

try:
    while True:
        pass
except KeyboardInterrupt:
    # Stop external screen notification listener, discard logger,
    # optional handlers, ...
    es.terminate()
    pass
```


