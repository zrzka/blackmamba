#!python3

# Open Quickly... dialog settings

OPEN_QUICKLY_IGNORE_FOLDERS = {
    '': ['.git'],
    '.': ['.Trash', 'Examples',
          'site-packages', 'site-packages-2', 'site-packages-3']
}

# Run Quickly... dialog settings

RUN_QUICKLY_IGNORE_FOLDERS = {
    '': ['.git'],
    '.': ['.Trash', 'Examples',
          'site-packages', 'site-packages-2', 'site-packages-3']
}


# Analyzer settings

ANALYZER_HUD_DELAY = 1.0

ANALYZER_PEP8_IGNORE = (
    'W391',  # Blank line at the end of file
    'W293',  # Blank line contains whitespace
)

ANALYZER_PEP8_MAX_LINE_LENGTH = 79
