"""YouTube Short, 9:16 (1080x1920), ~89 s. v2 after the user's design note (2026-11-07): nothing pops up like subtitles; professional,
matching the series theme; the EngineX Charcoal Gold palette ONLY (charcoal #1C1C1C, cream #FFF8E6, gold #F5B700 + their opacities);
captions (if any) subtle, above the bottom zone YouTube covers with the title/description (bottom ~440 px), no movement, soft fades only.
Voice = short voice (raghav, sped 1.05x). Times below are from the ORIGINAL take (transcribe cce277b2) / SPEED."""
import json

SPEED = 1.05
S = lambda t: round(t / SPEED, 2)
DUR = 89.3
GOLD, CREAM = '#F5B700', '#FFF8E6'

CSS = '''
  :root { --dark:#1C1C1C; --gold:#F5B700; --cream:#FFF8E6; --edge:rgba(255,248,230,0.35); }
  body { margin:0; }
  #root { position:relative; width:1080px; height:1920px; overflow:hidden; background:var(--dark);
          font-family:'Space Grotesk','Hind',sans-serif; color:var(--cream); }
  #kit { position:absolute; left:20px; top:150px; width:1000px; height:940px; }
  #splate { position:absolute; left:-210px; top:150px; width:1500px; height:844px; object-fit:cover; }
  /* key graphics: one restrained element per scene, left-aligned above the captions (y 1090-1370) */
  .grp { position:absolute; left:80px; top:1090px; width:780px; height:280px; display:flex; flex-direction:column; justify-content:flex-end;
         align-items:flex-start; gap:10px; }
  .lab  { font:600 34px 'Space Grotesk','Hind',sans-serif; letter-spacing:0.2em; opacity:0.7; }
  .big  { font:700 170px/0.95 'Space Grotesk','Hind',sans-serif; letter-spacing:-0.02em; color:var(--gold); }
  .big2 { font:700 112px/1 'Space Grotesk','Hind',sans-serif; letter-spacing:-0.01em; color:var(--gold); }
  .dots { display:flex; gap:22px; }
  .dots i { width:64px; height:64px; border-radius:32px; border:3px solid var(--cream); display:inline-flex; align-items:center; justify-content:center;
            font:700 34px 'Space Grotesk','Hind',sans-serif; font-style:normal; opacity:0.35; }
  .stamp { display:inline-block; padding:8px 26px 12px; border:6px solid var(--gold); border-radius:14px; font:700 70px/1 'Space Grotesk','Hind',sans-serif;
           color:var(--gold); transform:rotate(-4deg); transform-origin:20% 50%; }
  /* captions: soft fade only, centred, ends at y 1480, clear of the bottom 440 px (title/description) and the right 150 px (buttons) */
  #cap { position:absolute; left:150px; width:780px; bottom:370px; height:150px; }
  .c { position:absolute; left:0; right:0; bottom:0; text-align:center; font:500 42px/1.3 'Space Grotesk','Hind',sans-serif; color:var(--cream);
       opacity:0; text-shadow:0 2px 14px rgba(0,0,0,0.75); }
'''

# key graphics: group = (out time, [(t, class, html)])
G = [
    (12.6, [(0.03, 'big', '₹85,000')]),
    (26.4, [(13.8, 'lab', 'BY DEEPINDER GOYAL'), (20.17, 'big2', '$25M'), (20.4, 'lab', 'OF HIS OWN MONEY')]),
    (38.3, [(26.85, 'lab', 'INSIDE: SHELL, BATTERY, BOARDS, SENSORS'), (36.4, 'lab', 'THE BRAIN FLOW SCORE')]),
    (49.2, [(40.4, 'lab', 'ONE ARTERY FEEDS THE SKIN, ANOTHER FEEDS THE BRAIN'), (47.9, 'big2', 'Whose blood?')]),
    (60.4, [(51.3, 'lab', 'THE COMPANY’S TWO STUDIES'), (52.8, 'big2', '≈ 0.8'), (55.7, 'big2', '59 / 60')]),
    (74.7, [(61.1, 'lab', 'THE DOCTORS’ FOUR OBJECTIONS'), (62.5, 'dots', '<i>1</i><i>2</i><i>3</i><i>4</i>')]),
    (83.1, [(75.4, 'lab', 'THE GRAVITY AGEING THEORY'), (81.8, 'stamp', 'PSEUDOSCIENCE')]),
    (93.0, [(88.2, 'big2', 'An experiment'), (91.2, 'lab', 'YOUR CALL — COMMENT BELOW')]),
]

