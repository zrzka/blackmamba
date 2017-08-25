#!python3

import unittest
from blackmamba.toggle_comments import _comment_line, _uncomment_line


class ToggleCommentsTests(unittest.TestCase):

    def test_comment_line(self):
        assert '# a' == _comment_line('a')

    def test_uncomment_line(self):
        assert 'a' == _uncomment_line('# a')
        assert 'a' == _uncomment_line('#a')
