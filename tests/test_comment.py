#!python3

from blackmamba.comment import _comment_line, _uncomment_line, _toggle_lines


_BASIC_TEST_CASES = {
    # Not indented lines
    (0, 'a'): '# a',
    (0, 'a '): '# a ',
    # Keep new line
    (0, 'a\n'): '# a\n',
    # Space indented lines
    (0, '    a'): '#     a',
    (0, '        a'): '#         a',
    # Tab indented lines
    (0, '\ta'): '# \ta',
    (0, '\t\ta'): '# \t\ta',
    (0, '\t\ta '): '# \t\ta ',
    # Hash indexes
    (1, '\ta'): '\t# a',
    (2, '\t\ta'): '\t\t# a',
    (4, '    a'): '    # a'
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
    assert '# a b c' == _comment_line('# a b c')
    assert '\t# a b c' == _comment_line('\t# a b c')


def test_do_not_touch_not_commented_lines():
    assert 'a b c' == _uncomment_line('a b c')
    assert ' a b c   ' == _uncomment_line(' a b c   ')
    assert '\ta b c' == _uncomment_line('\ta b c')


_LINES_TEST_CASES = [
    (
        [
            "def hallo():",
            "    pass"
        ],
        [
            "# def hallo():",
            "#     pass"
        ]
    ),
    (
        [
            "    def hallo():",
            "        pass"
        ],
        [
            "    # def hallo():",
            "    #     pass"
        ],
    ),
    (
        [
            "\t\tdef hallo():",
            "\t\t    pass"
        ],
        [
            "\t\t# def hallo():",
            "\t\t#     pass"
        ],
    )
]


def test_toggle_comments():
    for case in _LINES_TEST_CASES:
        assert _toggle_lines(case[0]) == case[1]
        assert _toggle_lines(case[1]) == case[0]
