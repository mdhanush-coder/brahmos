"""ch7 and ch8 overlays: v2 word times -> master v3 (words_raghav_v3.json, chapter-relative)."""
def sub(path, pairs):
    s = open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert old in s, (path, old)
        s = s.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(s)

sub('overlay_ch7.html', [
 ('data-duration="46.06"', 'data-duration="42.24"'),
 ("inn('#r1', 2.15);", "inn('#r1', 2.15);"),
 ("inn('#d1', 3.85);", "inn('#d1', 3.55);"),
 ("inn('#d1w', 6.95);", "inn('#d1w', 6.55);"),
 ("out('#d1', 10.9);", "out('#d1', 10.2);"),
 ("done('#r1', 11.3); inn('#r2', 11.3);", "done('#r1', 10.6); inn('#r2', 10.6);"),
 ("inn('#d2', 11.95);", "inn('#d2', 11.0);"),
 ("inn('#d2l', 16.55);", "inn('#d2l', 15.75);"),
 ("out('#d2', 19.35);", "out('#d2', 18.4);"),
 ("done('#r3', 31.35)", "done('#r3', 29.45)") if False else ("done('#r2', 19.75); inn('#r3', 19.75);", "done('#r2', 18.6); inn('#r3', 18.6);"),
 ("tl.set('#d3', { autoAlpha: 1 }, 20.5);\n  inn('#d3 .lab', 20.5);", "tl.set('#d3', { autoAlpha: 1 }, 19.4);\n  inn('#d3 .lab', 19.4);"),
 ("inn('#c1', 21.55); inn('#c2', 22.15); inn('#c3', 23.7);", "inn('#c1', 20.2); inn('#c2', 20.75); inn('#c3', 22.1);"),
 ("inn('#d3l', 26.4);", "inn('#d3l', 24.35);"),
 ("out('#d3', 30.9);", "out('#d3', 28.95);"),
 ("done('#r3', 31.35); inn('#r4', 31.35);", "done('#r3', 29.45); inn('#r4', 29.45);"),
 ("tl.set('#d4', { autoAlpha: 1 }, 32.3);\n  inn('#d4 > .line', 32.3);", "tl.set('#d4', { autoAlpha: 1 }, 30.4);\n  inn('#d4 > .line', 30.4);"),
 ("inn('#q1', 35.15);", "inn('#q1', 32.75);"),
 ("inn('#q2', 39.85);", "inn('#q2', 36.7);"),
 ("out(['#d4', '#head', '#list'], 45.4);", "out(['#d4', '#head', '#list'], 41.7);"),
 ('ch7 starts at 200.10 s of the master', 'ch7 starts at 188.46 s of master v3'),
])
sub('overlay_ch8.html', [
 ('data-duration="20.73"', 'data-duration="19.68"'),
 ("inn('#theory', 0.0);", "inn('#theory', 0.0);"),
 ("inn('#diag', 2.35);", "inn('#diag', 1.9);"),
 ("inn('#c1', 5.85);", "inn('#c1', 6.3);"),
 ("inn('#grav', 6.65);", "inn('#grav', 7.3);"),
 ("inn('#c2', 8.1);", "inn('#c2', 8.35);"),
 ("tl.to('#flowLow', { strokeDashoffset: 0, duration: 0.5, ease: 'none' }, 8.1)\n    .to('#flowHigh', { strokeDashoffset: 0, duration: 0.5, ease: 'none' }, 8.6)\n    .to('#flowHigh', { opacity: 0.25, duration: 0.5, ease: 'power2.out' }, 9.05);",
  "tl.to('#flowLow', { strokeDashoffset: 0, duration: 0.5, ease: 'none' }, 8.35)\n    .to('#flowHigh', { strokeDashoffset: 0, duration: 0.5, ease: 'none' }, 8.85)\n    .to('#flowHigh', { opacity: 0.25, duration: 0.5, ease: 'power2.out' }, 9.15);"),
 ("inn('#c3', 10.3);", "inn('#c3', 10.35);"),
 ("out(['#theory', '#c1', '#c2', '#c3'], 12.3);", "out(['#theory', '#c1', '#c2', '#c3'], 12.0);"),
 ("tl.set('#docs', { autoAlpha: 1 }, 12.6);", "tl.set('#docs', { autoAlpha: 1 }, 12.3);"),
 ("{ autoAlpha: 1, y: 0, duration: 0.5, ease: 'power3.out' }, 12.6);   // \"डॉक्टरों ने\" (12.62)", "{ autoAlpha: 1, y: 0, duration: 0.5, ease: 'power3.out' }, 12.3);   // \"डॉक्टरों ने\" (12.31)"),
 ("duration: 0.18, ease: 'power4.in' }, 13.78)", "duration: 0.18, ease: 'power4.in' }, 13.2)"),
 ("}, 13.96);\n  inn('#reply', 15.2);", "}, 13.38);\n  inn('#reply', 14.7);"),
 ("out(['#docs', '#reply', '#diag'], 20.2);", "out(['#docs', '#reply', '#diag'], 19.2);"),
 ('ch8 starts at 246.16 s of the master', 'ch8 starts at 230.70 s of master v3'),
])
print('retimed 7 and 8')
