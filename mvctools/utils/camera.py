from mvctools.sprite import ViewSprite
from mvctools.model import BaseModel
from mvctools.view import BaseView
from pygame import Surface, Rect
from mvctools import xytuple

class CameraModel(BaseModel):

    camera_speed = None

    def init_camera(self, rect, speed=None):
        self.base_rect = Rect(rect)
        self.camera_rect = Rect(rect)
        self.target_rect = Rect(rect)
        self.camera_speed = speed
        self.old_camera_rect = None

    def reset_camera(self, force=False):
        self.target_rect = self.base_rect
        if force:
            self.camera_rect = self.base_rect

    def set_camera(self, rect):
        self.target_rect = Rect(rect)

    @property
    def camera_changed(self):
        return self.camera_rect != self.old_camera_rect

    @property
    def is_camera_set(self):
        return not self.target_rect == self.base_rect

    def post_update(self):
        # Save current
        self.old_camera_rect = self.camera_rect
        # No speed
        if self.camera_speed is None:
            self.camera_rect = Rect(self.target_rect)
            return
        # Get reference
        delta = {}
        for attr in ("top", "left", "bottom", "right"):
            target = getattr(self.target_rect, attr)
            current = getattr(self.camera_rect, attr)
            delta[attr] = float(target) - current
        ref = max(map(abs, delta.values()))
        step = float(self.delta * self.camera_speed)
        # Close enough
        if ref <= step:
            self.camera_rect = Rect(self.target_rect)
            return
        # Get new values
        ratio = step/ref
        dct = {}
        for attr in ("top", "left", "bottom", "right"):
            current = getattr(self.camera_rect, attr)
            dct[attr] = current + delta[attr] * ratio
        # Create rect
        for attr in dct:
            dct[attr] = round(dct[attr])
        size = dct["right"] - dct["left"], dct["bottom"] - dct["top"]
        topleft = dct["left"], dct["top"]
        self.camera_rect = Rect(topleft, size)


class CameraSprite(ViewSprite):

    @property
    def size(self):
        return self.parent.screen_size

    def get_rect(self):
        return self.image.get_rect()

    def transform(self, screen, dirty):
        # No update needed
        if not dirty and not self.model.camera_changed:
            return self.image, None
        # Crop the screen with the camera rectangle
        if self.model.camera_rect != screen.get_rect():
            cropped = screen.subsurface(self.model.camera_rect)
            return ViewSprite.transform(self, cropped, None)
        # Update needed
        if self.model.camera_changed:
            self.set_dirty()
            dirty = None
        return ViewSprite.transform(self, screen, dirty)

    def convert_position(self, pos):
        new_pos = ViewSprite.convert_position(self, pos)
        new_pos /= self.view.screen_size
        new_pos *= self.model.camera_rect.size
        return new_pos + self.model.camera_rect.topleft


