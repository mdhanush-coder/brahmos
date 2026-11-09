# Asset library: catalog.json and find_asset.py

## Where it is
The library is **inside the EngineX Blender pod** at `/library` (found via `blender/script`: the `find_assets` DB,
`BLENDER_LIBRARY=/library`). It is not on the user's disk. There is no 5,000-file local library; EngineX's is
**10,853 entries** (8,467 models, 1,154 materials, 547 HDRIs, 685 scenes), which `assets/catalog.json` indexes.
`.claude/skills/blender-animation/assets/catalog.json` (copy in `./skills/blender-animation/assets/`).
Paths in the catalog are pod paths. Regenerate with the job in `learning` history: dump `find_assets.__globals__['_db']()`
then `build_catalog.py` (see scratch notes in `tests/`); counts and sources: NVIDIA SimReady/Omniverse (USD), AI-generated
GLB, DigitalXModels FBX, KitBash3D, Video Copilot, vMaterials/automotive MDL, BackLight HDRIs.

## Entry schema
`id, name, category, tags[], path (pod path), blender_file (importable GLB if any), format, source, licence,
attribution, thumb, type (model|rig|material|texture|HDRI|scene), polycount (triangles; null = not measured),
texture_maps {albedo|normal|roughness|metallic|orm|ao|height|opacity|emissive|glossiness|specular: path or 'embedded'},
orm_channels ('R=ao G=roughness B=metallic'), animations (GLB only)`.
Honest gaps: polycount known for 4,544 of 8,467 models (GLB read from the header, USD where `pxr` loaded in time; FBX and
the rest null); `rig` = skeleton present (33 entries; FBX detected by a byte scan, may over/under-report).

## Searching
```
python .claude/skills/blender-animation/scripts/find_asset.py gear metal
python find_asset.py --type HDRI studio            # softboxes, photo studios
python find_asset.py --type material --map normal --map orm brushed aluminium
python find_asset.py --type model --max-tris 200000 --category automotive motor
python find_asset.py --type rig --json
```
All keywords must match name/tags/category (synonyms: couch<->sofa, motor<->engine, aluminum<->aluminium, ...).
`--selfcheck` runs the unit assertions. Faster for a single query inside a job: `find_assets(words, kind, category, n)`.
EngineX also has `find_asset` (the same DB with pictures): use it when you need to *see* options.

## Using an asset in a job
- Model: `place_asset("<id>", location=..., size=<longest side m>, floor=True)` returns a holder empty (parents
  meshes with their materials). **SimReady USD meshes are NOT parented under it**: use `gather_asset()` or collect by set
  difference. USD import resets scene frame range: set it afterwards. Attribution must be credited when published.
- Material: build from `texture_maps` with `library_material(name, maps, tint=...)`; ALWAYS `assign_material`; check
  `material['missing_maps']`. Colour variants (Anodized Red/Black/Blue) share one near-white albedo: the colour is the tint.
  ORM = R occlusion, G roughness, B metallic. Box-mapped (no UVs needed). Falls back to `anodized()`/`metal()`.
- HDRI: `hdri_world(path, strength, rotation_deg, background_strength=1.0)`.
- Scenes (USD): reference environments; heavy, use for context only.

## What the library does NOT have (so model it)
Multi-part technical assemblies (gearbox = 3 meshes, electric engine = 1), drone motors, bearings with housings. Use
`product_models.py` or separate by loose parts. Always check `mesh_objects` after placing.
Test products found: `ai3d-vintage-pocket-watch-d1bc3d` (95k tris), `flightkit-drone` (32k tris),
`steeringSystem_steering_gearbox_a01` (3 parts), `powerTool_drill_a01` (5 parts).
