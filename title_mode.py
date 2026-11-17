"""Dungeon title menu with mouse and keyboard navigation."""
import math


class TitleMode:
    labels = ('던전 입장', '조작 방법', '게임 종료')
    menu_x = 104
    menu_y = 422
    menu_width = 364
    menu_height = 62
    menu_gap = 78

    def __init__(self):
        self.elapsed = 0.0
        self.selected = 0
        self.help_open = False

    def update(self, view, dt):
        self.elapsed += dt

    def hover(self, x, y):
        for index in range(len(self.labels)):
            top = self.menu_y + index*self.menu_gap
            if self.menu_x <= x <= self.menu_x+self.menu_width and top <= y <= top+self.menu_height:
                self.selected = index
                return index
        return None

    def activate(self, view):
        if self.selected == 0:
            view.game = None
            view.selected = [None] * 4
            view.change_mode('selection')
        elif self.selected == 1:
            self.help_open = True
        else:
            return False
        return True

    def handle_key(self, view, key):
        p = view.p
        if self.help_open:
            if key in (p.SDLK_ESCAPE, p.SDLK_RETURN, p.SDLK_SPACE):
                self.help_open = False
            return True
        if key == p.SDLK_ESCAPE:
            return False
        if key in (p.SDLK_UP, p.SDLK_w):
            self.selected = (self.selected-1) % len(self.labels)
        elif key in (p.SDLK_DOWN, p.SDLK_s):
            self.selected = (self.selected+1) % len(self.labels)
        elif key in (p.SDLK_RETURN, p.SDLK_SPACE):
            return self.activate(view)
        return True

    def click(self, view, x, y):
        if self.help_open:
            if 490 <= x <= 790 and 598 <= y <= 650:
                self.help_open = False
            return True
        if self.hover(x, y) is not None:
            return self.activate(view)
        return True

    def draw(self, view):
        view.title_background.draw(640, 400, 1280, 800)
        # Rising embers animate independently of the menu and its hit areas.
        for index in range(24):
            x = 698 + (index*137) % 550 + math.sin(self.elapsed+index)*12
            y = 760 - (index*47+self.elapsed*(17+index%5)) % 650
            view.rect(x, y, 2, 3, (219, 162, 77), 120)
        view.draw_brand(68, 86, 450, 230)
        view.center_text('성격의 시험장', 286, 332, 24, (122, 217, 211), font='heading')
        for index, label in enumerate(self.labels):
            top = self.menu_y + index*self.menu_gap
            active = self.selected == index
            view.stone_panel(self.menu_x, top, self.menu_width, self.menu_height, active)
            view.center_text(label, self.menu_x+self.menu_width/2, top+15, 24,
                             (250, 222, 161) if active else (188, 184, 178), font='heading')
            if active:
                view.text('◆', self.menu_x+21, top+20, 16, (110, 225, 215))
        view.text('↑ ↓ 선택    Enter / Space 확인    마우스 클릭', 105, 705, 16, (172, 174, 179))
        view.text('F11 / Alt+Enter  전체화면 전환', 105, 742, 16, (172, 174, 179))
        if self.help_open:
            self.draw_help(view)
        fade = max(0, 1-self.elapsed/0.45)
        if fade:
            view.rect(0, 0, 1280, 800, (0, 0, 0), round(fade*255))

    def draw_help(self, view):
        view.rect(0, 0, 1280, 800, (3, 6, 14), 210)
        view.stone_panel(298, 137, 684, 541, True)
        view.center_text('탐험 안내', 640, 169, 30, (239, 211, 157), font='heading')
        view.center_text('네 지표를 선택하고 열쇠를 찾아 출구로 이동하세요.', 640, 227, 21)
        controls = (
            ('WASD / 방향키', '캐릭터 이동'),
            ('Space', '대화 · 열쇠 획득 · 출구 열기'),
            ('1 · 2 · 3 · 4', '장착한 네 가지 능력 사용'),
            ('R', 'MBTI 다시 선택'),
            ('F11 / Alt+Enter', '전체화면 · 창 모드 전환'),
            ('Esc', '선택 화면에서 타이틀 / 던전에서 종료'),
        )
        for index, (key, description) in enumerate(controls):
            y = 286 + index*46
            view.text(key, 337, y, 18, (119, 214, 205))
            view.text(description, 520, y, 18, (224, 221, 212))
        view.stone_panel(490, 598, 300, 52, True)
        view.center_text('돌아가기  Enter / Esc', 640, 611, 18, (239, 211, 157))