# captions (script text, phrase level): (start, end) from the original take
CAPS = [
    (0.03, 3.45, 'Eighty-five thousand rupees, for a tiny gold device'), (3.7, 5.9, 'that you stick on your temple'),
    (6.4, 9.15, 'Pre-orders opened, and the website crashed'), (9.5, 12.3, 'Doctors called it an expensive toy'),
    (13.05, 18.3, 'It is Temple, built by Zomato’s founder, Deepinder Goyal'), (18.7, 21.8, 'who put in $25 million of his own money'),
    (22.2, 26.1, 'The promise: an estimate of the blood reaching your brain'), (26.8, 30.2, 'It sends green, red and infrared light into your skin'),
    (30.55, 34.8, 'Blood absorbs some of it, and the rest returns to a sensor'), (35.15, 37.95, 'and an algorithm turns that into a Brain Flow score'),
    (38.65, 43.2, 'But here is the catch: the artery under Temple feeds your skin'), (43.5, 46.3, 'while your brain gets blood by a different route'),
    (46.55, 48.6, 'So the real question: whose blood?'), (49.5, 54.1, 'Study one: 20 people, a match of about 0.8'),
    (54.35, 57.8, 'Study two: 59 of 60 sessions pointed the same way'), (58.0, 60.0, 'But both studies are still preprints'),
    (60.7, 65.3, 'Doctors: the anatomy, and a third of the signal unexplained'), (65.7, 69.8, 'Only young, healthy people, and no medical approval'),
    (70.1, 74.3, 'Goyal himself says: fitness and wellness, not medical'), (75.1, 80.6, 'The gravity theory: standing upright means less blood to the brain'),
    (80.9, 82.8, 'Doctors call it pseudoscience'), (83.45, 86.0, 'So for now, not a big discovery'),
    (86.3, 90.9, 'Not just a toy, but an experiment you can buy'), (91.35, 93.5, 'Your call: tell us in the comments'),
]

# the drawing in the palette: brain arteries cream, the scalp artery gold, light/pulses gold and cream
KIT = '''
  gsap.set('#kit', { opacity: 0 });
  tl.to('#splate', { opacity: 0, duration: 0.5 }, %(p1)s);                                         // the 3D model hands over to the drawing
  tl.to('#kit', { opacity: 1, duration: 0.6 }, %(p1)s);
  B.vessels.forEach(v => gsap.set(v, { attr: { stroke: '%(cream)s' }, opacity: 0.8 }));
  gsap.set(B.scalp, { attr: { stroke: '%(gold)s' }, opacity: 0 });
  B.drawOn(tl, %(p1)s, 1.6);
  B.flow(%(p1)s + 1.0, %(a2)s, { period: 1.1, colors: ['%(gold)s', '%(cream)s'], beam: true });
  tl.to(B.scalp, { opacity: 1, duration: 0.6 }, %(c1)s);                                           // the scalp artery under the device
  B.flowScalp(%(c1)s, %(c2)s, { period: 0.9, colors: ['%(gold)s'] });
  B.flow(%(d1)s, %(d2)s, { period: 1.0, colors: ['%(cream)s'] });                                  // the brain's own arteries
  tl.to(B.scalp, { opacity: 0, duration: 0.5 }, %(e1)s);
  tl.to('#kit', { opacity: 0.5, duration: 0.6 }, %(e1)s);                                          // evidence and doctors: the picture steps back
  tl.to('#kit', { opacity: 1, duration: 0.6 }, %(f1)s);
  B.flow(%(f1)s, %(f2)s, { period: 1.1, colors: ['%(gold)s', '%(cream)s'], beam: true });         // verdict: the light again
''' % dict(cream=CREAM, gold=GOLD, p1=S(37.4), a2=S(40.3), c1=S(40.4), c2=S(43.4), d1=S(43.8), d2=S(48.4), e1=S(49.4), f1=S(75.0), f2=S(92.5))

