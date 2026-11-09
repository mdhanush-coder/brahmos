"""Text must never cover the 3D model (user rule, 2026-11-07).
For each overlay element: its screen box (px, from the page's CSS, widths estimated conservatively from the font size)
and its on-screen window (s). For each measured frame in that window, the device box (keepout_chN.json, from Blender)
grown by MARGIN must not intersect it. Prints every conflict with its worst overlap.
usage: python -I keepout_check.py <chapter>"""
import json, sys

MARGIN = 24
W, H = 1920, 1080
PLATE_SCALE, PLATE_DX = 0.78, 300          # bg_layer.html: #plate { transform: translateX(300px) scale(0.78) }
EL = {
    '1': [  # name, (x0, y0, x1, y1) px, t_in, t_out   (left column layout, video type sizes, widths estimated generously)
        ('note', (136, 96, 390, 134), 0.2, 24.15),
        ('price', (136, 190, 736, 430), 0.0, 7.7),          # #price is a fixed 600 px column
        ('where', (136, 770, 705, 930), 1.7, 8.0),
        ('date', (136, 190, 580, 320), 8.0, 14.6),
        ('crash', (136, 348, 610, 432), 12.05, 14.6),
        ('doctors', (136, 505, 560, 800), 14.8, 18.35),
        ('who', (136, 722, 560, 930), 18.5, 23.7),
    ],
    '2': [  # plays the ch1 plate again (keepout_ch2.json is a copy of keepout_ch1.json)
        ('note', (136, 96, 390, 134), 0.2, 24.15),
        ('name', (136, 190, 736, 370), 0.75, 6.3),
        ('maker', (136, 430, 736, 610), 3.0, 6.3),
        ('m1', (136, 190, 736, 380), 7.15, 16.6),
        ('m2', (136, 470, 736, 640), 9.75, 16.6),
        ('ceo', (136, 776, 620, 930), 13.75, 16.6),
        ('promise', (136, 190, 736, 520), 17.05, 24.15),
    ],
    '6': [  # only the first 6.2 s have the head plate; later pages are text + flat graphics on their own sides
        ('note', (136, 96, 390, 134), 0.2, 6.2),
        ('claim', (136, 190, 736, 480), 0.0, 6.2),
        ('two', (136, 520, 736, 680), 4.3, 6.2),
        ('lights', (136, 880, 620, 930), 0.9, 6.2),
    ],
    '4': [
        ('note', (136, 96, 390, 134), 0.2, 39.45),
        ('watch', (136, 774, 645, 930), 2.6, 8.5),
        ('ppg', (136, 190, 670, 400), 5.65, 8.5),
        ('partnames', (1580, 280, 1800, 695), 4.4, 9.9),   # right of the exploded stack; leaders touch the parts on purpose
        ('steps', (136, 190, 700, 585), 8.5, 20.35),
        ('wave', (136, 770, 696, 960), 16.2, 20.35),
        ('colours', (136, 190, 655, 615), 20.5, 29.2),
        ('algo', (136, 809, 520, 930), 29.4, 33.8),
        ('brainflow', (136, 190, 736, 525), 34.0, 39.45),
        ('entropy', (136, 590, 736, 865), 36.65, 39.45),
    ],
}


def placed(a, b, c, d):
    """Device box (normalised, plate space) -> page pixels after the plate's scale and move."""
    f = lambda v, n, dx: (v - 0.5) * PLATE_SCALE * n + n / 2 + dx
    return f(a, W, PLATE_DX), f(b, H, 0), f(c, W, PLATE_DX), f(d, H, 0)


def run(ch):
    k = json.load(open(f'keepout_ch{ch}.json'))
    fps = k['fps']
    boxes = {int(f): b for f, b in k['boxes'].items()}
    bad = 0
    for name, (x0, y0, x1, y1), t0, t1 in EL[ch]:
        worst, wf = 0, None
        for f, (a, b, c, d) in boxes.items():
            t = (f - 1) / fps
            if not (t0 <= t <= t1):
                continue
            px0, py0, px1, py1 = placed(a, b, c, d)
            dx0, dy0, dx1, dy1 = px0 - MARGIN, py0 - MARGIN, px1 + MARGIN, py1 + MARGIN
            ox, oy = min(x1, dx1) - max(x0, dx0), min(y1, dy1) - max(y0, dy0)
            if ox > 0 and oy > 0 and ox * oy > worst:
                worst, wf = ox * oy, (f, round(t, 2), [round(dx0), round(dy0), round(dx1), round(dy1)], round(ox), round(oy))
        if worst:
            bad += 1
            print(f'ch{ch} {name:10s} COVERS the model: frame {wf[0]} ({wf[1]} s) device+margin {wf[2]} overlap {wf[3]}x{wf[4]} px')
        else:
            print(f'ch{ch} {name:10s} clear')
    span = [min(b[0] for b in boxes.values()), min(b[1] for b in boxes.values()), max(b[2] for b in boxes.values()), max(b[3] for b in boxes.values())]
    print(f'ch{ch} device never leaves x {span[0]:.2f}-{span[2]:.2f}, y {span[1]:.2f}-{span[3]:.2f} of the frame;', 'ALL CLEAR' if not bad else f'{bad} to move')


for ch in sys.argv[1:] or ['1', '4']:
    run(ch)
