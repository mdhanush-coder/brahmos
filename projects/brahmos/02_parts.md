# BrahMos parts list (one shared model for every chapter: brahmos_model_fc.py -> brahmos.glb)

Axis = +X, tail at x = 0, spike tip at x = 8400 mm. Dimensions from 01_research.md (8.4 m x ~0.67 m, 4 + 4 surfaces);
layout from the 4 reference photos in refs/ (silver body, red band at the nose joint, dark ring between sections,
cable fairing on the side, X-configured clipped-delta wings mid-body, small clipped-delta tail fins). The internal
layout and the separable booster are ILLUSTRATIVE (no public cutaway): labelled so on screen.

| Spoken name | Object | x range (mm) | Material (Blender) | Notes |
|---|---|---|---|---|
| Intake Cone | intake_cone | 7300-8400 | brushed titanium | central spike, tip 100 mm ahead of the cowl lip |
| Seeker | seeker | ~7850 | lime emissive dish | radar dish inside the spike (x-ray only) |
| — | nose_cowl | 7200-8300 | silver aluminium | ogive shell, open annular intake |
| Guidance System | guidance_unit | 6200-7100 | dark electronics + lime | annular box around the duct |
| Warhead | warhead | 5500-6100 | dark steel, orange highlight | annular |
| — | air_duct | 3400-7300 | translucent cyan when cut away | carries the air from intake to combustor |
| (fuel) | fuel_tank | 3600-5400 | amber | annular tank around the duct |
| Ramjet Engine | combustor | 1500-3400 | heat-tinted steel | liner; flame lives here |
| Nozzle | nozzle | 1500-1650 | dark heat-blued steel | ramjet nozzle ring at the aft end |
| Booster | booster | -250-1500 | orange-banded silver | solid rocket, own nozzle bell, separates |
| — | skin_fwd / skin_aft | 5400-7200 / 1500-5400 | silver aluminium | hollow skins (glass in x-ray shots) |
| — | red_band, dark_ring | 7200 / 5400 | red / near-black | from the photos |
| — | wing_1..4, fin_1..4 | 2650-4600 / 1550-2250 | silver | X layout (45 deg) |
| — | cable_fairing | 2400-7000 | silver | along the top |
| Canister | canister_tube, canister_cap_front, canister_cap_rear | -400-8700 | olive + maroon camo, silver dome cap | r 400 mm |
| (truck) | library asset | — | green/maroon camo | 12x12 launcher, 3 canisters (find_asset first) |
