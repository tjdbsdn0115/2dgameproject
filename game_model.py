"""Rendering-independent rules for the week-two prototype. Coordinates are top-down."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ABILITIES = json.loads((ROOT / 'data/abilities.json').read_text(encoding='utf-8'))
MAP = json.loads((ROOT / 'data/dungeon.json').read_text(encoding='utf-8'))
PAIRS = ('EI', 'SN', 'TF', 'JP')


def loadout(mbti):
    if len(mbti) != 4 or any(letter not in pair for letter, pair in zip(mbti, PAIRS)):
        raise ValueError('MBTI must contain one letter from each of EI, SN, TF, JP')
    return [(letter, ABILITIES[letter]) for letter in mbti]


class Game:
    radius = 13
    base_speed = 150

    def __init__(self, mbti='INTJ'):
        self.mbti = mbti
        self.slots = loadout(mbti)
        self.tile = MAP['tile_size']
        self.x, self.y = self.position('spawn')
        self.cooldowns = {letter: 0.0 for letter in mbti}
        self.effects = {letter: 0.0 for letter in mbti}
        self.elapsed = 0.0
        self.bump = 0.0
        self.facing = 'down'
        self.walking = False
        self.npc_hp = 50
        self.has_key = False
        self.cleared = False
        self.message = 'WASD로 이동하고 1~4로 능력을 시험하세요.'

    def position(self, name):
        return tuple(value * self.tile for value in MAP[name])

    def near(self, name, distance=85):
        px, py = self.position(name)
        return math.hypot(self.x - px, self.y - py) <= distance

    def active(self, letter):
        return self.effects.get(letter, 0) > 0

    @property
    def speed(self):
        return self.base_speed * (ABILITIES['P']['speed_multiplier'] if self.active('P') else 1)

    @property
    def trap_on(self):
        return not self.active('J') and self.elapsed % 2.4 < 1.2

    def blocked(self, x, y):
        rows = MAP['rows']
        for cx in (x - self.radius, x + self.radius):
            for cy in (y - self.radius, y + self.radius):
                col, row = int(cx // self.tile), int(cy // self.tile)
                if row < 0 or row >= len(rows) or col < 0 or col >= len(rows[0]):
                    return True
                if rows[row][col] == '#':
                    return True
        return False

    def update(self, dt, dx=0, dy=0):
        if self.cleared:
            return
        self.elapsed += dt
        self.bump = max(0, self.bump - dt)
        for letter in self.mbti:
            self.cooldowns[letter] = max(0, self.cooldowns[letter] - dt)
            self.effects[letter] = max(0, self.effects[letter] - dt)
        length = math.hypot(dx, dy)
        self.walking = length > 0
        if not length:
            return
        if dx:
            self.facing = 'right' if dx > 0 else 'left'
        else:
            self.facing = 'down' if dy > 0 else 'up'
        # Substeps retain collision safety during frame stalls and speed boosts.
        distance = self.speed * dt
        steps = max(1, math.ceil(distance / 6))
        move_x, move_y = dx / length * distance / steps, dy / length * distance / steps
        for _ in range(steps):
            if self.blocked(self.x + move_x, self.y):
                self.collide()
            else:
                self.x += move_x
            if self.blocked(self.x, self.y + move_y):
                self.collide()
            else:
                self.y += move_y

    def collide(self):
        self.bump = 0.18
        self.message = '벽 충돌 · 이동 제한과 부딪힘 애니메이션'

    def use(self, slot):
        if self.cleared:
            return False
        letter, ability = self.slots[slot]
        if self.cooldowns[letter] > 0:
            self.message = f"{ability['name']} 재사용 대기 중"
            return False
        target = {'E': 'npc', 'F': 'npc', 'T': 'tablet'}.get(letter)
        if target and not self.near(target, ability['range']):
            self.message = '대상에게 가까이 이동하세요. 대기시간은 소모하지 않습니다.'
            return False
        if letter == 'F' and self.npc_hp >= 100:
            self.message = '안내자의 체력이 가득 찼습니다.'
            return False
        self.cooldowns[letter] = ability['cooldown']
        self.effects[letter] = ability['duration']
        self.message = f"{letter} {ability['name']} · {ability['description']}"
        if letter == 'E':
            self.message = '소통 · 안내자 추가 단서 “열쇠는 남동쪽 방에 있어요.”'
        if letter == 'T':
            self.message = '논리 · 석판 단서 “달, 별, 태양 순서를 기억하세요.”'
        if letter == 'F':
            self.npc_hp = min(100, self.npc_hp + ability['heal'])
        return True

    def interact(self):
        if self.cleared:
            return
        if self.near('key', 65) and not self.has_key:
            self.has_key = True
            self.message = '열쇠 획득 · 북동쪽 출구로 이동하세요.'
        elif self.near('exit', 65):
            if self.has_key:
                self.cleared = True
                self.message = '연습 맵 탐색 완료! R로 다시 선택합니다.'
            else:
                self.message = '출구를 열려면 열쇠가 필요합니다.'
        elif self.near('npc'):
            self.message = '안내자 “동쪽 길을 따라가면 열쇠가 있어요.”'
        elif self.near('tablet'):
            self.message = '연습 석판 · 달, 별, 태양. 정식 문 퍼즐은 4주차 개발 예정'

    def sprite_index(self):
        row = {'down': 1, 'up': 2, 'left': 3, 'right': 3}[self.facing]
        frame = 3 if self.bump else (1 + int(self.elapsed * 8) % 2 if self.walking else 0)
        return row, frame
