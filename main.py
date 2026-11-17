"""MBTI Dungeon week-two demo. Run with Python 3 and pico2d."""
import argparse
import ctypes
import math
import os
import time
from pathlib import Path

from game_model import ABILITIES, MAP, PAIRS, ROOT, Game
from logo_mode import LogoMode
from title_mode import TitleMode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--capture', action='store_true', help='Export actual rendered demo screens')
    args = parser.parse_args()
    if args.capture:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        os.environ['SDL_RENDER_DRIVER'] = 'software'
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
    import pico2d.pico2d as p
    p.open_canvas(1280, 800)
    p.hide_lattice()
    view = View(p)
    try:
        if args.capture:
            view.capture_all()
            return
        p.SDL_MaximizeWindow(p.window)
        previous = time.perf_counter()
        pressed = set()
        running = True
        while running:
            now = time.perf_counter()
            dt, previous = min(now - previous, 0.1), now
            for event in p.get_events():
                if event.type == p.SDL_QUIT:
                    running = False
                elif event.type == p.SDL_KEYUP:
                    pressed.discard(event.key)
                elif event.type == p.SDL_KEYDOWN:
                    pressed.add(event.key)
                    previous_mode = view.mode
                    running = view.handle_key(event.key)
                    if view.mode != previous_mode:
                        pressed.clear()
                elif event.type == p.SDL_MOUSEMOTION:
                    view.hover(event.x, event.y)
                elif event.type == p.SDL_MOUSEBUTTONDOWN and event.button == p.SDL_BUTTON_LEFT:
                    previous_mode = view.mode
                    running = view.click(event.x, event.y)
                    if view.mode != previous_mode:
                        pressed.clear()
                if not running:
                    break
            if not running:
                break
            if not p.SDL_GetWindowFlags(p.window) & p.SDL_WINDOW_INPUT_FOCUS:
                pressed.clear()
            if not p.SDL_GetMouseFocus():
                view.hovered_ability = None
            dx = int(p.SDLK_d in pressed or p.SDLK_RIGHT in pressed) - int(p.SDLK_a in pressed or p.SDLK_LEFT in pressed)
            dy = int(p.SDLK_s in pressed or p.SDLK_DOWN in pressed) - int(p.SDLK_w in pressed or p.SDLK_UP in pressed)
            view.update(dt, dx, dy)
            view.draw()
            p.update_canvas()
            p.delay(0.008)
    finally:
        p.close_canvas()


