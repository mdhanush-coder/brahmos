"""overlay_ch6: the opening is now the Blender anatomy plate (x-ray head, red/green/blue signal, pumping brain), not the SVG sketch.
build_pages: optional 4th argument = how long the plate lasts (ch6 uses it for 6.2 s of a 36.7 s chapter)."""
import re
s = open('overlay_ch6.html', encoding='utf-8').read()
s = s.replace('  <div id="brainHost"></div>\n', '')
s = s.replace('<!--BRAINKIT-->\n', '')
s = s.replace("  #lights { position:absolute; left:1000px; top:900px; display:flex; gap:34px; }", "  #lights { position:absolute; left:136px; top:880px; display:flex; gap:30px; }")
s = s.replace("  const B = BrainKit('#brainHost', { device: true });\n", '')
s = s.replace("  B.drawOn(tl, 0.0, 1.8);                                     // the brain sketches itself in\n", '')
s = s.replace("  B.flow(1.2, 5.8);                                           // red, green, blue pulses from the device up into the brain\n", '')
s = s.replace("  inn('#lights', 1.2);", "  inn('#lights', 0.9);                                        // the plate's four heartbeats at 0.9, 2.4, 3.9, 5.4 s: red, green, infrared, red")
s = s.replace("out(['#claim', '#two', '#brainHost', '#lights'], 6.2);", "out(['#claim', '#two', '#lights'], 6.2);\n  tl.to('#plate', { autoAlpha: 0, duration: 0.4, ease: 'power2.in' }, 5.85);   // the 3D plate leaves with the words")
a = s.index("  const upd = t => B.update(t);")
b = s.index("  window.__timelines")
s = s[:a] + s[b:]
open('overlay_ch6.html', 'w', encoding='utf-8').write(s)
assert 'BrainKit' not in s and 'B.' not in re.sub(r'[A-Za-z]B\.', '', s)

p = open('build_pages.py', encoding='utf-8').read()
if 'plate_dur' not in p:
    p = p.replace("plate = sys.argv[3] if len(sys.argv) > 3 else f'ch{ch}_alpha.webm'",
                  "plate = sys.argv[3] if len(sys.argv) > 3 else f'ch{ch}_alpha.webm'\nplate_dur = float(sys.argv[4]) if len(sys.argv) > 4 else dur     # how long the plate plays (ch6: 6.2 s of a longer chapter)")
    p = p.replace("f'data-duration=\"{dur}\"></video>')", "f'data-duration=\"{plate_dur}\"></video>')")
    open('build_pages.py', 'w', encoding='utf-8').write(p)
print('patched')
