import zlib, struct

PAL = {
    'h': '#2b1d16',  # loc dark
    'H': '#463122',  # loc highlight (separates individual dreads)
    's': '#b07a52',  # skin
    'S': '#96603c',  # skin shadow (used sparingly: young face = little shadow)
    'e': '#141014',  # eye
    'j': '#2a3556',  # navy jacket
    'w': '#e8e4d8',  # shirt
    't': '#d4592e',  # rust tie
    'b': '#1a1f33',  # trousers
}

W24 = 24
# Two distinct locs per side, separated by a real gap so they read as strands
# rather than a solid curtain. Highlight column gives each loc a rounded edge.
LOCL = 'hH.hH'
LOCR = 'Hh.Hh'


def center(s, width=W24):
    pad = width - len(s)
    l = pad // 2
    return '.' * l + s + '.' * (pad - l)


def fr(face12, locl, locr):
    """A face row: 1 pad + 5 locs + 12 face + 5 locs + 1 pad = 24."""
    assert len(face12) == 12 and len(locl) == 5 and len(locr) == 5, face12
    row = '.' + locl + face12 + locr + '.'
    assert len(row) == W24, (len(row), row)
    return row


# Cropped hair with faded sides (the original shape), the younger face, and a tee.
def cf(face12):
    """Centred face row: 6 pad + 12 face + 6 pad = 24."""
    assert len(face12) == 12, face12
    row = '......' + face12 + '......'
    assert len(row) == W24, (len(row), row)
    return row


PORTRAIT = [
    center(''),
    center('hhhhhhhh'),
    center('hhHhhhhHhhhh'),
    center('hhHhhhHhhhhHhh'),
    center('hhhhhhhhhhhhhh'),
    center('hhhhhhhhhhhhhh'),
    '.....' + 'hh' + 'ssssssssss' + 'hh' + '.....',   # hairline, faded temples
    '.....' + 'h' + 'ssssssssssss' + 'h' + '.....',
    cf('ssssssssssss'),   # forehead
    cf('sshhhsshhhss'),   # eyebrows
    cf('ssssssssssss'),
    cf('sseesssseess'),   # eyes, 2x2 (large eyes read young)
    cf('sseesssseess'),
    cf('ssssssssssss'),
    cf('sssssSSsssss'),   # nose, 2px only
    cf('sssshhhhssss'),   # mustache, thin
    cf('sssssSSsssss'),   # mouth, subtle
    cf('ssssssssssss'),   # chin
    cf('.ssssssssss.'),   # jaw taper
    cf('...ssssss...'),   # neck
    '....' + 'tttttt' + 'ssss' + 'tttttt' + '....',   # tee, crew neck
    '...' + 's' + 'tttttttttttttttt' + 's' + '...',   # bare arms
    '...' + 's' + 'tttttttttttttttt' + 's' + '...',
    center(''),
]

# 16x16 in-game sprite, same silhouette compressed.
W16 = 16


def hr(face8, locl='hH', locr='Hh'):
    """Head row: 2 pad + 2 loc + 8 face + 2 loc + 2 pad = 16."""
    row = '..' + locl + face8 + locr + '..'
    assert len(row) == W16, (len(row), row)
    return row


def br(body10, edge=('.', '.')):
    """Body row: 2 pad + 1 edge + 10 body + 1 edge + 2 pad = 16."""
    row = '..' + edge[0] + body10 + edge[1] + '..'
    assert len(row) == W16, (len(row), row)
    return row


def f8(face8):
    """Face row with faded-hair temples: 3 pad + h + 8 face + h + 3 pad = 16."""
    row = '...h' + face8 + 'h...'
    assert len(row) == W16, (len(row), row)
    return row


def c8(mid, width=W16):
    return center(mid, width)


_CROWN = ['................', '....hhhhhhhh....',
          '...hHhhhHhhHh...', '...hhhhhhhhhh...']
_TEE = ['...tttttttttt...',      # shoulders
        '..stttttttttts..',      # bare arms
        '..stttttttttts..',
        '...tttttttttt...',
        '...bbbbbbbbbb...']      # trousers
_LEGS = '....bbb..bbb....'
_LEGS_WALK = '...bbb....bbb...'

