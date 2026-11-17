"""Timed opening logo, following the logo-to-title flow in gameframe."""
import math


class LogoMode:
    duration = 2.8

    def __init__(self):
        self.elapsed = 0.0

    def update(self, view, dt):
        self.elapsed += dt
        if self.elapsed >= self.duration:
            view.change_mode('title')

    def handle_key(self, view, key):
        if key == view.p.SDLK_ESCAPE:
            return False
        if key in (view.p.SDLK_RETURN, view.p.SDLK_SPACE):
            view.change_mode('title')
        return True

    def draw(self, view):
        view.rect(0, 0, 1280, 800, (8, 11, 21))
        pulse = math.sin(self.elapsed * 2.5) * 8
        view.draw_brand(240-pulse/2, 170-pulse/4, 800+pulse, 400+pulse/2)
        view.center_text('성격의 시험장', 640, 612, 24, (105, 202, 198), font='heading')
        view.center_text('Enter / Space  건너뛰기', 640, 737, 16, (137, 143, 158))
        opacity = min(1.0, self.elapsed / 0.65, (self.duration-self.elapsed) / 0.55)
        view.rect(0, 0, 1280, 800, (0, 0, 0), round(255*(1-max(0, opacity))))
