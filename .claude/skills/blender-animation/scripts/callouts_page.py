#!/usr/bin/env python3
"""tracks.json (per-frame screen position of every part, from the Blender job) -> Motion Graphic HTML overlay.

Why not 3D text in Blender: labels become crisp 2D type that tracks the parts exactly, can be restyled without
re-rendering the 3D plate, and layout is checked numerically (overlap report below) instead of by eye.

  python callouts_page.py tracks.json overlay.html --title "2207 BRUSHLESS MOTOR" --subtitle "EXPLODED VIEW" \
         [--plate assets/plate.mp4] [--duration 10]
Then: motion-graphic/render {html: <file text>, media: [<plate key>], format: 'mp4'} (the plate is assets/<basename>).
Page rules honoured: GSAP paused timeline registered + drawing from the hf-seek time, no clocks/rAF.
"""
import argparse, json, sys

W, H = 1920, 1080
ROWS = [0.20, 0.80, 0.31, 0.69]    # label row centres (share of frame height); row = x-order rank % 4
PILL_W, PILL_H = 320, 82
LEAD_IN, LEAD_OUT = 12, 4           # label appears LEAD_IN frames before the part arrives, leaves LEAD_OUT before it returns
ACCENT = '#ff7a1a'


def layout(tp, f):
    k = min(max(f - 1, 0), len(tp['pts']) - 1)
    a, u = int(k), k - int(k)
    b = min(a + 1, len(tp['pts']) - 1)
    ax = (tp['pts'][a][0] * (1 - u) + tp['pts'][b][0] * u) * W
    ay = (tp['pts'][a][1] * (1 - u) + tp['pts'][b][1] * u) * H
    lx = min(max(ax, PILL_W / 2 + 40), W - PILL_W / 2 - 40)
    return ax, ay, lx, ROWS[tp['row']] * H


def overlap_report(tracks):
    """Simulate the layout on every frame; return frames where two visible pills overlap or a pill leaves safe area."""
    bad = []
    for f in range(1, tracks['frames'] + 1):
        rects = []
        for tp in tracks['parts']:
            if tp['out'] - LEAD_IN <= f <= tp['back'] - LEAD_OUT:
                _, _, lx, ly = layout(tp, f)
                rects.append((tp['id'], lx - PILL_W / 2, ly - PILL_H / 2, lx + PILL_W / 2, ly + PILL_H / 2))
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b = rects[i], rects[j]
                if a[1] < b[3] + 12 and b[1] < a[3] + 12 and a[2] < b[4] and b[2] < a[4]:
                    bad.append((f, a[0], b[0]))
    return bad


