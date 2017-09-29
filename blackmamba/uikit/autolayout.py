#!python3

import ui
from objc_util import ObjCInstance, ObjCClass, on_main_thread
from enum import Enum
from functools import partial


_LayoutConstraint = ObjCClass('NSLayoutConstraint')


class LayoutRelation(int, Enum):
    lessThanOrEqual = -1
    equal = 0
    greaterThanOrEqual = 1


class LayoutAttribute(int, Enum):
    notAnAttribute = 0
    left = 1
    right = 2
    top = 3
    bottom = 4
    leading = 5
    trailing = 6
    width = 7
    height = 8
    centerX = 9
    centerY = 10
    baseline = 11
    lastBaseline = 12
    firstBaseline = 13
    leftMargin = 14
    rightMargin = 15
    topMargin = 16
    bottomMargin = 17
    leadingMargin = 18
    trailingMargin = 19
    centerXWithinMargins = 20
    centerYWithinMargins = 21


class LayoutConstraintOrientation(int, Enum):
    horizontal = 0
    vertical = 1


class LayoutPriority(float, Enum):
    required = 1000
    defaultHight = 750
    defaultLow = 250
    fittingSizeLevel = 50


class _LayoutBaseAttribute:
    _relations = {
        "min": LayoutRelation.greaterThanOrEqual,
        "max": LayoutRelation.lessThanOrEqual,
        "equal": LayoutRelation.equal
    }

    def __init__(self, view, attribute, other=None, other_attribute=LayoutAttribute.notAnAttribute):
        assert(isinstance(view, LayoutProxy))
        assert(isinstance(attribute, LayoutAttribute))

        self._view = view
        self._attribute = attribute
        self._constraints = {}

        if other:
            assert(isinstance(other, ui.View))
            assert(isinstance(other_attribute, LayoutAttribute))

            self._other = other
            self._other_attribute = other_attribute
        else:
            self._other = None
            self._other_attribute = LayoutAttribute.notAnAttribute

    @property
    def view(self):
        return self._view

    @property
    def attribute(self):
        return self._attribute

    @property
    def other(self):
        return self._other

    @property
    def other_attribute(self):
        return self._other_attribute

    @property
    def superview(self):
        return self._view.superview

    @on_main_thread
    def remove_constraint(self, constraint):
        ObjCInstance(self.superview).removeConstraint_(constraint)

    @on_main_thread
    def add_constraint(self, constraint):
        ObjCInstance(self.superview).addConstraint_(constraint)

    def constraint(relation, value, priority):
        raise NotImplementedError

    def __setattr__(self, name, value):
        if name in self._relations.keys():
            constraint = self._constraints.get(name, None)
            if constraint:
                self.remove_constraint(constraint)

            if value is None:
                return

            if isinstance(value, tuple):
                priority = value[1]
                value = value[0]
            else:
                priority = LayoutPriority.required

            constraint = self.constraint(self._relations[name], value, priority)
            self._constraints[name] = constraint
            self.add_constraint(constraint)
        else:
            super().__setattr__(name, value)


class _LayoutConstantAttribute(_LayoutBaseAttribute):
    def __init__(self, view, attribute, other=None, other_attribute=LayoutAttribute.notAnAttribute):
        super().__init__(view, attribute, other, other_attribute)

    def constraint(self, relation, value, priority):
        constraint = _LayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
            self.view, int(self.attribute), int(relation), self.other, int(self.other_attribute), 1.0, value
        )
        constraint.setPriority_(priority)
        return constraint


class _LayoutMultiplierAttribute(_LayoutBaseAttribute):
    def __init__(self, view, attribute, other=None, other_attribute=LayoutAttribute.notAnAttribute):
        super().__init__(view, attribute, other, other_attribute)

    def constraint(self, relation, value, priority):
        constraint = _LayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
            self.view, int(self.attribute), int(relation), self.other, int(self.other_attribute), value, 0
        )
        constraint.setPriority_(priority)
        return constraint


