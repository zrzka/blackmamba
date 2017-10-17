#!python3

from objc_util import ObjCInstance, UIApplication, on_main_thread
import ui
from enum import IntEnum
from blackmamba.uikit.autolayout import LayoutProxy
from blackmamba.ide.theme import get_theme_value

_OVERLAY_BAR_HEIGHT = 33
_OVERLAY_RESIZE_SIZE = 33
_OVERLAY_MIN_WIDTH = 200
_OVERLAY_MIN_HEIGHT = _OVERLAY_BAR_HEIGHT + _OVERLAY_RESIZE_SIZE

_manager = None


def get_manager():
    global _manager
    if _manager is None:
        _manager = OverlayManager()
    return _manager


class OverlayState(IntEnum):
    expanded = 1 << 1
    active = 1 << 2


class OverlayResizeView(ui.View):
    def __init__(self, container, left=True):
        self._container = container
        self._left = left
        self._touch_began_location = None
        self._initial_container_frame = None
        self._container_superview = ObjCInstance(container).superview()

    def touch_began(self, touch):
        self._container.become_active()
        self._touch_began_location = ObjCInstance(touch).locationInView_(self._container_superview)
        self._initial_container_frame = self._container.frame

    def touch_moved(self, touch):
        location = ObjCInstance(touch).locationInView_(self._container_superview)
        dx = location.x - self._touch_began_location.x
        dy = location.y - self._touch_began_location.y

        f = self._initial_container_frame
        nh = max(f.height + dy, _OVERLAY_MIN_HEIGHT)
        if self._left:
            nw = f.width - dx
            nx = f.x + dx
            # Don't move x if we reach min width
            if nw <= _OVERLAY_MIN_WIDTH:
                nx -= _OVERLAY_MIN_WIDTH - nw
                nw = _OVERLAY_MIN_WIDTH
        else:
            nw = max(f.width + dx, _OVERLAY_MIN_WIDTH)
            nx = f.x

        self._container.frame = (nx, f.y, nw, nh)

    def touch_ended(self, touch):
        self._touch_began_location = None
        self._initial_container_frame = None


class OverlayBarView(ui.View):
    def __init__(self, container, state):
        self._container = container
        self._touch_began_location = None
        self._initial_container_frame = None
        self._container_superview = ObjCInstance(container).superview()

        label = LayoutProxy(ui.Label())
        label.font = ('<system>', 13.0)
        label.alignment = ui.ALIGN_CENTER
        label.text_color = get_theme_value('bar_title_color')
        label.touch_enabled = False
        self.add_subview(label)
        label.layout.align_left_with_superview.equal = 0
        label.layout.align_right_with_superview.equal = 0
        label.layout.align_center_y_with_superview.equal = 0
        self.title_label = label

        button = LayoutProxy(ui.Button(title='x', tint_color=get_theme_value('tint_color')))
        self.add_subview(button)
        button.layout.align_left_with_superview.equal = 0
        button.layout.align_top_with_superview.equal = 0
        button.layout.align_bottom_with_superview.equal = 0
        button.layout.width.equal = _OVERLAY_BAR_HEIGHT
        self.close_button = button

        button = LayoutProxy(ui.Button(title='-', tint_color=get_theme_value('tint_color')))
        self.add_subview(button)
        button.layout.align_right_with_superview.equal = 0
        button.layout.align_top_with_superview.equal = 0
        button.layout.align_bottom_with_superview.equal = 0
        button.layout.width.equal = _OVERLAY_BAR_HEIGHT
        self.collapse_button = button

        separator = LayoutProxy(ui.View(background_color=get_theme_value('separator_color')))
        self.add_subview(separator)
        separator.layout.height.equal = 1
        separator.layout.align_left_with_superview.equal = 0
        separator.layout.align_bottom_with_superview.equal = 0
        separator.layout.align_right_with_superview.equal = 0
        self.separator = separator

        self.update_appearance(state)

    def touch_began(self, touch):
        self._container.become_active()
        self._touch_began_location = ObjCInstance(touch).locationInView_(self._container_superview)
        self._initial_container_frame = self._container.frame

    def touch_moved(self, touch):
        location = ObjCInstance(touch).locationInView_(self._container_superview)
        self._container.x = self._initial_container_frame.x + location.x - self._touch_began_location.x
        self._container.y = self._initial_container_frame.y + location.y - self._touch_began_location.y

    def touch_ended(self, touch):
        self._touch_began_location = None
        self._initial_container_frame = None

    def update_appearance(self, state):
        if state & OverlayState.active:
            self.background_color = get_theme_value('active_bar_background_color')
        else:
            self.background_color = get_theme_value('inactive_bar_background_color')

        if state & OverlayState.expanded:
            self.collapse_button.title = '-'
        else:
            self.collapse_button.title = '+'


class OverlayDelegate:
    def did_close(self, overlay):
        pass

    def did_become_active(self, overlay):
        pass