PAGE = r'''<!doctype html><html><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
body{margin:0;background:#000}
#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:#000;font-family:"Helvetica Neue","Inter",Arial,sans-serif;color:#fff}
#plate{position:absolute;left:0;top:0;width:1920px;height:1080px;object-fit:cover}
#shade{position:absolute;left:0;top:0;width:1920px;height:1080px;background:radial-gradient(ellipse at 50% 50%,rgba(0,0,0,0) 52%,rgba(0,0,0,.55) 100%),linear-gradient(to top,rgba(0,0,0,.4),rgba(0,0,0,0) 24%)}
#lines{position:absolute;left:0;top:0;width:1920px;height:1080px}
.callout{position:absolute;left:0;top:0;width:__PW__px;height:__PH__px;box-sizing:border-box;border-radius:12px;background:rgba(10,12,16,.78);
  border:1px solid rgba(255,255,255,.2);display:flex;align-items:center;gap:14px;padding:0 18px;opacity:0;transform-origin:50% 50%}
.callout .n{flex:none;width:34px;height:34px;border-radius:9px;background:__ACC__;color:#111;font-weight:700;font-size:17px;display:flex;align-items:center;justify-content:center;letter-spacing:.02em}
.callout b{display:block;font-size:24px;font-weight:700;letter-spacing:.09em;white-space:nowrap}
.callout i{display:block;font-style:normal;font-size:17px;font-weight:400;color:rgba(255,255,255,.64);margin-top:5px;letter-spacing:.04em;white-space:nowrap}
#title{position:absolute;left:72px;top:60px;opacity:0}
#title h1{margin:0;font-size:44px;font-weight:700;letter-spacing:.06em}
#title p{margin:10px 0 0;font-size:19px;font-weight:500;letter-spacing:.28em;color:__ACC__}
#title .bar{width:64px;height:4px;background:__ACC__;margin-bottom:18px;border-radius:2px}
#count{position:absolute;left:72px;bottom:64px}
#count .k{font-size:15px;font-weight:500;letter-spacing:.28em;color:rgba(255,255,255,.62)}
#count .v{font-size:58px;font-weight:700;letter-spacing:.02em;margin-top:2px}
#count .v em{font-style:normal;color:rgba(255,255,255,.4);font-weight:400;font-size:34px}
#track{position:absolute;left:72px;bottom:44px;width:260px;height:3px;background:rgba(255,255,255,.2);border-radius:2px}
#fill{height:3px;width:0;background:__ACC__;border-radius:2px}
.chip{position:absolute;right:96px;bottom:150px;padding:10px 26px 12px;background:linear-gradient(90deg,#ffb21a,#ff7a1a);color:#14100a;
  font-size:40px;font-weight:800;font-style:italic;letter-spacing:.04em;text-transform:uppercase;opacity:0;transform-origin:100% 50%;white-space:nowrap}
.num{position:absolute;right:110px;top:300px;text-align:right;opacity:0;white-space:nowrap}
.num b{display:block;font-size:150px;font-weight:800;letter-spacing:-.01em;line-height:1;color:#fff;text-shadow:0 0 40px rgba(255,140,30,.35)}
.num i{display:block;font-style:normal;font-size:30px;font-weight:600;color:__ACC__;letter-spacing:.12em;margin-top:6px}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="__DUR__" data-width="1920" data-height="1080">
<video id="plate" src="__PLATE__" muted playsinline data-start="0" data-duration="__DUR__"></video>
__AUDIO__
<div id="shade"></div>
<svg id="lines" viewBox="0 0 1920 1080"></svg>
<div id="title"><div class="bar"></div><h1>__TITLE__</h1><p>__SUB__</p></div>
<div id="count"><div class="k">PARTS</div><div class="v"><span id="cn">00</span> <em>/ __N__</em></div></div>
<div id="track"><div id="fill"></div></div>
<div id="chips"></div>
</div>
<script>
const T = __TRACKS__;
const W=1920,H=1080,FPS=T.fps,N=T.parts.length,PW=__PW__,PH=__PH__,ROWS=__ROWS__,IN=__IN__,OUT=__OUT__,DUR=__DUR__;
const cl=(v,a,b)=>Math.min(Math.max(v,a),b), c01=v=>cl(v,0,1);
const easeOut=t=>1-Math.pow(1-t,3);
const easeBack=t=>{const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(t-1,3)+c1*Math.pow(t-1,2)};
const svg=document.getElementById('lines'),NS='http://www.w3.org/2000/svg';
const mk=(tag,attrs)=>{const e=document.createElementNS(NS,tag);for(const k in attrs)e.setAttribute(k,attrs[k]);svg.appendChild(e);return e};
const root=document.getElementById('root');
const els=T.parts.map((p,i)=>{
  const d=document.createElement('div');d.className='callout';
  d.innerHTML='<span class="n">'+String(i+1).padStart(2,'0')+'</span><div><b>'+p.label+'</b><i>'+p.sub+'</i></div>';
  root.appendChild(d);
  return {d, line:mk('line',{stroke:'rgba(255,255,255,.9)','stroke-width':1.6,'stroke-linecap':'round'}),
          ring:mk('circle',{fill:'none',stroke:'__ACC__','stroke-width':2}), dot:mk('circle',{r:5.5,fill:'__ACC__',stroke:'#fff','stroke-width':1.6})};
});
const BEATS = __BEATS__;
if(N===0){document.getElementById('count').style.display='none';document.getElementById('track').style.display='none';}
const chipEls=BEATS.map(b=>{
  const box=document.getElementById('chips'); const o={b};
  if(b.chip){o.c=document.createElement('div');o.c.className='chip';o.c.textContent=b.chip;box.appendChild(o.c);}
  if(b.number){const m=String(b.number).match(/^([\d.,+\-\/x×%]+)\s*(.*)$/)||[null,b.number,''];
    o.n=document.createElement('div');o.n.className='num';o.n.innerHTML='<b></b><i></i>';o.n.querySelector('i').textContent=m[2]||'';
    o.target=m[1];box.appendChild(o.n);}
  return o;});
function rollNumber(target,p){ // counts up like Branch (00000 -> 32,768); non-numeric text just appears
  const v=parseFloat(String(target).replace(/,/g,'')); if(isNaN(v)) return target;
  const dec=(String(target).split('.')[1]||'').length, cur=v*p;
  const s=cur.toFixed(dec); return String(target).includes(',')?Number(s).toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec}):s;}
function drawChips(f){
  chipEls.forEach(o=>{const b=o.b, inF=b.word_f||b.settle_f, outF=b.end_f-6;
    const a=c01((f-inF)/7)*(1-c01((f-outF)/6)), pop=easeBack(c01((f-inF)/9));
    if(o.c){o.c.style.opacity=a;o.c.style.transform='translateX('+(40*(1-pop))+'px) skewX(-8deg)';}
    if(o.n){o.n.style.opacity=a;o.n.style.transform='translateY('+(20*(1-pop))+'px)';
      o.n.querySelector('b').textContent=rollNumber(o.target,easeOut(c01((f-inF)/24)));}});}
function sample(p,f){const k=cl(f-1,0,p.pts.length-1),a=Math.floor(k),b=Math.min(a+1,p.pts.length-1),u=k-a;
  return [p.pts[a][0]*(1-u)+p.pts[b][0]*u, p.pts[a][1]*(1-u)+p.pts[b][1]*u];}
function draw(t){
  const f=t*FPS+1; let shown=0;
  T.parts.forEach((p,i)=>{
    const e=els[i], inF=p.out-IN, outF=p.back-OUT;
    const a=c01((f-inF)/9)*(1-c01((f-outF)/6));
    const [px,py]=sample(p,f), ax=px*W, ay=py*H;
    const lx=cl(ax,PW/2+40,W-PW/2-40), ly=ROWS[p.row]*H;
    if(a>0.5) shown++;
    e.d.style.opacity=a;
    e.d.style.transform='translate('+(lx-PW/2)+'px,'+(ly-PH/2)+'px) scale('+(0.86+0.14*easeBack(c01((f-inF)/9)))+')';
    const up=ly<ay, ey=up?ly+PH/2:ly-PH/2, ex=cl(ax,lx-PW/2+30,lx+PW/2-30), pr=easeOut(c01((f-inF)/12));
    e.line.setAttribute('x1',ax);e.line.setAttribute('y1',ay);
    e.line.setAttribute('x2',ax+(ex-ax)*pr);e.line.setAttribute('y2',ay+(ey-ay)*pr);e.line.setAttribute('opacity',a);
    e.dot.setAttribute('cx',ax);e.dot.setAttribute('cy',ay);e.dot.setAttribute('opacity',a);
    const ph=(((f-inF)%45)+45)%45/45;
    e.ring.setAttribute('cx',ax);e.ring.setAttribute('cy',ay);e.ring.setAttribute('r',6+16*ph);e.ring.setAttribute('opacity',a*(1-ph)*0.7);
  });
  drawChips(f);
  document.getElementById('cn').textContent=String(shown).padStart(2,'0');
  document.getElementById('fill').style.width=(260*shown/N)+'px';
  const ti=document.getElementById('title');
  const tin=easeOut(c01((t-0.25)/0.7)), tout=c01((t-(DUR-0.7))/0.6);
  ti.style.opacity=tin*(1-tout);ti.style.transform='translateY('+(18*(1-tin))+'px)';
}
const tl=gsap.timeline({paused:true});tl.to({},{duration:DUR});window.__timelines={main:tl};
window.addEventListener('hf-seek',e=>draw(e.detail.time));draw(0);
</script></body></html>'''


