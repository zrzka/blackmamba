#!python3

import editor
import ast
import os
from enum import Enum
from blackmamba.uikit.picker import PickerView, PickerItem, PickerDataSource
from ui import Image
import blackmamba.ide.source as source
import re


_TODO_RE = re.compile('\A.*#\s*\[?(?i:TODO)\]?[ :]*(?P<text>.*?)\s*\Z')
_FIXME_RE = re.compile('\A.*#\s*\[?(?i:FIXME)\]?[ :]*(?P<text>.*?)\s*\Z')


class OutlineNodeItem(PickerItem):
    class Style(str, Enum):
        cls = 'class'
        fn = 'function'
        todo = 'iob:alert_circled_24'
        fixme = 'iob:alert_circled_24'

    def __init__(self, style, name, line, column, level, breadcrumb):
        super().__init__('{}{}'.format(level * '    ', name),
                         '{} (line {})'.format(breadcrumb, line))
        self.style = style
        self.name = name
        self.line = line
        self.column = column
        self.level = level
        self.breadcrumb = breadcrumb
        self.image = Image(style)


class OutlineDataSource(PickerDataSource):
    def __init__(self, text, filename):
        super().__init__()

        r = ast.parse(text)
        ast_nodes = OutlineDataSource._generate_nodes(r, breadcrumb=filename)

        comment_nodes = []
        for i, line in enumerate(text.splitlines()):
            match = _TODO_RE.fullmatch(line)
            if match:
                comment_nodes.append(OutlineNodeItem(
                    OutlineNodeItem.Style.todo, match.group('text'), i + 1, 0, 0, filename
                ))

            match = _FIXME_RE.fullmatch(line)
            if match:
                comment_nodes.append(OutlineNodeItem(
                    OutlineNodeItem.Style.fixme, match.group('text'), i + 1, 0, 0, filename
                ))

        self.items = sorted(ast_nodes + comment_nodes, key=lambda x: x.line)

    @staticmethod
    def _generate_nodes(parent, level=0, breadcrumb=''):
        nodes = []

        for child in parent.body:
            if isinstance(child, ast.ClassDef):
                style = OutlineNodeItem.Style.cls
            elif isinstance(child, ast.FunctionDef) or isinstance(child, ast.AsyncFunctionDef):
                style = OutlineNodeItem.Style.fn
            else:
                style = None

            if style:
                node = OutlineNodeItem(style, child.name, child.lineno, child.col_offset, level, breadcrumb)
                nodes.append(node)
                if breadcrumb:
                    bc = '{} • {}'.format(breadcrumb, child.name)
                else:
                    bc = child.name
                child_nodes = OutlineDataSource._generate_nodes(child, level + 1, bc)
                if child_nodes:
                    nodes.extend(child_nodes)

        return nodes

    def tableview_cell_for_row(self, tv, section, row):
        cell = super().tableview_cell_for_row(tv, section, row)

        item = self.filtered_items[row]

        font = '<system>'
        tint_color = None

        if item.style is OutlineNodeItem.Style.todo:
            font = '<system-bold>'
            tint_color = 'yellow'
        elif item.style is OutlineNodeItem.Style.fixme:
            font = '<system-bold>'
            tint_color = 'red'

        cell.text_label.font = (font, 17)
        cell.image_view.tint_color = tint_color

        return cell


def main():
    filename = editor.get_path()
    if not filename:
        return

    if not filename.endswith('.py'):
        return

    text = editor.get_text()
    if not text:
        return

    def scroll_to_node(node, shift_enter):
        source.scroll_to_line(node.line)

    v = PickerView()
    v.name = 'Outline'
    v.datasource = OutlineDataSource(text, os.path.basename(filename))
    v.shift_enter_enabled = False
    v.help_label.text = (
        '⇅ - select • Enter - scroll to location'
        '\n'
        'Esc - close • Cmd . - close with Apple smart keyboard'
    )
    v.textfield.placeholder = 'Start typing to filter nodes...'
    v.did_select_item_action = scroll_to_node
    v.present('sheet')
    v.wait_modal()


if __name__ == '__main__':
    main()