class OverlayView(ui.View):
    def __init__(self, title, content, delegate, tag):
        self._state = OverlayState.expanded | OverlayState.active
        self._expanded_height = None
        self._delegate = delegate
        self.tag = tag

        bar = OverlayBarView(self, self._state)
        bar.close_button.action = self.dismiss
        bar.collapse_button.action = self.toggle_collapse
        bar.title_label.text = title
        bar = LayoutProxy(bar)
        self.add_subview(bar)
        bar.layout.height.equal = _OVERLAY_BAR_HEIGHT
        bar.layout.align_left_with_superview.equal = 0
        bar.layout.align_top_with_superview.equal = 0
        bar.layout.align_right_with_superview.equal = 0
        self._bar = bar

        content = LayoutProxy(content)
        self.add_subview(content)
        content.layout.align_left_with_superview.equal = 0
        content.layout.align_right_with_superview.equal = 0
        content.layout.align_bottom_with_superview.equal = 0
        content.layout.top_offset_to(bar).equal = 0
        self._content_view = content

        resize = LayoutProxy(OverlayResizeView(self, True))
        self.add_subview(resize)
        resize.layout.align_left_with_superview.equal = 0
        resize.layout.align_bottom_with_superview.equal = 0
        resize.layout.width.equal = 44
        resize.layout.height.equal = 44
        self._left_resize_view = resize

        resize = LayoutProxy(OverlayResizeView(self, False))
        self.add_subview(resize)
        resize.layout.align_right_with_superview.equal = 0
        resize.layout.align_bottom_with_superview.equal = 0
        resize.layout.width.equal = 44
        resize.layout.height.equal = 44
        self._right_resize_view = resize

        self._bar.bring_to_front()

        self.corner_radius = 4
        self.border_width = 1.0
        self.border_color = get_theme_value('separator_color')
        self.update_appearance()

    @property
    def title(self):
        return self._bar.title_label.text

    @title.setter
    def title(self, new_value):
        self._bar.title_label.text = new_value

    @property
    def content_view(self):
        return self._content_view.view

    @property
    def state(self):
        return self._state

    def become_active(self):
        self.bring_to_front()

        if self.is_active():
            return

        self._state |= OverlayState.active
        self.update_appearance()
        if self._delegate:
            self._delegate.did_become_active(self)

    def become_inactive(self):
        if not self._state & OverlayState.active:
            return
        self._state &= ~OverlayState.active
        self.update_appearance()

    def is_active(self):
        return self._state & OverlayState.active == OverlayState.active

    def is_expanded(self):
        return self._state & OverlayState.expanded == OverlayState.expanded

    def expand(self):
        if self.is_expanded():
            return

        self.height = self._expanded_height
        self._expanded_height = None
        self._left_resize_view.touch_enabled = True
        self._right_resize_view.touch_enabled = True
        self._state |= OverlayState.expanded
        self.update_appearance()

    def collapse(self):
        if not self.is_expanded():
            return

        self._expanded_height = self.height
        self.height = _OVERLAY_BAR_HEIGHT
        self._left_resize_view.touch_enabled = False
        self._right_resize_view.touch_enabled = False
        self._state &= ~OverlayState.expanded
        self.update_appearance()

    def update_appearance(self):
        self._bar.update_appearance(self._state)

    @on_main_thread
    def dismiss(self, sender=None):
        from objc_util import ObjCInstance
        ObjCInstance(self).removeFromSuperview()
        if self._delegate:
            self._delegate.did_close(self)

    def toggle_collapse(self, collapse_button):
        if self.is_expanded():
            self.collapse()
        else:
            self.expand()


class OverlayManager(OverlayDelegate):
    def __init__(self):
        self._overlays = []

    @on_main_thread
    def present(self, title, content, frame=None, tag=None):
        overlay = OverlayView(title, content, self, tag)
        if frame:
            overlay.width = max(_OVERLAY_MIN_WIDTH, frame[2])
            overlay.height = max(_OVERLAY_MIN_HEIGHT, frame[3])
            overlay.x = frame[0]
            overlay.y = frame[1]
        else:
            overlay.width = _OVERLAY_MIN_WIDTH
            overlay.height = _OVERLAY_MIN_HEIGHT
            overlay.x = 50
            overlay.y = 110
        self.tag = tag

        for o in self._overlays:
            if o.is_active():
                o.become_inactive()

        self._overlays.append(overlay)

        window = UIApplication.sharedApplication().keyWindow()
        window.addSubview_(overlay)

        return overlay

    def did_close(self, overlay):
        try:
            self._overlays.remove(overlay)
            overlay = self._overlays[-1]
            overlay.become_active()
        except ValueError:
            # Overlay does not exist
            pass
        except IndexError:
            # No more overlays
            pass

    def did_become_active(self, overlay):
        for o in self._overlays:
            if o.is_active() and o is not overlay:
                o.become_inactive()
        try:
            index = self._overlays.index(overlay)
            del self._overlays[index]
            self._overlays.append(overlay)
        except ValueError:
            pass

    def get_overlay(self, tag):
        for o in self._overlays:
            if o.tag == tag:
                return o
        return None

    def dismiss_active_overlay(self):
        try:
            overlay = self._overlays[-1]
            overlay.dismiss()
        except IndexError:
            # No more overlays
            pass


def dismiss_active_overlay():
    get_manager().dismiss_active_overlay()
