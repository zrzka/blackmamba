#!python3

from blackmamba.comment import _comment_line, _uncomment_line


_BASIC_TEST_CASES = {
    # Not indented lines
    'a': '# a',
    'a ': '# a ',
    # Keep new line
    'a\n': '# a\n',
    # Space indented lines
    '    a': '    # a',
    '        a': '        # a',
    # Tab indented lines
    '\ta': '\t# a',
    '\t\ta': '\t\t# a',
    '\t\ta ': '\t\t# a '
}


def test_comment_line():
    for key, value in _BASIC_TEST_CASES.items():
        assert value == _comment_line(key)


def test_uncomment_line():
    for key, value in _BASIC_TEST_CASES.items():
        assert key == _uncomment_line(value)


def test_backward_compatible_uncomment():
    assert 'a' == _uncomment_line('#a')
    assert 'a ' == _uncomment_line('#a ')
    assert '\ta' == _uncomment_line('\t#a')
    assert '\ta ' == _uncomment_line('\t#a ')


def test_do_not_comment_commented_lines():
    assert '# a b c' == _comment_line('# a b c')
    assert '\t# a b c' == _comment_line('\t# a b c')


def test_do_not_touch_not_commented_lines():
    assert 'a b c' == _uncomment_line('a b c')
    assert ' a b c   ' == _uncomment_line(' a b c   ')
    assert '\ta b c' == _uncomment_line('\ta b c')