class Layout:
    _definitions = {
        "width": (_LayoutConstantAttribute, LayoutAttribute.width, LayoutAttribute.notAnAttribute),
        "height": (_LayoutConstantAttribute, LayoutAttribute.height, LayoutAttribute.notAnAttribute),

        "align_center_x_to": (_LayoutConstantAttribute, LayoutAttribute.centerX, LayoutAttribute.centerX),
        "align_center_y_to": (_LayoutConstantAttribute, LayoutAttribute.centerY, LayoutAttribute.centerY),
        "align_leading_to": (_LayoutConstantAttribute, LayoutAttribute.leading, LayoutAttribute.leading),
        "align_trailing_to": (_LayoutConstantAttribute, LayoutAttribute.trailing, LayoutAttribute.trailing),
        "align_top_to": (_LayoutConstantAttribute, LayoutAttribute.top, LayoutAttribute.top),
        "align_bottom_to": (_LayoutConstantAttribute, LayoutAttribute.bottom, LayoutAttribute.bottom),
        "align_left_to": (_LayoutConstantAttribute, LayoutAttribute.left, LayoutAttribute.left),
        "align_right_to": (_LayoutConstantAttribute, LayoutAttribute.right, LayoutAttribute.right),
        "align_baseline_to": (_LayoutConstantAttribute, LayoutAttribute.baseline, LayoutAttribute.baseline),

        "align_center_x_with_superview": (_LayoutConstantAttribute, LayoutAttribute.centerX, LayoutAttribute.centerX),
        "align_center_y_with_superview": (_LayoutConstantAttribute, LayoutAttribute.centerY, LayoutAttribute.centerY),
        "align_leading_with_superview": (_LayoutConstantAttribute, LayoutAttribute.leading, LayoutAttribute.leading),
        "align_trailing_with_superview": (_LayoutConstantAttribute, LayoutAttribute.trailing, LayoutAttribute.trailing),
        "align_top_with_superview": (_LayoutConstantAttribute, LayoutAttribute.top, LayoutAttribute.top),
        "align_bottom_with_superview": (_LayoutConstantAttribute, LayoutAttribute.bottom, LayoutAttribute.bottom),
        "align_left_with_superview": (_LayoutConstantAttribute, LayoutAttribute.left, LayoutAttribute.left),
        "align_right_with_superview": (_LayoutConstantAttribute, LayoutAttribute.right, LayoutAttribute.right),

        "relative_superview_width": (_LayoutMultiplierAttribute, LayoutAttribute.width, LayoutAttribute.width),
        "relative_superview_height": (_LayoutMultiplierAttribute, LayoutAttribute.height, LayoutAttribute.height),

        "relative_width_to": (_LayoutMultiplierAttribute, LayoutAttribute.width, LayoutAttribute.width),
        "relative_height_to": (_LayoutMultiplierAttribute, LayoutAttribute.height, LayoutAttribute.height),

        "left_offset_to": (_LayoutConstantAttribute, LayoutAttribute.left, LayoutAttribute.right),
        "right_offset_to": (_LayoutConstantAttribute, LayoutAttribute.right, LayoutAttribute.left),
        "top_offset_to": (_LayoutConstantAttribute, LayoutAttribute.top, LayoutAttribute.bottom),
        "bottom_offset_to": (_LayoutConstantAttribute, LayoutAttribute.bottom, LayoutAttribute.top),
        "leading_offset_to": (_LayoutConstantAttribute, LayoutAttribute.leading, LayoutAttribute.trailing),
        "trailing_offset_to": (_LayoutConstantAttribute, LayoutAttribute.trailing, LayoutAttribute.leading)
    }

    def __init__(self, view):
        assert(isinstance(view, LayoutProxy))

        self._view = view
        self._attributes = {}

    def _create_attribute(self, cls, attribute, other_attribute, other):
        assert(isinstance(attribute, LayoutAttribute))
        if other:
            assert(isinstance(other_attribute, LayoutAttribute))
            assert(isinstance(other, ui.View))

        name = '{}{}{}'.format(int(attribute), id(other), int(other_attribute))

        layout_attribute = self._attributes.get(name, None)
        if layout_attribute:
            return layout_attribute

        layout_attribute = cls(self._view, attribute, other, other_attribute)
        self._attributes[name] = layout_attribute
        return layout_attribute

    def _attribute(self, name, definition):
        cls = definition[0]
        attribute = definition[1]
        other_attribute = definition[2]

        assert(isinstance(attribute, LayoutAttribute))
        assert(isinstance(other_attribute, LayoutAttribute))

        if 'superview' in name:
            return self._create_attribute(cls, attribute, other_attribute, self._view.superview)
        elif name.endswith('_to'):
            return partial(self._create_attribute, cls, attribute, other_attribute)
        else:
            assert(other_attribute is LayoutAttribute.notAnAttribute)
            return self._create_attribute(cls, attribute, other_attribute, None)

    def __getattr__(self, name):
        if name in self._definitions:
            return self._attribute(name, self._definitions[name])

        return super().__getattr__(name)

    def center_in_superview(self):
        self.align_center_x_in_superview.equal = 0
        self.align_center_y_in_superview.equal = 0


class LayoutProxy(ui.View):
    _attributes = [
        '_view', '_view_objc', '_layout', '_objc', 'layout', 'view'
    ]

    def __init__(self, view):
        assert(isinstance(view, ui.View))

        self._view = view
        self.add_subview(self._view)

        self._view_objc = ObjCInstance(self._view)
        self._objc = ObjCInstance(self)

        self._view_objc.setTranslatesAutoresizingMaskIntoConstraints_(False)
        self._objc.setTranslatesAutoresizingMaskIntoConstraints_(False)

        attributes = [LayoutAttribute.left, LayoutAttribute.right, LayoutAttribute.top, LayoutAttribute.bottom]
        for attribute in attributes:
            constraint = _LayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
                self._view_objc, int(attribute), int(LayoutRelation.equal), self._objc, int(attribute), 1.0, 0
            )
            self._objc.addConstraint_(constraint)

        self._layout = None

    @property
    def layout(self):
        if not self._layout:
            self._layout = Layout(self)

        return self._layout

    @property
    def view(self):
        return self._view

    def __getattr__(self, name):
        if name in self._attributes:
            return super().__getattr__(name)
        return self._view.__getattr__(name)

    def __setattr__(self, name, value):
        if name in self._attributes:
            return super().__setattr__(name, value)
        return self._view.__setattr__(name, value)
