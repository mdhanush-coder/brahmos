"""ch8: replace the plain ellipse/heart diagram with the illustrated brain + heart (BrainKit), the same drawing the other chapters use.
Story: blood climbs from the heart to the brain (red pulses); gravity pulls down (arrow); then LESS of each pulse reaches the brain."""
import re
s = open('overlay_ch8.html', encoding='utf-8').read()

# HTML: drop the SVG diagram, add the kit host and a gravity arrow
a = s.index('  <svg id="diag"'); b = s.index('</svg>', a) + len('</svg>')
s = s[:a] + '''  <div id="kit"></div>
  <svg id="grav" viewBox="0 0 120 520"><path d="M60 20 L60 440 M32 400 L60 452 L88 400" fill="none" stroke="#FFF8E6" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="60" y="500" text-anchor="middle">GRAVITY</text></svg>''' + s[b:]
s = s.replace('</div>\n<script>', '</div>\n<!--BRAINKIT-->\n<script>', 1)

# CSS: place them (words stay in the left column; the brain + heart on the right, gravity arrow beside)
a = s.index('  #diag {'); b = s.index('</style>')
s = s[:a] + '''  #kit { position:absolute; left:1000px; top:80px; width:620px; height:950px; }
  #grav { position:absolute; left:1690px; top:300px; width:120px; height:520px; }
  #grav text { fill:#FFF8E6; font:600 30px 'Space Grotesk','Hind',sans-serif; letter-spacing:0.18em; opacity:0.7; }
''' + s[b:]

# JS timeline
a = s.index("  gsap.set(['#theory'"); b = s.index("  inn('#c3'")
s = s[:a] + '''  gsap.set(['#theory', '#c1', '#c2', '#c3', '#docs', '#reply', '#grav'], { autoAlpha: 0 });
  const inn = (sel, t) => tl.fromTo(sel, { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: 'power3.out' }, t);
  const out = (sel, t) => tl.to(sel, { autoAlpha: 0, duration: 0.4, ease: 'power2.in' }, t);
  const B = BrainKit('#kit', { heart: true });
  inn('#theory', 0.0);                                  // "इसके पीछे एक थ्योरी" ... "ग्रैविटी एजिंग हाइपोथिसिस" (0.02-3.8)
  B.drawOn(tl, 1.9, 1.8);                               // the brain and its vessels sketch themselves in
  B.flow(3.0, 8.3, { period: 0.9, colors: ['#F0412E'] });                 // the heart sends blood up to the brain: full strength
  inn('#c1', 6.3);                                      // "ज़िंदगी भर सीधे खड़े रहने से" (6.44)
  inn('#grav', 7.3);                                    // "सीधे खड़े" (7.33): gravity pulls down
  inn('#c2', 8.35);                                     // "दिमाग़ तक ख़ून कम पहुँचता है" (8.41-9.69)
  B.flow(8.9, 12.0, { period: 0.9, colors: ['#F0412E'], reach: () => 0.3 });   // "कम पहुँचता": only a third of each pulse now gets there
''' + s[b:]
s = s.replace("  out(['#docs', '#reply', '#diag'], 19.2);\n", "  out(['#docs', '#reply', '#kit', '#grav'], 19.2);\n  out('#grav', 12.0);\n  const upd = t => B.update(t);\n  window.addEventListener('hf-seek', e => upd(e.detail.time));\n  tl.eventCallback('onUpdate', () => upd(tl.time()));\n  upd(0);\n")
s = s.replace("  // fades on \"कम पहुँचता\" (opacity only), which is the claim itself.", "  // thins out on \"कम पहुँचता\": each pulse now reaches only a third of the way over the brain (the claim itself).")
open('overlay_ch8.html', 'w', encoding='utf-8').write(s)
assert 'diag' not in s and 'flowLow' not in s and "BrainKit('#kit'" in s
print('ok')
