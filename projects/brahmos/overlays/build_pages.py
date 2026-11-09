"""Assemble a chapter's Motion Graphic page: [designed background] + plate video + the overlay's words.
usage: python -I build_pages.py <chapter> <plate_name|-> [bg|nobg]  ->  page_ch<N>.html
bg   = transparent plate over bg_layer.html (studio chapters); nobg = opaque plate fills the frame (sea, dusk chapters).
plate '-' builds without the video (design and motion checks before the plate exists)."""
import sys, re, pathlib
here = pathlib.Path(__file__).parent
ch, plate = sys.argv[1], sys.argv[2]
use_bg = (sys.argv[3] if len(sys.argv) > 3 else 'bg') == 'bg'
page = (here / f'overlay_ch{ch}.html').read_text(encoding='utf-8')
dur = float(re.search(r'data-duration="([\d.]+)"', page).group(1))
assert '<!--PLATE-->' in page and 'window.__timelines' in page
video = '' if plate == '-' else f'<video id="plate" src="assets/{plate}" muted playsinline data-start="0" data-duration="{dur}"></video>'
if use_bg:
    bg = (here / 'bg_layer.html').read_text(encoding='utf-8')
    css = bg.split('<!-- BG-CSS -->')[1].split('<!-- BG-HTML -->')[0]
    html = bg.split('<!-- BG-HTML -->')[1].split('<!-- BG-JS -->')[0]
    js = bg.split('<!-- BG-JS -->')[1]
    page = page.replace('</head>', css + '</head>', 1).replace('<!--PLATE-->', html + video, 1)
    page = page.replace('<script>\n  // ', js + '<script>\n  // ', 1)
    page = re.sub(r'(\n\s*)window\.__timelines', rf'\1if (window.__bgTween) window.__bgTween(tl, {dur});\1window.__timelines', page, count=1)
else:
    page = page.replace('<!--PLATE-->', video, 1)
out = here / f'page_ch{ch}.html'
out.write_text(page, encoding='utf-8')
print(out.name, len(page), 'plate:', plate, 'bg:', use_bg, 'dur:', dur)
