#!python3

from blackmamba.toggle_comments import _comment_line, _uncomment_line


def test_comment_line():
    assert '# a' == _comment_line('a')


def test_uncomment_line():
    assert 'a' == _uncomment_line('# a')
    assert 'a' == _uncomment_line('#a')
