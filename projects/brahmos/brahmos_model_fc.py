# BrahMos airframe v2 for FreeCAD (EngineX freecad/script). Units mm. Axis +X, tail x=0, spike tip x=L=8400.
# Separate solid per part that moves or is named (02_parts.md). Internal layout is illustrative.
# v2: smooth spline ogive (v1 was faceted), fins at the very tail as in the photos, booster nested INSIDE the aft
#     chamber (integral rocket-ramjet: it slides out backwards at separation), total length exactly 8400, duct clear of spike.
import Part, math
V = App.Vector
P = dict(L=8400.0, R=335.0, wall=12.0, lip_r=262.0, cowl_x0=7200.0, cowl_lip_x=8300.0,
         spike_r=200.0, spike_x0=7300.0, spike_base_x=7650.0, duct_r=180.0, duct_x0=3400.0,
         booster_x0=160.0, booster_x1=1750.0, booster_r=278.0)
sheet = doc.addObject('Spreadsheet::Sheet', 'Params')
for i, (k, v) in enumerate(P.items(), 1):
    sheet.set(f'A{i}', k); sheet.set(f'B{i}', f'{v} mm'); sheet.setAlias(f'B{i}', k)
L, R, W = P['L'], P['R'], P['wall']
AX = V(1, 0, 0); O = V(0, 0, 0)

def revolve(pts):
    w = Part.makePolygon([V(x, r, 0) for x, r in pts] + [V(pts[0][0], pts[0][1], 0)])
    return Part.Face(w).revolve(O, AX, 360)

def tube(x0, x1, ro, ri):
    return revolve([(x0, ri), (x1, ri), (x1, ro), (x0, ro)])

def spline(pts):
    c = Part.BSplineCurve(); c.interpolate([V(x, r, 0) for x, r in pts]); return c.toShape()

def add(name, shape):
    o = doc.addObject('Part::Feature', name)
    try: shape = shape.removeSplitter()
    except Exception: pass
    o.Shape = shape; return o

objs = []
# --- nose cowl: smooth ogive shell (spline profile), open annular intake
x0, x1 = P['cowl_x0'], P['cowl_lip_x']
ts = [i / 12 for i in range(13)]
outer = [(x0 + (x1 - x0) * t, R - (R - P['lip_r']) * t * t) for t in ts]
inner = [(x, r - 22) for x, r in reversed(outer)]
e1 = spline(outer); e3 = spline(inner)
e2 = Part.LineSegment(V(*outer[-1], 0), V(*inner[0], 0)).toShape()
e4 = Part.LineSegment(V(*inner[-1], 0), V(*outer[0], 0)).toShape()
cowl = Part.Face(Part.Wire([e1, e2, e3, e4])).revolve(O, AX, 360)
objs.append(add('nose_cowl', cowl))
# --- intake cone (spike) with a slightly curved cone (spline) and its centre-body
sx0, sb = P['spike_x0'], P['spike_base_x']
sp = [(sb + (L - sb) * t, P['spike_r'] * (1 - t) ** 1.15) for t in [i / 10 for i in range(11)]]
sp[-1] = (L, 0.0)
ecurve = spline(sp)
spike_w = Part.Wire([Part.LineSegment(V(L, 0, 0), V(sx0, 0, 0)).toShape(),
                     Part.LineSegment(V(sx0, 0, 0), V(sx0, P['spike_r'], 0)).toShape(),
                     Part.LineSegment(V(sx0, P['spike_r'], 0), V(sb, P['spike_r'], 0)).toShape(), ecurve])
spike = Part.Face(spike_w).revolve(O, AX, 360)
objs.append(add('intake_cone', spike))
for k in range(3):
    s = Part.makeBox(220, 14, R, V(7400, -7, 0)); s.rotate(O, AX, 120 * k + 30)
    objs.append(add(f'intake_strut_{k + 1}', s.cut(spike).cut(cowl)))
