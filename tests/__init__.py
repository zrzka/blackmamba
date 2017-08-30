import os
import re

IS_PYTHONISTA = re.search('Pythonista\d+', os.environ.get('PYTHONPATH', ''), re.ASCII) is not None

if not IS_PYTHONISTA:
    import sys
    from mock import MagicMock

    sys.modules['editor'] = MagicMock()
    sys.modules['ui'] = MagicMock()
    sys.modules['objc_util'] = MagicMock()
    sys.modules['console'] = MagicMock()
    sys.modules['clipboard'] = MagicMock()