FRONT = _CROWN + [
    f8('ssssssss'),      # forehead, temples faded
    c8('seessees'),      # eyes, 2px wide
    c8('ssssssss'),
    c8('ssshhsss'),      # mustache, 2px
    c8('..ssss..'),      # chin into neck
] + _TEE + [_LEGS, '................']
FRONT_WALK = FRONT[:14] + [_LEGS_WALK, '................']

BACK = _CROWN + [
    f8('hhhhhhhh'),
    c8('hhhhhhhh'),
    c8('hhhhhhhh'),
    c8('.hhhhhh.'),
    c8('..ssss..'),      # nape
] + _TEE + [_LEGS, '................']
BACK_WALK = BACK[:14] + [_LEGS_WALK, '................']

# Side view: profile, one eye, hair cropped close at the back.
SIDE = ['................', '....hhhhhhh.....',
        '...hHhhhHhh.....', '...hhhhhhhh.....'] + [
    '...h' + 'sssssss' + '.....',
    '...h' + 'sseesss' + '.....',
    '...h' + 'sssssss' + '.....',
    '...h' + 'sshhsss' + '.....',
    '....' + '.ssss..' + '.....',
    '...' + 'ttttttt' + '......',
    '..s' + 'ttttttt' + 't.....',
    '..s' + 'ttttttt' + 't.....',
    '...' + 'ttttttt' + '......',
    '...' + 'bbbbbbb' + '......',
    '....bb.bb.......', '................',
]
SIDE_WALK = SIDE[:14] + ['....bb...bb.....', '................']


def hex_rgb(h):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


def render(rows, scale, bg=None, pad=0):
    h = len(rows) + pad * 2
    w = len(rows[0]) + pad * 2
    W, H = w * scale, h * scale
    out = bytearray()
    for y in range(H):
        out.append(0)
        sy = y // scale - pad
        for x in range(W):
            sx = x // scale - pad
            ch = '.'
            if 0 <= sy < len(rows) and 0 <= sx < len(rows[0]):
                ch = rows[sy][sx]
            if ch != '.' and ch in PAL:
                r, g, b = hex_rgb(PAL[ch])
                out += bytes((r, g, b, 255))
            elif bg is not None:
                r, g, b = hex_rgb(bg)
                out += bytes((r, g, b, 255))
            else:
                out += bytes((0, 0, 0, 0))
    return W, H, bytes(out)


def write_png(path, W, H, raw):
    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9))
    png += chunk(b'IEND', b'')
    open(path, 'wb').write(png)


def js_rows(rows, per_line=3):
    out = []
    for i in range(0, len(rows), per_line):
        out.append(','.join('"%s"' % r for r in rows[i:i + per_line]))
    return ',\n'.join(out)


if __name__ == '__main__':
    for name, rows in [('PORTRAIT', PORTRAIT), ('FRONT', FRONT), ('BACK', BACK), ('SIDE', SIDE)]:
        w = len(rows[0])
        bad = [(i, len(r)) for i, r in enumerate(rows) if len(r) != w]
        print('%-9s %dx%d  bad=%s' % (name, w, len(rows), bad))

    base = '/private/tmp/claude-501/-Users-lewisdyson-Claude/146667f4-9ecc-4618-8257-b5b6db946ca4/scratchpad/'
    W, H, raw = render(PORTRAIT, 24, bg=None, pad=1)
    write_png(base + 'lewis-8bit-face.png', W, H, raw)
    W, H, raw = render(PORTRAIT, 24, bg='#0b0b16', pad=1)
    write_png(base + 'lewis-8bit-face-dark.png', W, H, raw)
    W, H, raw = render(FRONT, 32, bg=None, pad=1)
    write_png(base + 'lewis-8bit-sprite.png', W, H, raw)

    # contact sheet of every in-game view, on grass, for visual checking
    sheet = []
    for y in range(16):
        sheet.append(FRONT[y] + '..' + BACK[y] + '..' + SIDE[y] + '..' +
                     SIDE[y][::-1] + '..' + FRONT_WALK[y])
    W, H, raw = render(sheet, 20, bg='#7da453', pad=1)
    write_png(base + 'sprite-sheet.png', W, H, raw)
    print('pngs written')
