"""Regression checks for the concrete week-two movement and loadout requirements."""
import itertools
import json
from collections import deque

from game_model import ABILITIES, MAP, PAIRS, ROOT, Game, loadout


def verify():
    results = []
    for letters in itertools.product(*PAIRS):
        mbti = ''.join(letters)
        assert [letter for letter, _ in loadout(mbti)] == list(mbti)
    results.append('16개 유형의 4개 능력 슬롯 대응 확인')
    for invalid in ('AAAA', 'INT', 'INTJJ', 'ESJT'):
        try:
            loadout(invalid)
        except ValueError:
            continue
        raise AssertionError(invalid)
    g = Game()
    g.x, g.y = 6*48-14, 3.5*48
    g.update(0.1, 1, 0)
    assert not g.blocked(g.x, g.y) and g.bump > 0
    assert g.sprite_index() == (3, 3)
    g.update(10, 1, 0)
    assert g.x < 6*48 and not g.blocked(g.x, g.y)
    # A blocked horizontal axis must still allow vertical wall sliding.
    old_y = g.y
    g.update(0.1, 1, 1)
    assert g.y > old_y
    straight, diagonal = Game(), Game()
    sx, sy = straight.x, straight.y
    straight.update(0.1, 1, 0)
    diagonal.update(0.1, 1, 1)
    assert abs((straight.x-sx)**2 - ((diagonal.x-sx)**2+(diagonal.y-sy)**2)) < 0.01
    results.append('벽 통과 방지, 큰 시간 간격, 충돌 프레임, 벽면 이동, 대각선 속도 확인')
    for letter, ability in ABILITIES.items():
        letters = list('ISTJ')
        index = next(i for i, pair in enumerate(PAIRS) if letter in pair)
        letters[index] = letter
        game = Game(''.join(letters))
        if letter in 'EFT':
            target = 'tablet' if letter == 'T' else 'npc'
            game.x, game.y = game.position(target)
        assert game.use(index), letter
        assert not game.use(index), letter
        assert game.active(letter), letter
        if letter == 'F':
            assert game.npc_hp == 75
        if letter == 'J':
            assert not game.trap_on
        if letter == 'P':
            assert game.speed == 240
        game.update(ability['cooldown']+0.1)
        assert not game.active(letter) and game.cooldowns[letter] == 0
        assert game.speed == game.base_speed
    g = Game('ESTJ')
    g.x, g.y = g.position('key')
    assert not g.use(0) and g.cooldowns['E'] == 0
    results.append('8개 능력의 발동, 쿨타임 재사용 제한, 효과 종료, 대상 거리 조건 확인')
    g = Game()
    g.x, g.y = g.position('exit')
    g.interact()
    assert not g.cleared
    g.x, g.y = g.position('key')
    g.interact()
    g.x, g.y = g.position('exit')
    g.interact()
    assert g.cleared
    reset = Game(g.mbti)
    assert not reset.has_key and not reset.cleared and all(v == 0 for v in reset.effects.values())
    start = tuple(int(v) for v in MAP['spawn'])
    visited, queue = {start}, deque([start])
    while queue:
        col, row = queue.popleft()
        for dc, dr in ((1,0),(-1,0),(0,1),(0,-1)):
            nxt = (col+dc, row+dr)
            x, y = nxt
            if 0 <= y < len(MAP['rows']) and 0 <= x < len(MAP['rows'][0]) and MAP['rows'][y][x] != '#' and nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
    assert all(tuple(int(v) for v in MAP[name]) in visited for name in ('key','exit','npc','tablet'))
    results.append('열쇠·출구 조건, 재선택 초기화, 맵의 주요 지점 연결 확인')
    report = {'scope': '2주차 프로토타입 규칙 및 연습 효과', 'passed': results,
              'pending': ['정식 함정 피해와 플레이어 체력', '문 퍼즐 해결', '16개 유형의 완성 던전 클리어 플레이', '밸런스 조정']}
    (ROOT / 'output/verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    for result in results:
        print('PASS', result)


if __name__ == '__main__':
    verify()
