#!python3

import blackmamba.ide.source as source
import console


def jump_to_line():
    try:
        input = console.input_alert('Jump to line...', 'Empty (or invalid) value  to dismiss.')
        source.scroll_to_line(int(input))
    except ValueError:
        # Invalid input value (not int)
        pass
    except KeyboardInterrupt:
        # Cancel button
        pass


if __name__ == '__main__':
    jump_to_line()
