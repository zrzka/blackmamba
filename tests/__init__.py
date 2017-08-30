import blackmamba.system as system


if not system.PYTHONISTA:
    import sys
    from mock import MagicMock

    sys.modules['editor'] = MagicMock()
    sys.modules['ui'] = MagicMock()
    sys.modules['objc_util'] = MagicMock()
    sys.modules['console'] = MagicMock()
    sys.modules['clipboard'] = MagicMock()
