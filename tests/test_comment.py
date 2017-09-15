#!python3

from blackmamba.comment import _comment_line, _uncomment_line, _toggle_lines


_BASIC_TEST_CASES = {
    # Not indented lines
    ('', 'a\n'): '# a\n',
    ('', 'a \n'): '# a \n',
    # Space indented lines
    ('', '    a\n'): '#     a\n',
    ('', '        a\n'): '#         a\n',
    # Tab indented lines
    ('', '\ta\n'): '# \ta\n',
    ('', '\t\ta\n'): '# \t\ta\n',
    ('', '\t\ta \n'): '# \t\ta \n',
    # Hash indexes
    ('\t', '\ta\n'): '\t# a\n',
    ('\t\t', '\t\ta\n'): '\t\t# a\n',
    ('    ', '    a\n'): '    # a\n',
    # Comment even if there's inline comment
    ('    ', '    def main():  # Hallo\n'): '    # def main():  # Hallo\n'
}


def test_comment_line():
    for key, value in _BASIC_TEST_CASES.items():
        assert value == _comment_line(key[1], key[0])


def test_uncomment_line():
    for key, value in _BASIC_TEST_CASES.items():
        assert key[1] == _uncomment_line(value)


def test_backward_compatible_uncomment():
    assert 'a' == _uncomment_line('#a')
    assert 'a ' == _uncomment_line('#a ')
    assert '\ta' == _uncomment_line('\t#a')
    assert '\ta ' == _uncomment_line('\t#a ')


def test_do_not_comment_commented_lines():
    assert '# a b c' == _comment_line('# a b c', '')
    assert '\t# a b c' == _comment_line('\t# a b c', '\t')


def test_do_not_touch_not_commented_lines():
    assert 'a b c' == _uncomment_line('a b c')
    assert ' a b c   ' == _uncomment_line(' a b c   ')
    assert '\ta b c' == _uncomment_line('\ta b c')


def test_empty_lines():
    assert '    # \n' == _comment_line('\n', '    ')
    assert '\n' == _uncomment_line('     #     \n')


_LINES_TEST_CASES = [
    (
        [
            "def hallo():\n",
            "    pass\n"
        ],
        [
            "# def hallo():\n",
            "#     pass\n"
        ]
    ),
    (
        [
            "def hallo():\n",
            "\n",
            "    pass\n"
        ],
        [
            "# def hallo():\n",
            "# \n",
            "#     pass\n"
        ]
    ),
    (
        [
            "    def hallo():\n",
            "        pass\n"
        ],
        [
            "    # def hallo():\n",
            "    #     pass\n"
        ],
    ),
    (
        [
            "    def hallo():\n",
            "\n",
            "        pass\n"
        ],
        [
            "    # def hallo():\n",
            "    # \n",
            "    #     pass\n"
        ],
    ),
    (
        [
            "\t\tdef hallo():\n",
            "\t\t    pass\n"
        ],
        [
            "\t\t# def hallo():\n",
            "\t\t#     pass\n"
        ],
    ),
    (
        [
            "\t\tdef hallo():\n",
            "\n",
            "\t\t    pass\n"
        ],
        [
            "\t\t# def hallo():\n",
            "\t\t# \n",
            "\t\t#     pass\n"
        ],
    )
]


def test_toggle_comments():
    for case in _LINES_TEST_CASES:
        assert _toggle_lines(case[0]) == case[1]
        assert _toggle_lines(case[1]) == case[0]
