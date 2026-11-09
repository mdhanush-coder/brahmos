"""brain_kit.html (device mode): the Temple sits ON the skin of a head outline and its light enters the skull and the brain
(user, 2026-11-07: the signal looked like it passed behind / outside the brain). Also: ch9 flows use the beam."""
import ast
s = open('brain_kit.html', encoding='utf-8').read()


def rep(old, new):
    global s
    assert old in s, old[:70]
    s = s.replace(old, new, 1)


rep("d: 'M105,500 C125,430 140,370 150,300 C158,240 165,180 185,110'", "d: 'M52,430 C30,370 22,300 26,240 C30,180 52,112 112,62'")
a = s.index("  // ---- Temple device (optional)")
b = s.index("  // ---- signal pulses")
s = s[:a] + '''  // ---- Temple device (optional): a head outline around the brain, the gold device ON the skin at the temple, and its light
  //      entering the skull as a coloured beam that ends inside the brain ----
  let dev = null, beam = null, beamPath = null, headEl = null, bst = [];
  if (o.device) {
    headEl = el('path', { d: 'M42,255 C14,170 70,60 185,30 C262,6 345,2 415,20 C520,42 592,105 606,198 C618,265 600,320 566,345 C548,372 505,392 492,420 L488,600 M42,255 C44,282 46,296 40,318 C24,330 6,346 4,356 C16,364 30,370 38,372 C28,384 26,394 32,402 C24,412 28,432 48,442 C70,462 110,476 170,484 C230,490 262,494 268,520 L268,600',
      fill: 'none', stroke: CREAM, 'stroke-width': 3.5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', opacity: 0.9 });
    svg.insertBefore(headEl, brain);
    ink.push(headEl);
    const grad = el('linearGradient', { id: 'bkBeam', x1: 0, y1: 0, x2: 1, y2: 0 }, defs);
    bst = [el('stop', { offset: 0, 'stop-color': '#F0412E', 'stop-opacity': 0.95 }, grad), el('stop', { offset: 1, 'stop-color': '#F0412E', 'stop-opacity': 0.06 }, grad)];
    beamPath = el('path', { d: 'M46,236 C120,232 200,236 272,248', fill: 'none', stroke: 'none' });
    beam = el('path', { d: 'M46,226 L300,150 L300,350 L46,246 Z', fill: 'url(#bkBeam)', opacity: 0 });
    dev = el('ellipse', { cx: 31, cy: 236, rx: 15, ry: 34, fill: '#F5B700', stroke: '#FFE29A', 'stroke-width': 2 });
  }
  const LB = beamPath ? beamPath.getTotalLength() : 1;
''' + s[b:]
rep("    svg, brain, heart, dev, ink, vessels, scalp,", "    svg, brain, heart, dev, ink, vessels, scalp, beam, headEl,")
rep("      let used = 0, flash = 0, flashCol = null, beat = 0;\n      rings.forEach(r => r.setAttribute('opacity', 0));",
    "      let used = 0, flash = 0, flashCol = null, beat = 0, bflash = 0, bcol = null;")
rep("          beat = Math.max(beat, Math.exp(-age / 0.18));", "          beat = Math.max(beat, Math.exp(-age / 0.18));\n          if (f.beam && beam && !f.scalp) { const bf = Math.exp(-age / 0.5); if (bf > bflash) { bflash = bf; bcol = f.colors[k % f.colors.length]; } }")
rep("const uu = Math.max(0, u - j * 0.035), p = vessels[vi].getPointAtLength(uu * L[vi]);",
    "const uu = Math.max(0, u - j * 0.035), bm = f.beam && vi === 0, p = (bm ? beamPath : vessels[vi]).getPointAtLength(uu * (bm ? LB : L[vi]));")
a = s.index("          if (dev && age < 1.2)"); b = s.index("        }\n      }\n      for (let i = used;")
s = s[:a] + s[b:]
rep("      glow.setAttribute('opacity', 0.10 + 0.30 * flash);",
    "      if (beam) { beam.setAttribute('opacity', 0.75 * bflash); if (bcol) bst.forEach(st => st.setAttribute('stop-color', bcol)); }\n      glow.setAttribute('opacity', 0.10 + 0.30 * flash);")
assert 'rings' not in s
open('brain_kit.html', 'w', encoding='utf-8').write(s)

m = open('make_story.py', encoding='utf-8').read()
old = "B.flow(4.5, 19.5, { period: 1.0, colors: ['#F0412E', '#2BD45A', '#3A7BFF'] });"
assert old in m
m = m.replace(old, "B.flow(4.5, 19.5, { period: 1.0, colors: ['#F0412E', '#2BD45A', '#3A7BFF'], beam: true });   // Temple's light enters the head and reaches the brain")
open('make_story.py', 'w', encoding='utf-8').write(m)
print('patched')