def build(tracks, title, subtitle, plate, duration, beats=None, sound=None):
    fps = tracks.get('fps', 30)
    for b in beats or []:
        b['word_f'] = int(round(b['word_t'] * fps)) + 1 if 'word_t' in b else b.get('settle_f')
    rep = {'__BEATS__': json.dumps([b for b in (beats or []) if b.get('chip') or b.get('number')], separators=(',', ':')),'__PW__': PILL_W, '__PH__': PILL_H, '__ACC__': ACCENT, '__DUR__': duration, '__PLATE__': plate,
           '__TITLE__': title, '__SUB__': subtitle, '__N__': len(tracks['parts']), '__TRACKS__': json.dumps(tracks, separators=(',', ':')),
           '__ROWS__': json.dumps(ROWS), '__AUDIO__': _audio(sound), '__IN__': LEAD_IN, '__OUT__': LEAD_OUT}
    html = PAGE
    for k, v in rep.items():
        html = html.replace(k, str(v))
    return html


def _audio(cues):
    """<audio> cues from tech-explainer-video/scripts/sound_layer.py (music bed + SFX); the voice is ducked in later."""
    return '
'.join(f'<audio id="snd{i}" src="{c["src"]}" data-start="{c["start"]}" data-duration="{c["dur"]}" '
                     f'data-volume="{c["vol"]}" data-media-start="{c.get("media_start", 0)}"></audio>'
                     for i, c in enumerate(cues or []))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('tracks'), ap.add_argument('out')
    ap.add_argument('--title', default='EXPLODED VIEW'), ap.add_argument('--subtitle', default='')
    ap.add_argument('--plate', default='assets/plate.mp4'), ap.add_argument('--duration', type=float, default=10)
    ap.add_argument('--sound', help='sound.json from sound_layer.py cues (music bed + SFX as <audio>)')
    ap.add_argument('--beats', help='beats.json from beat_sheet.py: chips and kinetic numbers on their words')
    a = ap.parse_args()
    tr = json.load(open(a.tracks, encoding='utf-8')) if a.tracks != '-' else {'fps': 30, 'frames': int(a.duration * 30), 'parts': []}
    beats = json.load(open(a.beats, encoding='utf-8'))['beats'] if a.beats else None
    bad = overlap_report(tr)
    open(a.out, 'w', encoding='utf-8').write(build(tr, a.title, a.subtitle, a.plate, a.duration, beats,
          json.load(open(a.sound, encoding='utf-8'))['cues'] if a.sound else None))
    print(f'wrote {a.out}; label overlaps: {len(bad)}' + (f' e.g. {bad[:4]}' if bad else ''))
    sys.exit(1 if bad else 0)
