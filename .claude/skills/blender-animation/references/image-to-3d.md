# 2D image -> 3D object (relief modelling)

Source: `learning/image-to-3d/notes.md` (Wellington Coloni, Portuguese, translated by EngineX; Blender 5.0).
Script: `scripts/image_to_3d.py`. **Status: written from the video, NOT yet executed in an EngineX job.** Run it once on
a test image and review the frames before relying on it (add the result to the Failure log).

## When
A frontal, low-perspective photo of a flat-fronted subject: building, storefront, panel, sign, product front, logo.
Gives a light mesh with real depth, parallax and cast shadows, ideal for background assets. Not for objects that need
to be seen from behind - use the library or model it.

## Workflow (exact)
1. Clean scene (`A`, `Delete`). **Shift+A > Image > Mesh Plane** (built in since 4.2; older: add-on "Import Images as
   Planes"). File dialog options: Relative Paths on; Material **Shader Principled**, **Render Method Dithered**,
   Backface Culling off, **Overwrite Material on**; Texture **Interpolation Linear, Extension Clip, Alpha on**;
   Transform **Size Mode Absolute, Height 1 m, Align Camera's Main Axis**. -> `image_plane(path, height=1.0)`.
2. Source image: front view, weak perspective. If the photo is perspective-heavy, regenerate it "front view,
   orthographic" with an image model first.
3. Stand it up: `S` scale up, `R X 90`, `G Z` above the grid. Material Preview shading to see the texture.
4. Silhouette: front view (`Numpad 1`), Edit Mode, **K** Knife around the outline, `Enter`; delete the outside faces
   (face mode, `X > Faces`). UVs are kept, so the texture stays mapped. Headless: `silhouette_from_alpha` (cut-out PNG)
   or `keep_polygon(ob, poly_uv)` with a polygon in image UV space.
5. Depth: select all, `E` extrude backwards -> `extrude_depth(ob, depth)` (0.1-0.25 m for a building front).
6. Relief: per feature (cornice, window, door, pilaster) K its outline, select the face, `E` out (cornices, balconies)
   or in (recessed windows/doors) -> `relief_regions(ob, [((u0,v0,u1,v1), depth), ...])` (depth < 0 = toward viewer).
   More detail where the camera gets close; rough is fine for distant assets.
7. Finish: global bevel (`Ctrl+B`) so edges catch light -> `bevel_all(ob, width, segments)`; delete stretched side faces
   that read badly or re-map them with another texture.
8. Light and render: EEVEE (Viewport samples 16, **Render samples 64**, Raytracing on, Shadows on, Film filter 1.50 px,
   Film Transparent for compositing) or Cycles for the final. One **Sun** lamp at a raking angle so reliefs throw
   shadows; a ground plane to catch them.

## Rules from the review loop
- Judge at the *camera distance* of use; do not over-model.
- The relief must cast readable shadows: raking light (sun 30-50 deg from the facade), not frontal.
- Check the side silhouette: stretched UVs on the extruded sides are the usual defect.
