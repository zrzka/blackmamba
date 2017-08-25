import sys
from mock import MagicMock

sys.modules['editor'] = MagicMock()
sys.modules['ui'] = MagicMock()
sys.modules['objc_util'] = MagicMock()
sys.modules['console'] = MagicMock()
