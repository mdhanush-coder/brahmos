"""Assemble a chapter's final Motion Graphic page: designed background + transparent 3D plate + the overlay's words.
Order inside #root: background, plate (video with alpha), then the overlay's own elements (they come after <!--PLATE-->).
usage: python -I build_pages.py <chapter> <duration_s> [plate_name|-]   ->  page_ch<N>.html
plate '-' builds without the video (for a design check before the plate exists)."""
import sys, re, pathlib

here = pathlib.Path(__file__).parent
ch, dur = sys.argv[1], float(sys.argv[2])
plate = sys.argv[3] if len(sys.argv) > 3 else f'ch{ch}_alpha.webm'
plate_dur = float(sys.argv[4]) if len(sys.argv) > 4 else dur     # how long the plate plays (ch6: 6.2 s of a longer chapter)
page = (here / f'overlay_ch{ch}.html').read_text(encoding='utf-8')
bg = (here / 'bg_layer.html').read_text(encoding='utf-8')
css = bg.split('<!-- BG-CSS -->')[1].split('<!-- BG-HTML -->')[0]
html = bg.split('<!-- BG-HTML -->')[1].split('<!-- BG-JS -->')[0]
js = bg.split('<!-- BG-JS -->')[1]
video = '' if plate == '-' else (f'<video id="plate" src="assets/{plate}" muted playsinline data-start="0" '
                                 f'data-duration="{plate_dur}"></video>')
assert '<!--PLATE-->' in page and '</head>' in page and 'window.__timelines' in page
page = page.replace('<!--BRAINKIT-->', (here / 'brain_kit.html').read_text(encoding='utf-8'), 1)   # the illustrated brain, if used
page = page.replace('</head>', css + '</head>', 1)
page = page.replace('<!--PLATE-->', html + video, 1)
# the background script runs first, then the overlay registers the background tweens on its own timeline
page = page.replace('<script>\n  // ', js + '<script>\n  // ', 1) if '<script>\n  // ' in page else page.replace('</body>', js + '</body>', 1)
page = re.sub(r'(\n\s*)window\.__timelines', rf'\1if (window.__bgTween) window.__bgTween(tl, {dur});\1window.__timelines', page, count=1)
out = here / f'page_ch{ch}.html'
out.write_text(page, encoding='utf-8')
print(out.name, len(page), 'plate:', plate)
