# 게임 PNG 리소스

내장 ImageGen 도구로 생성한 픽셀 아트입니다. 주인공은 청록 후드와 남색 망토, 맵은 보라색 석재로 구성했습니다.

`dungeon_atlas.png`는 4×4 셀 아틀라스입니다. 첫 행은 바닥, 벽, 열쇠, 출구입니다. 나머지 행은 아래·위·오른쪽 방향의 대기, 걷기 2프레임, 충돌 프레임입니다. 왼쪽 방향은 게임에서 오른쪽 스프라이트를 반전해 표시합니다.

`sprites/`에는 재사용할 수 있도록 분리한 개별 PNG가 있습니다. 걷기는 초당 8프레임, 벽 충돌은 0.18초 동안 반응합니다. 안내자 NPC는 전용 이미지 `sprites/npc_guide.png`를 사용합니다.

## 던전 지형

`dungeon_terrain.png`는 내장 ImageGen 도구로 생성한 2×2 지형 아틀라스입니다. 첫 행은 어두운 청회색 판석 바닥 2종, 둘째 행은 밝은 회청색 벽 윗면과 수직 옆면입니다. 현재 게임은 이 아틀라스로 지형을 표시합니다. 통로 쪽 벽에는 수직면과 가장자리를 표시하고, 벽 아래의 바닥에는 그림자를 더합니다. 두 바닥 이미지는 맵 좌표에 따라 일정하게 섞어 표시합니다.

최종 생성 프롬프트는 다음과 같습니다.

> Use case stylized-concept. Production game TILE TEXTURE ATLAS, EXACT square canvas divided into a perfectly aligned 2 columns x 2 rows of four equal square texture cells, NO gutters, NO margins, NO labels, NO text, NO grid lines. Full opaque pixel-art tile textures edge to edge. For a top-down 2D ancient mystery dungeon. Top left cell: walkable FLOOR A, DARK desaturated blue-charcoal gray stone slabs seen straight down, broad flat worn flagstones with faint hairline cracks, subtle grout, quiet low contrast, NO plants, NO crystals, NO items. Top right cell: FLOOR B, identical palette and scale but slightly different cracks and stone joints, no major decoration. Bottom left cell: WALL TOP SURFACE, LIGHT desaturated cool gray-blue massive chiseled rectangular stone blocks seen straight down, visibly thicker and MUCH lighter than both floor cells, strong beveled stone rims, worn sculpted edges, restrained dusty lavender highlights, no moss. Bottom right cell: WALL FRONT FACE, vertical front elevation of substantial gray-blue masonry with horizontal block courses, dark deep mortar gaps, substantial carved stone, bright upper edge and darker lower edge, MUCH lighter than floor, matches bottom left stone material. Orthographic textures, NOT a perspective scene, no isometric angles. Cohesive premium crisp retro RPG pixel art, large readable pixel clusters. CRITICAL contrast: floor near-black charcoal/navy values, wall top medium-light cool stone gray values, wall front medium cool gray with deep dark grout. Avoid saturated purple that would blend the floor with walls. All four cells must tile naturally when repeated. Exact four equal quadrants. No outside frame.

## 안내자 NPC

`sprites/npc_guide.png`는 내장 ImageGen 도구로 생성한 투명 PNG입니다. 은발, 안경, 보라색 학자 로브와 크림색 어깨 망토를 입고 책과 랜턴을 든 던전 기록관으로 디자인했습니다. 게임에서는 원본 비율을 유지해 48×64 영역 안에 표시합니다.

최종 생성 프롬프트는 다음과 같습니다.

> Create a single production-ready NPC sprite for the top-down 2D pixel-art game MBTI DUNGEON. Full-body front-facing friendly mysterious elderly dungeon archivist, silver-white hair, short silver beard, tiny round gold spectacles, plum-purple long scholar robe with antique gold trim and a cream shoulder mantle, leather belt, brown boots. He carries one small closed leather spellbook with a golden clasp against his chest; a tiny brass lantern glows warm amber at his side. Distinctive unhooded head with white hair, compact readable silhouette, head about one third body height. Cute polished RPG pixel art, crisp pixel clusters and dark outline, limited purple/cream/gold palette to suit a purple stone dungeon and cyan portals. Slight overhead top-down RPG camera showing top of head and shoulders, eyes looking toward player below. ONE character only, neutral standing idle pose, fully visible head to feet. Character occupies 85 to 90 percent image height with small even transparent margins. Portrait 3:4 composition. Intended to be reduced to roughly 48x64 pixels, keep book, hair and robe simple and highly readable. Actual transparent alpha-zero background, NO background scene, NO floor, NO cast ground shadow, NO grid, NO text, NO labels, NO frame, NO extra characters, NO staff. PNG game asset.

## 생성 프롬프트

최초 생성에는 다음 조건을 사용했습니다.

> Production game sprite atlas, square, strictly 4 columns x 4 rows of equal cells. Cohesive crisp pixel art top-down mystical MBTI dungeon, midnight navy, purple stone, cyan magic and warm gold. First row floor tile, brick wall, golden key, cyan exit portal. Other rows identical teal-hooded adventurer facing down, up and right, with idle, two walk poses and collision recoil. No text or labels. Transparent sprite backgrounds.