groups, js = [], []
for gi, (out_t, items) in enumerate(G):
    gid = f'g{gi}'
    groups.append(f'  <div class="grp" id="{gid}">' + ''.join(f'<div class="{c}" id="{gid}_{i}">{h}</div>' for i, (_, c, h) in enumerate(items)) + '</div>')
    js.append(f"  gsap.set('#{gid} > div', {{ autoAlpha: 0 }});")
    for i, (tt, c, h) in enumerate(items):
        if c == 'stamp':
            js.append(f"  tl.fromTo('#{gid}_{i}', {{ autoAlpha: 0, scale: 1.35, rotation: -1 }}, {{ autoAlpha: 1, scale: 1, rotation: -4, duration: 0.2, ease: 'power4.in' }}, {S(tt)});")
        else:
            js.append(f"  fade('#{gid}_{i}', {S(tt)});")
        if c == 'dots':   # the four dots light up as each objection is spoken
            for k, tk in enumerate((62.55, 63.75, 65.99, 68.7)):
                js.append(f"  tl.to('#{gid}_{i} i:nth-child({k + 1})', {{ opacity: 1, backgroundColor: '{GOLD}', color: '#1C1C1C', borderColor: '{GOLD}', duration: 0.4 }}, {S(tk)});")
    js.append(f"  gone('#{gid} > div', {S(out_t)});")
caps_html = ''.join(f'<div class="c" id="c{i}">{t}</div>' for i, (_, _, t) in enumerate(CAPS))
for i, (a, b, _) in enumerate(CAPS):
    js.append(f"  tl.to('#c{i}', {{ opacity: 0.88, duration: 0.3, ease: 'sine.out' }}, {S(a)}).to('#c{i}', {{ opacity: 0, duration: 0.3, ease: 'sine.in' }}, {S(b) - 0.05});")

page = f'''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="short" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
  <!--PLATE-->
  <video id="splate" src="assets/render.webm" muted playsinline data-start="0" data-duration="{S(37.4) + 0.6}"></video>
  <div id="kit"></div>
{chr(10).join(groups)}
  <div id="cap">{caps_html}</div>
</div>
<!--BRAINKIT-->
<script>
  // GENERATED by make_short.py v2. Times = original take / {SPEED}. Key graphics rise 24 px once (0.5 s); captions only fade (no movement).
  const tl = gsap.timeline({{ paused: true }});
  const fade = (sel, t) => tl.fromTo(sel, {{ autoAlpha: 0, y: 24 }}, {{ autoAlpha: 1, y: 0, duration: 0.5, ease: 'power3.out' }}, t);
  const gone = (sel, t) => tl.to(sel, {{ autoAlpha: 0, duration: 0.4, ease: 'power2.in' }}, t);
  const B = BrainKit('#kit', {{ device: true }});
{KIT}
{chr(10).join(js)}
  const upd = t => B.update(t);
  window.addEventListener('hf-seek', e => upd(e.detail.time));
  tl.eventCallback('onUpdate', () => upd(tl.time()));
  upd(0);
  window.__timelines = {{ short: tl }};
</script>
</body>
</html>
'''
open('overlay_chshort.html', 'w', encoding='utf-8').write(page)
print('overlay_chshort.html', len(page), 'captions', len(CAPS))