objs.append(add('seeker', Part.makeCylinder(150, 30, V(7820, 0, 0), AX)))
# --- skins and rings (from the photos)
objs.append(add('skin_fwd', tube(5400, x0, R, R - W)))
objs.append(add('skin_aft', tube(150, 5400, R, R - W)))
objs.append(add('red_band', tube(x0 - 30, x0 + 30, R + 2, R - W)))
objs.append(add('dark_ring', tube(5400 - 25, 5400 + 25, R + 2, R - W)))
# --- internals (illustrative)
dr = P['duct_r']
objs.append(add('air_duct', tube(P['duct_x0'], sx0 - 2, dr + 15, dr)))
objs.append(add('guidance_unit', tube(6200, 7100, R - W - 8, dr + 25)))
objs.append(add('warhead', tube(5500, 6100, R - W - 8, dr + 25)))
objs.append(add('fuel_tank', tube(3600, 5400, R - W - 8, dr + 25)))
objs.append(add('combustor', tube(150, P['duct_x0'] + 10, R - W - 6, R - W - 22)))   # liner, the booster sits inside
objs.append(add('nozzle', revolve([(0, 292), (150, 300), (150, R), (0, R)])))         # aft ring, no throat (illustrative)
# --- booster nested in the chamber: case + its own bell nozzle + a marking band
b0, b1, br = P['booster_x0'], P['booster_x1'], P['booster_r']
booster = Part.makeCylinder(br, b1 - b0, V(b0, 0, 0), AX)
booster = booster.fuse(revolve([(b0 - 130, 225), (b0, 150), (b0, 120), (b0 - 130, 200)]))
objs.append(add('booster', booster))
objs.append(add('booster_band', tube(b0 + 500, b0 + 580, br + 2, br - 20)))
# --- lifting surfaces, X layout; fins at the very tail as in the photos
def surface(x_front, x_back, tip_front, tip_back, span, t):
    w = Part.makePolygon([V(x_back, R - 5, 0), V(x_front, R - 5, 0), V(tip_front, R + span, 0),
                          V(tip_back, R + span, 0), V(x_back, R - 5, 0)])
    s = Part.Face(w).extrude(V(0, 0, t)); s.translate(V(0, 0, -t / 2)); return s
for k in range(4):
    a = 45 + 90 * k
    w_ = surface(4700, 2700, 3150, 2750, 520, 26); w_.rotate(O, AX, a); objs.append(add(f'wing_{k + 1}', w_))
    f_ = surface(900, 40, 380, 60, 430, 20); f_.rotate(O, AX, a); objs.append(add(f'fin_{k + 1}', f_))
objs.append(add('cable_fairing', Part.makeBox(5900, 70, 45, V(1000, -35, R - 10)).cut(Part.makeCylinder(R - 2, 9000, V(-100, 0, 0), AX))))
# --- canister (separate group)
CR = 400.0
objs.append(add('canister_tube', tube(-300, 8700, CR, CR - 15)))
cap = Part.makeSphere(CR, V(8700, 0, 0)).common(Part.makeBox(CR, 2 * CR, 2 * CR, V(8700, -CR, -CR)))
m = App.Matrix(); m.scale(0.45, 1, 1); cap = cap.transformGeometry(m); cap.translate(V(8700 - 8700 * 0.45, 0, 0))
objs.append(add('canister_cap_front', cap))
objs.append(add('canister_cap_rear', Part.makeCylinder(CR, 40, V(-340, 0, 0), AX)))

doc.recompute(); check()
missile = [o for o in objs if not o.Name.startswith('canister')]
bb = App.BoundBox()
for o in missile: bb.add(o.Shape.BoundBox)
result['missile_length_mm'] = round(bb.XLength); result['missile_xmin_xmax'] = [round(bb.XMin), round(bb.XMax)]
result['span_mm'] = round(bb.YLength)
result['invalid'] = [o.Name for o in objs if not o.Shape.isValid() or o.Shape.Volume <= 0]
def ov(a, b): return round(doc.getObject(a).Shape.common(doc.getObject(b).Shape).Volume / 1e3, 1)
result['overlap_cm3'] = dict(spike_cowl=ov('intake_cone', 'nose_cowl'), duct_spike=ov('air_duct', 'intake_cone'),
                             booster_combustor=ov('booster', 'combustor'), booster_nozzle=ov('booster', 'nozzle'),
                             guidance_skin=ov('guidance_unit', 'skin_fwd'), fuel_skin=ov('fuel_tank', 'skin_aft'),
                             missile_canister=ov('skin_aft', 'canister_tube'), fins_booster=ov('fin_1', 'booster'))
result['booster_exit_clear_mm'] = round(292 - (br + 2))   # booster band must pass the aft ring's bore
for o in doc.Objects:
    if o.TypeId == 'Spreadsheet::Sheet': o.Visibility = False
export(objs, 'brahmos.glb'); export(objs, 'brahmos.step'); doc.saveAs(out + '/brahmos.FCStd')
for o in objs:
    if o.Name.startswith('canister'): o.Visibility = False
picture('brahmos_iso.png', view='iso')
picture('brahmos_side.png', view='front')
snapshot('brahmos airframe v2')