투명도를 확인한 뒤 같은 이미지를 대상으로 다음 편집을 적용했습니다.

> Preserve the 4x4 layout and sprites. Remove white, gray, checkerboard backgrounds and grid lines from character, key and portal cells. Background alpha exactly zero. Keep sprite pixels opaque and the two stone tiles opaque. Retain positioning, scale and artwork.

게임은 아틀라스의 셀 경계를 약간 안쪽으로 잘라 샘플링합니다. 타일의 바깥 여백과 셀 경계선을 화면에 표시하지 않도록 적용했습니다.

## 타이틀 배경

`title_background.png`는 내장 ImageGen 도구로 생성했습니다. 실제 게임에서는 1280×800 화면 전체에 표시하며, 메뉴는 pico2d로 그립니다. 게임명은 아래의 전용 로고 PNG를 사용합니다.

타이틀 배경의 최종 생성 프롬프트는 다음과 같습니다.

> Use case stylized-concept. Asset type actual title screen background for a 1280x800 top-down pixel-art dungeon game MBTI DUNGEON. Wide 16:10 composition. High quality detailed hand-pixelled fantasy game key art, cohesive dark navy and purple ancient stone dungeon, cyan magical runes and gold torch embers. On the RIGHT HALF, a monumental arched dungeon entrance glows turquoise, stairs lead toward it, foreground small lone adventurer seen from behind in a teal hood and navy cloak with gold trim stands at lower right facing portal. Crumbling purple stone pillars frame scene, warm small torches at sides. LEFT HALF is VERY DARK shadowed stone, quiet low-contrast near-black navy negative space reserved for a large title and menu drawn by game code. Keep left 55 percent simple and dark with subtle stone detail, right portal exquisitely detailed. Atmospheric cinematic pixel art, crisp pixel clusters, no blur, no photorealism. NO text, NO lettering, NO UI, NO logos, NO watermark. Full bleed landscape 16:10.

## 미스터리 게임명 로고

`mbti_dungeon_wordmark.png`는 내장 ImageGen 도구로 제작한 투명 배경의 게임명 이미지입니다. 로고 화면, 타이틀 메뉴와 MBTI 선택 화면에서 비율을 유지해 표시합니다. 금속과 석재 질감의 고딕 글자에 청록색 균열, 연금술 문양과 보석 장식을 적용했습니다. 시작 로고에는 페이드와 느린 크기 변화를 적용합니다.

최종 생성 프롬프트는 다음과 같습니다.

> Create a polished custom dark fantasy mystery GAME TITLE WORDMARK as a reusable transparent PNG. Exact readable text in TWO centered lines: upper smaller line 'MBTI', lower dominant wider line 'DUNGEON'. Spell MBTI and DUNGEON exactly. No other words. Wide 2:1 image composition, wordmark fills central 90 percent width and 85 percent height with small transparent margins. Handcrafted mysterious angular gothic serif lettering, ancient silver stone and aged pale-gold metallic bevels, fine cracks with subtle turquoise magical light shining inside, deep purple dimensional shadows. Ornate but clearly legible. A thin broken alchemical halo behind MBTI, tiny compass diamond sigil at top center, delicate symmetrical etched rune ornaments around the sides, subtle turquoise edge glow. Under DUNGEON a narrow gold engraved ornamental line with a single turquoise gem. This is a premium indie dungeon puzzle adventure logo, ancient enigmatic atmosphere, fits a purple stone dungeon with cyan portals. No skulls, no weapons, no characters, no background scene. ACTUAL completely transparent alpha-zero background, no opaque black rectangle, no checkerboard, no white backdrop. Tight silhouette, restrained glow contained near letters, crisp contours usable at 400px width. Do not crop any letters or ornaments.

## 능력 선택 석판

`ability_tablet.png`는 내장 ImageGen 도구로 제작했습니다. 능력 선택 화면에서 각 지표의 버튼으로 사용하며 글자는 게임 코드에서 표시합니다. 선택한 석판에는 청록색 테두리의 밝기가 천천히 변하는 효과를 적용합니다.

최종 생성 프롬프트는 다음과 같습니다.

> Use case ui-mockup. Create a single reusable BLANK horizontal fantasy dungeon ability selection stone tablet PNG, aspect ratio 2:1, tightly framed centered with transparent background outside the silhouette. This is an actual game UI button frame to be displayed at 272x130 pixels. Ancient carved dark purple slate slab, thin weathered bronze and antique gold beveled border, delicate engraved alchemical ornament at four corners, tiny cyan rune diamond at exact top center. Interior MUST be very dark near-black navy, quiet, empty, flat low-contrast and spacious to hold live game text. Left interior will hold one large letter, right interior a Korean skill name, bottom interior one line of description, all added later by code. Keep ALL elaborate ornament strictly on outermost 8 percent rim. Subtle turquoise magic glow near frame, restrained purple highlights, premium pixel-art fantasy game UI matching purple dungeon and cyan portals. NO text, NO letters, NO numbers, NO symbols in the interior, NO skulls, NO icons inside, NO background scene, NO drop shadow far outside frame. True alpha zero outside the stone frame, clean edge, readable at small size.
