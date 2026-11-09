# Notes - 2D image to 3D object: "Como Transformar IMAGENS 2D em MODELOS 3D (Realistas) no Blender"

Source: https://www.youtube.com/watch?v=d-klXePH97g (Wellington Coloni, 12:16, **Portuguese**). Transcript is the EngineX `transcribe/translate` (pt to en). Blender **5.0.0**. Frame-NNNN is at about (NNNN-1)×3 s.

The technique is **projection-style modelling on an image plane**. A frontal photo becomes a light, textured relief mesh whose real depth casts real shadows. It is widely used for background buildings in games and archviz, and works for any flat-fronted object (product fronts, panels, signs, logos).

## Workflow
1. **Clean scene (0:57).** **A**, then **Delete** everything.
2. **Import the image as a plane (1:06-1:42).** **Shift+A > Image > Mesh Plane** (built in since 4.2; older versions use the add-on "Import Images as Planes" from Edit > Preferences > Add-ons). File browser options (frame-0035):
   - Relative Paths ✔, Force Reload ☐, Detect Image Sequences ☐
   - Material: **Shader Principled**, **Render Method Dithered**, Backface Culling ☐, Overwrite Material ✔
   - Texture: **Interpolation Linear**, **Extension Clip**, **Alpha ✔**, Auto Refresh ✔
   - Transform: **Size Mode Absolute**, **Height 1 m**, **Align: Camera's Main Axis**
3. **Image requirements (1:48).** It must be a **front view with weak perspective**. A long lens is fine, but strong perspective fails. Tip: ask an AI image model to redraw the subject "front view, orthographic".
4. **Orient (2:54-3:24).** **S** to scale up, **R X 90** Enter (stand the plane up, facing -Y/front), **G Z** to lift above the grid. Use **Material Preview** shading to see the texture.
5. **Cut the silhouette (3:30-4:36).** Front view **Numpad 1**, **Tab** into Edit Mode, **K** Knife. Left-click around the outline (rough is fine for distant assets), then **Enter** to confirm.
6. **Delete the outside (4:54).** Face select mode, **Shift**-click the outer faces, **X > Faces**. The texture stays mapped because the UVs are unchanged.
7. **Give it depth (5:27-5:48).** **A**, then **E** extrude backwards for the building depth, and **Tab** out. The result is a few vertices with the texture already applied.
8. **Relief detail (6:33-8:57).** For each feature (cornice, window, door, pilaster):
   - **K** knife its outline in front view, **Enter**, select that face.
   - **E** to extrude **outwards** (cornices, balconies, pilasters) or **inwards** (window and door recesses).
   - "The more patience, the better the result." Detail level depends on camera distance.
9. **Finish (9:12-10:39).** Add extra pieces (a ladder), then a global **bevel**: in Edit Mode select the edges and **Ctrl+B** for rounded corners that catch highlights.
   - Delete stretched side faces that read badly, or re-map them with another texture.
10. **Light and render (10:03).**
    - **EEVEE**: Viewport Samples 16, **Render Samples 64**, Temporal Reprojection ✔, **Raytracing ✔**, Shadows ✔, Film Filter Size 1.50 px, Film **Transparent ✔**.
    - One **Sun** lamp at a raking angle, rotated with **R** to make the reliefs throw shadows.
    - Then a final **Cycles** render.

## Why
The real displacement of the silhouette and reliefs produces correct parallax and contact shadows that a flat card cannot. Keeping the UVs from the plane avoids any texturing work.

## bpy equivalent
`scripts/image_to_3d.py`: `image_plane()` (Principled, alpha, height-scaled), `silhouette_from_alpha()` (bmesh: grid, delete transparent cells, dissolve), `extrude_depth()`, `relief_regions()` (inset and extrude rectangles given in image UV space), `bevel_all()`. This automates steps 2-9 for headless runs. The knife-by-hand steps become a polygon or rectangle list in normalised image coordinates.

## Unclear
- Extrude depth values (dragged by eye; none typed).
- Bevel width and segments for the global bevel.
- Sun strength and angle values.
