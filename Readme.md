# Black Mamba

I do use [Pythonista](http://omz-software.com/pythonista/) on a daily basis.

> Pythonista is a complete development environment for writing Python™
> scripts on your iPad or iPhone.

It's a great tool. But it lacks some features like keyboard shortcuts for
specific actions. I'm slow without them. So I decided to write set of
scripts to _fix_ all these issues. To speed up my iteration cycle. To make
it as fast as possible. And which snake is the speediest one on the planet?
[Black Mamba](https://en.wikipedia.org/wiki/Black_mamba). And you know
why it's called Black Mamba now :)

## Installation

### Initial installation

Use StaSH:

```
[site-packages-3]$ pwd
~/Documents/site-packages-3
[site-packages-3]$ git clone https://github.com/zrzka/blackmamba.git .
[site-packages-3]$
```

**NOTE**: Do not miss the ` .` (space dot) at the end of `git clone` command.

### Updates

```
[site-packages-3]$ pwd
~/Documents/site-packages-3
[site-packages-3]$ git pull
[site-packages-3]$ 
```

## Usage

### Default key commands

Add the following lines to your `~/Documents/site-packages-3/pythonista_startup.py` file:

```
#!python3

import blackmamba as bm
bm.register_default_key_commands()
```

Create the `pythonista_startup.py` file if it doesn't exist.
`register_default_key_commands` will register following key commands.


| Scope  | Shortcut       | Assigned Function                               |
|--------|----------------|-------------------------------------------------|
| Editor | `Cmd /`        | `toggle_comments.toggle_comments`               |
| Editor | `Cmd W`        | `tabs.close_current_tab`                        |
| Editor | `Cmd Shift W`  | `tabs.close_all_tabs_except_current_one`        |
| Editor | `Cmd N`        | `tabs.new_file`                                 |
| Editor | `Cmd Shift N`  | `tabs.new_tab`                                  |
| Editor | `Cmd 0`        | `tabs.toggle_navigator`                         |
| Editor | `Cmd Shift 0`  | `dash.search_dash`                              |

### Custom key commands

Following example shows how you can register custom key commands and bind them
to your own functions. `Cmd Shift H` just prints `Hallo`.

```
#!python3

import blackmamba as bm
bm.register_default_key_commands()


from blackmamba.key_commands import register_key_command
from blackmamba.uikit import *  # UIKeyModifier*

def my_fn():
    print('Hallo')
    
register_key_command(
    'H',
    UIKeyModifierCommand | UIKeyModifierShift,
    my_fn,
    'Print Hallo')
```