class View:
    def __init__(self, p):
        self.p = p
        p.SDL_SetWindowResizable(p.window, p.SDL_TRUE)
        # SDL also maps mouse events into these logical game coordinates.
        if p.SDL_RenderSetLogicalSize(p.renderer, 1280, 800) != 0:
            raise RuntimeError(p.SDL_GetError().decode('utf-8', errors='replace'))
        font_dir = ROOT / 'assets/fonts'
        self.fonts = {
            'body': {size: p.load_font(str(font_dir / 'NanumMyeongjo-Regular.ttf'), size)
                     for size in (16, 18, 21, 24, 30, 42, 64)},
            'heading': {size: p.load_font(str(font_dir / 'NanumMyeongjo-Bold.ttf'), size)
                        for size in (21, 24, 30, 42)},
            'display': {size: p.load_font(str(font_dir / 'Cinzel.ttf'), size)
                        for size in (30, 42, 64)},
            'sigil': {size: p.load_font(str(font_dir / 'CinzelDecorative-Bold.ttf'), size)
                      for size in (30, 42)},
            'engraved': {size: p.load_font(str(font_dir / 'NanumMyeongjo-ExtraBold.ttf'), size)
                         for size in (24, 30, 42)},
        }
        self.atlas = p.load_image(str(ROOT / 'assets/dungeon_atlas.png'))
        self.title_background = p.load_image(str(ROOT / 'assets/title_background.png'))
        self.wordmark = p.load_image(str(ROOT / 'assets/mbti_dungeon_wordmark.png'))
        self.ability_tablet = p.load_image(str(ROOT / 'assets/ability_tablet.png'))
        self.cell = self.atlas.w // 4
        self.selected = [None] * 4
        self.selection_elapsed = 0.0
        self.hovered_ability = None
        self.game = None
        self.mode = 'logo'
        self.logo = LogoMode()
        self.title = TitleMode()

    def rect(self, x, y, w, h, color, alpha=255):
        p = self.p
        p.SDL_SetRenderDrawBlendMode(p.renderer, p.SDL_BLENDMODE_BLEND)
        p.SDL_SetRenderDrawColor(p.renderer, *color, alpha)
        rect = p.SDL_Rect(int(x), int(y), int(w), int(h))
        p.SDL_RenderFillRect(p.renderer, ctypes.byref(rect))

    def text(self, text, x, y, size=21, color=(227, 232, 245), font='body'):
        self.fonts[font][size].draw(x, 800 - y - size, text, color)

    def center_text(self, text, center_x, y, size=21, color=(227, 232, 245), font='body'):
        width, height = ctypes.c_int(), ctypes.c_int()
        self.p.TTF_SizeUTF8(self.fonts[font][size].font, text.encode('utf-8'), ctypes.byref(width), ctypes.byref(height))
        self.text(text, center_x-width.value/2, y, size, color, font)

    def draw_brand(self, x, y, width, height):
        scale = min(width/self.wordmark.w, height/self.wordmark.h)
        self.wordmark.draw(x+width/2, 800-y-height/2,
                           self.wordmark.w*scale, self.wordmark.h*scale)

    def stone_panel(self, x, y, w, h, active=False):
        border = (169, 134, 76) if active else (83, 77, 79)
        self.rect(x, y, w, h, (8, 12, 21), 240)
        self.rect(x, y, w, 1, border)
        self.rect(x, y+h-1, w, 1, border)
        self.rect(x, y, 1, h, border)
        self.rect(x+w-1, y, 1, h, border)
        self.rect(x+4, y+4, w-8, 1, (57, 65, 68))
        if active:
            self.rect(x+1, y+1, 3, h-2, (98, 205, 194))

    def change_mode(self, mode):
        self.mode = mode
        self.hovered_ability = None
        if mode == 'title':
            self.title = TitleMode()
        elif mode == 'selection':
            self.selection_elapsed = 0.0

    def update(self, dt, dx=0, dy=0):
        if self.mode == 'logo':
            self.logo.update(self, dt)
        elif self.mode == 'title':
            self.title.update(self, dt)
        elif self.mode == 'play':
            self.game.update(dt, dx, dy)
        elif self.mode == 'selection':
            self.selection_elapsed += dt

    def handle_key(self, key):
        p = self.p
        if key == p.SDLK_F11 or (key == p.SDLK_RETURN and p.SDL_GetModState() & p.KMOD_ALT):
            self.toggle_fullscreen()
            return True
        if self.mode == 'logo':
            return self.logo.handle_key(self, key)
        if self.mode == 'title':
            return self.title.handle_key(self, key)
        if key == p.SDLK_ESCAPE:
            if self.mode == 'selection':
                self.change_mode('title')
                return True
            return False
        if self.mode == 'play':
            if key == p.SDLK_r:
                self.game = None
                self.change_mode('selection')
            elif key in (p.SDLK_1, p.SDLK_2, p.SDLK_3, p.SDLK_4):
                self.game.use(key-p.SDLK_1)
            elif key == p.SDLK_SPACE:
                self.game.interact()
        elif key == p.SDLK_RETURN:
            self.start()
        return True

    def toggle_fullscreen(self):
        p = self.p
        self.hovered_ability = None
        fullscreen = p.SDL_GetWindowFlags(p.window) & p.SDL_WINDOW_FULLSCREEN
        target = 0 if fullscreen else p.SDL_WINDOW_FULLSCREEN_DESKTOP
        if p.SDL_SetWindowFullscreen(p.window, target) != 0:
            print('전체화면 전환 실패:', p.SDL_GetError().decode('utf-8', errors='replace'))
            return False
        if fullscreen:
            p.SDL_MaximizeWindow(p.window)
        return True

    def sprite(self, row, col, x, y, w, h, flip=False):
        c = self.cell
        # Skip cell borders and preserve equal atlas grid coordinates.
        inset = 18 if row == 0 and col < 2 else 8
        self.atlas.clip_composite_draw(col*c+inset, self.atlas.h-(row+1)*c+inset, c-2*inset, c-2*inset,
                                       0, 'h' if flip else '', x+w/2, 800-y-h/2, w, h)

    def start(self):
        if self.mode == 'selection' and all(self.selected):
            self.game = Game(''.join(self.selected))
            self.change_mode('play')

    def click(self, x, y):
        if self.mode == 'logo':
            self.change_mode('title')
            return True
        if self.mode == 'title':
            return self.title.click(self, x, y)
        if self.mode != 'selection':
            return True
        self.hover(x, y)
        if self.hovered_ability:
            index, letter, _, _ = self.hovered_ability
            self.selected[index] = letter
        if 938 <= x <= 1210 and 655 <= y <= 724:
            self.start()
        return True

    def hover(self, x, y):
        self.hovered_ability = None
        if self.mode == 'title' and not self.title.help_open:
            self.title.hover(x, y)
        elif self.mode == 'selection':
            for index, pair in enumerate(PAIRS):
                for option, letter in enumerate(pair):
                    left, top = 64+index*292, 258+option*150
                    if left <= x <= left+272 and top <= y <= top+130:
                        self.hovered_ability = (index, letter, left, top)
                        return

    def draw(self):
        # Clear the complete output, including letterbox bars outside the game.
        self.p.SDL_SetRenderDrawColor(self.p.renderer, 0, 0, 0, 255)
        self.p.SDL_RenderClear(self.p.renderer)
        self.rect(0, 0, 1280, 800, (12, 16, 30))
        if self.mode == 'logo':
            self.logo.draw(self)
        elif self.mode == 'title':
            self.title.draw(self)
        elif self.mode == 'play':
            self.draw_dungeon()
        else:
            self.draw_selection()

    def draw_selection(self):
        self.title_background.draw(640, 400, 1280, 800)
        self.rect(0, 0, 1280, 800, (7, 9, 22), 218)
        self.draw_brand(50, 8, 480, 178)
        self.text('능력 선택', 568, 67, 42, (4, 10, 18), font='engraved')
        self.text('능력 선택', 566, 65, 42, (222, 202, 153), font='engraved')
        count = sum(letter is not None for letter in self.selected)
        self.text(f'선택한 지표  {count} / 4', 570, 135, 18, (123, 213, 206))
        self.text('마우스를 올려 능력을 확인하고, 각 지표에서 하나씩 선택하세요.', 68, 192, 21)
        labels = ('에너지 방향', '정보 수집', '판단 방식', '생활 방식')
        for index, pair in enumerate(PAIRS):
            x = 64+index*292
            self.center_text(labels[index], x+136, 228, 18, (206, 187, 145))
            for option, letter in enumerate(pair):
                self.draw_ability_tablet(letter, x, 258+option*150, self.selected[index] == letter)
        self.rect(68, 565, 1140, 1, (112, 94, 66))
        mbti = ''.join(letter or '?' for letter in self.selected)
        self.text(mbti, 70, 590, 42, (233, 204, 145), font='sigil')
        if all(self.selected):
            for index, letter in enumerate(self.selected):
                self.center_text(ABILITIES[letter]['name'], 352+index*152, 603, 24,
                                 (143, 228, 217), font='engraved')
        else:
            self.text('네 지표를 모두 선택하면 던전의 문이 열립니다.', 300, 611, 18, (182, 177, 163))
        self.stone_panel(938, 655, 272, 69, all(self.selected))
        self.text('던전 입장  Enter', 967, 673, 24,
                  (239, 218, 172) if all(self.selected) else (130, 131, 138), font='engraved')
        self.text('마우스 선택    Enter 입장    Esc 타이틀로    F11 전체화면', 68, 697, 18, (158, 170, 197))
        if self.hovered_ability:
            self.draw_ability_tooltip()

    def wrap_text(self, text, max_width, size=18):
        lines, line = [], ''
        width, height = ctypes.c_int(), ctypes.c_int()
        for character in text:
            candidate = line+character
            self.p.TTF_SizeUTF8(self.fonts['body'][size].font, candidate.encode('utf-8'),
                                ctypes.byref(width), ctypes.byref(height))
            if width.value > max_width and line:
                lines.append(line.rstrip())
                line = character.lstrip()
            else:
                line = candidate
        if line:
            lines.append(line.rstrip())
        return lines

    def draw_ability_tooltip(self):
        index, letter, left, top = self.hovered_ability
        ability = ABILITIES[letter]
        lines = self.wrap_text(ability['details'], 372)
        condition = ability['condition']
        if letter in 'EFT':
            condition += f" · {ability['range']}px 이내"
        elif letter == 'I':
            condition += f" · 반경 {ability['range']}px"
        conditions = self.wrap_text(condition, 372)
        height = 160+(len(lines)+len(conditions))*25
        x, y = min(left+16, 844), min(top+138, 784-height)
        self.rect(x+5, y+6, 420, height, (0, 0, 0), 160)
        self.rect(x, y, 420, height, (8, 12, 24))
        self.stone_panel(x, y, 420, height, True)
        self.text(f"{letter}  {ability['name']}", x+24, y+15, 24,
                  (245, 217, 159), font='engraved')
        cursor_y = y+62
        for line in lines:
            self.text(line, x+24, cursor_y, 18, (229, 226, 218))
            cursor_y += 25
        self.rect(x+24, cursor_y+8, 372, 1, (100, 88, 64))
        cursor_y += 22
        for line in conditions:
            self.text(line, x+24, cursor_y, 18, (127, 212, 203))
            cursor_y += 25
        effect = f"효과 {ability['duration']}초"
        if letter in 'ET':
            effect = '즉시 힌트 제공'
        elif letter == 'F':
            effect = f"체력 {ability['heal']} 회복"
        elif letter == 'P':
            effect += f" · 속도 {ability['speed_multiplier']}배"
        self.text(effect, x+24, cursor_y+8, 18, (222, 205, 164))
        self.text(f"재사용 {ability['cooldown']}초 · 입장 후 {index+1}번 키", x+24,
                  cursor_y+35, 18, (188, 189, 199))

    def draw_ability_tablet(self, letter, x, y, active):
        self.ability_tablet.opacify(1.0 if active else 0.80)
        self.ability_tablet.draw(x+136, 800-y-65, 272, 130)
        self.ability_tablet.opacify(1.0)
        if active:
            pulse = int(35*math.sin(self.selection_elapsed*2.5))
            self.rect(x+27, y+10, 218, 1, (104, 241, 222), 150+pulse)
            self.rect(x+27, y+120, 218, 1, (104, 241, 222), 150+pulse)
            self.rect(x+9, y+30, 1, 70, (104, 241, 222), 120+pulse)
            self.rect(x+262, y+30, 1, 70, (104, 241, 222), 120+pulse)
        self.center_text(letter, x+44, y+20, 42,
                         (136, 248, 232) if active else (187, 181, 170), font='sigil')
        self.rect(x+77, y+30, 1, 45, (119, 106, 78))
        name = ' '.join(ABILITIES[letter]['name'])
        self.text(name, x+96, y+27, 30, (0, 0, 0), font='engraved')
        self.text(name, x+94, y+25, 30,
                  (247, 222, 165) if active else (216, 202, 174), font='engraved')
        self.text(ABILITIES[letter]['description'], x+20, y+76, 16,
                  (196, 226, 221) if active else (166, 169, 176))

    def draw_dungeon(self):
        g = self.game
        self.text('MBTI DUNGEON', 40, 24, 30, font='display')
        self.text(MAP['name'], 40, 73, 18, (94, 225, 218))
        ox, oy, tile = 40, 128, g.tile
        for row, line in enumerate(MAP['rows']):
            for col, cell in enumerate(line):
                self.sprite(0, 1 if cell == '#' else 0, ox+col*tile, oy+row*tile, tile, tile)
        for tx, ty in MAP['traps']:
            x, y = ox+tx*tile, oy+ty*tile
            color = (92, 222, 229) if g.active('J') else ((238, 116, 128) if g.trap_on else (88, 73, 103))
            self.rect(x-16, y-7, 32, 14, color)
            if g.active('S') or (g.active('I') and math.hypot(tx*tile-g.x, ty*tile-g.y) < 160):
                self.text('!', x-5, y-42, 30, (255, 205, 120))
        nx, ny = g.position('npc')
        self.sprite(1, 0, ox+nx-23, oy+ny-38, 46, 60)
        self.text('안내자', ox+nx-26, oy+ny-69, 16)
        self.rect(ox+nx-24, oy+ny+26, 48, 5, (49, 46, 70))
        self.rect(ox+nx-24, oy+ny+26, 48*g.npc_hp/100, 5, (94, 225, 168))
        px, py = g.position('tablet')
        self.rect(ox+px-16, oy+py-22, 32, 40, (116, 104, 145))
        self.text('?', ox+px-6, oy+py-21, 24, (240, 197, 114))
        kx, ky = g.position('key')
        if not g.has_key:
            self.sprite(0, 2, ox+kx-22, oy+ky-25, 44, 50)
            if g.active('S'):
                self.text('열쇠', ox+kx-18, oy+ky-55, 18, (240, 197, 114))
        ex, ey = g.position('exit')
        self.sprite(0, 3, ox+ex-30, oy+ey-45, 60, 72)
        row, col = g.sprite_index()
        recoil = math.sin(g.bump*70)*3 if g.bump else 0
        self.sprite(row, col, ox+g.x-25+recoil, oy+g.y-40, 50, 64, g.facing == 'left')
        if g.active('N'):
            tx, ty = (ex, ey) if g.has_key else (kx, ky)
            angle = math.atan2(ty-g.y, tx-g.x)
            ax, ay = ox+g.x+math.cos(angle)*50, oy+g.y+math.sin(angle)*50
            self.text('목표', ax-16, ay-15, 18, (240, 197, 114))
            self.p.draw_line(ox+g.x, 800-oy-g.y, ax, 800-ay, 94, 225, 218)
        self.draw_hud()
        if g.cleared:
            self.rect(280, 300, 620, 160, (18, 30, 48))
            self.text('연습 맵 탐색 완료', 350, 325, 42, (94, 225, 218))
            self.text(f'{g.mbti}   {g.elapsed:.1f}초   R로 재선택', 370, 403, 24)

    def draw_hud(self):
        g = self.game
        self.text(g.mbti, 1030, 132, 42, (240, 197, 114), font='display')
        self.text('장착 능력', 1032, 204, 21, font='heading')
        for i, (letter, a) in enumerate(g.slots):
            y = 250+i*90
            self.text(f"{i+1}   {letter} {a['name']}", 1032, y, 24)
            remaining = g.cooldowns[letter]
            status = f'대기 {remaining:.1f}초' if remaining > 0 else '사용 가능'
            if g.active(letter):
                status = f'효과 {g.effects[letter]:.1f}초 / {remaining:.1f}초'
            self.text(status, 1032, y+38, 18, (94, 225, 218))
        self.text('열쇠 획득' if g.has_key else '열쇠 탐색 중', 1032, 636, 21, (240, 197, 114))
        self.text(f'{g.elapsed:05.1f}초', 1032, 679, 21)
        self.text(g.message, 40, 724, 18)
        self.text('WASD 이동    Space 상호작용    1~4 능력    R 재선택    Esc 종료    F11 전체화면', 40, 767, 16, (158, 170, 197))

    def screenshot(self, path):
        from PIL import Image
        p = self.p
        buffer = (ctypes.c_uint8 * (1280*800*4))()
        if p.SDL_RenderReadPixels(p.renderer, None, p.SDL_PIXELFORMAT_ABGR8888, buffer, 1280*4) != 0:
            raise RuntimeError(p.SDL_GetError())
        Image.frombytes('RGBA', (1280, 800), bytes(buffer)).save(path)

    def capture_all(self):
        out = ROOT / 'output/screens'
        out.mkdir(parents=True, exist_ok=True)
        self.logo.elapsed = 1.2
        self.draw()
        self.screenshot(out / '00_logo.png')
        self.change_mode('title')
        self.title.elapsed = 1.0
        self.draw()
        self.screenshot(out / '00_title.png')
        self.title.help_open = True
        self.draw()
        self.screenshot(out / '00_controls.png')
        self.change_mode('selection')
        for index, letter in enumerate('INTJ'):
            option = PAIRS[index].index(letter)
            self.click(80+index*292, 280+option*150)
        self.hovered_ability = None
        self.draw()
        self.screenshot(out / '01_mbti_selection.png')
        self.start()
        self.draw()
        self.screenshot(out / '02_dungeon.png')
        self.game.x, self.game.y = 6*48-14, 3.5*48
        self.game.update(0.03, 1, 0)
        self.draw()
        self.screenshot(out / '03_wall_collision.png')
        self.game.use(3)
        self.game.use(1)
        self.draw()
        self.screenshot(out / '04_abilities.png')
        frames = []
        from PIL import Image
        for i in range(36):
            self.game.update(1/12, 1 if i < 24 else -1, 0)
            self.draw()
            path = out / '_frame.png'
            self.screenshot(path)
            with Image.open(path) as frame:
                frames.append(frame.convert('RGB').resize((960, 600)))
        frames[0].save(ROOT / 'output/movement_collision.gif', save_all=True,
                       append_images=frames[1:], duration=83, loop=0)
        (out / '_frame.png').unlink()
        print('Captured logo, title, controls, 4 game screens and movement_collision.gif')


if __name__ == '__main__':
    main()
