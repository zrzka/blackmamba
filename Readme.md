# Black Mamba

[Pythonista](http://omz-software.com/pythonista/) on steroids.

> Pythonista is a complete development environment for writing Python™
> scripts on your iPad or iPhone.

Pythonista is a great tool. But it lacks some features like keyboard shortcuts
for specific actions. I'm slow without them. So I decided to write set of
scripts to _fix_ all these issues. To speed up my iteration cycle. To make
it as fast as possible. And which snake is the speediest one on the planet?
[Black Mamba](https://en.wikipedia.org/wiki/Black_mamba). And you know
why it's called Black Mamba now :)

## Status

It's still an experiment and you can expect breaking changes. I'm trying
to avoid them, but I can't promise stable interface for now.

You're welcome to report [new issue](https://github.com/zrzka/blackmamba/issues/new)
if you find a bug or would like to have something added.

## Installation

### Initial installation

Use StaSH:

```sh
[site-packages-3]$ pwd
~/Documents/site-packages-3
[site-packages-3]$ git clone https://github.com/zrzka/blackmamba.git .
[site-packages-3]$
```

**NOTE**: Do not miss the ` .` (space dot) at the end of `git clone` command.

### Updates

```sh
[site-packages-3]$ pwd
~/Documents/site-packages-3
[site-packages-3]$ git pull
[site-packages-3]$ 
```

## Usage

Following examples should be placed in the `~/Documents/site-packages-3/pythonista_startup.py`
file. Create this file if it doesn't exist.

### Register default key commands

How to register default Black Mamba key commands.

```python
#!python3

import blackmamba as bm
bm.register_default_key_commands()
```

List of default key commands:

| Shortcut       | Function                                        |
|----------------|-------------------------------------------------|
| `Cmd /`        | Comment / uncomment selected line(s)            |
| `Cmd W`        | Close current editor tab                        |
| `Cmd Shift W`  | Close all editor tabs except current one        |
| `Cmd N`        | New tab + new file                              |
| `Cmd Shift N`  | Just new tab                                    |
| `Cmd 0`        | Show / hide navigator (library)                 |
| `Cmd Shift 0`  | Query selected text in Dash                     |
| `Cmd O`        | Open Quickly file...                            |

### Register custom key commands

How to print `Hallo` with `Cmd Shift H`.

```python
#!python3

# Register default key commands. You're not forced to call it, feel
# free to remove these two lines if you don't like these key commands.
import blackmamba as bm
bm.register_default_key_commands()

# `register_key_command` can be called even if you don't call
# `register_default_key_commands`. IOW you can use Black Mamba
# for your own key commands only.
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

