"""Short v3 (user, 2026-11-07): show the 3D model and its exploded view (the ch4 Blender plate), ENGLISH text only (no Hindi captions)."""
import ast
s = open('make_short.py', encoding='utf-8').read()


def rep(old, new):
    global s
    assert old in s, old[:60]
    s = s.replace(old, new, 1)


rep("  #kit { position:absolute; left:20px; top:150px; width:1000px; height:940px; }",
    "  #kit { position:absolute; left:20px; top:150px; width:1000px; height:940px; }\n"
    "  #splate { position:absolute; left:-210px; top:150px; width:1500px; height:844px; object-fit:cover; }")
rep("font:500 44px/1.3 'Hind','Space Grotesk',sans-serif; color:var(--cream);", "font:500 42px/1.3 'Space Grotesk','Hind',sans-serif; color:var(--cream);")
rep("(38.3, [(36.4, 'lab', 'THE BRAIN FLOW SCORE')]),", "(38.3, [(26.85, 'lab', 'INSIDE: SHELL, BATTERY, BOARDS, SENSORS'), (36.4, 'lab', 'THE BRAIN FLOW SCORE')]),")
a = s.index("CAPS = ["); b = s.index("# the drawing in the palette")
EN = '''CAPS = [
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

'''
s = s[:a] + EN + s[b:]
a = s.index("KIT = '''"); b = s.index("groups, js = [], []")
KIT = """KIT = '''
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

"""
s = s[:a] + KIT + s[b:]
rep("  <!--PLATE-->\n  <div id=\"kit\"></div>", "  <!--PLATE-->\n  <video id=\"splate\" src=\"assets/render.webm\" muted playsinline data-start=\"0\" data-duration=\"{S(37.4) + 0.6}\"></video>\n  <div id=\"kit\"></div>")
ast.parse(s)
open('make_short.py', 'w', encoding='utf-8').write(s)
print('patched')
