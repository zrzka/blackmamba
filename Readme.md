# Pythonista packages

Packages for Pythonista (Python 3), which should be place into `site-packages-3`.

## Packages

* [external_screen](#external_screen)
* [pythonista_startup](#pythonista_startup)

### external_screen

This module allows you to use external screen to present different view on
iPad and on TV for example.

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

### pythonista_startup

Custom shortcuts registration.

| Scope  | Shortcut       | Assigned Function                               |
|--------|----------------|-------------------------------------------------|
| Editor | `Cmd /`        | `toggle_comments.toggle_comments`               |
| Editor | `Cmd W`        | `tabs.close_current_tab`                        |
| Editor | `Cmd Shift W`  | `tabs.close_all_tabs_except_current_one`        |

NOTE: Scope is not implemented yet.

