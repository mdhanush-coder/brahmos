# How BrahMos Works
<!-- English only (user, 2026-11-09): narration AND every on-screen word. ~6 min at 146 wpm. Every spoken number is in
     01_research.md; [EST] values (about 1 km a second, 30 km radar horizon, 30 s vs 2 min) carry an "illustrative" tag.
     Visual directive after || on EVERY line. Frame: the radar screen (04_creative_plan.md).
     Palette night-blaze/dark; Unbounded (display) + Rajdhani (text, labels) + JetBrains Mono (HUD). -->

## 1. Hook || shot=sea
It's night on the open sea, and a warship's radar is sweeping quietly. Then a tiny dot appears at the edge, just a few metres above the water. || vis=radar HUD sweep, blip at the edge; cut to a low chase cam skimming night waves
That dot is covering about a kilometre every second, which leaves the ship roughly half a minute to react. || number=≈1 km/s; vis=HUD clock 0:30 slams in, blaze orange; tag=illustrative
[pause]
Its name is BrahMos, one of the fastest cruise missiles in the world, flying at nearly three times the speed of sound. || number=MACH 2.8; vis=missile rips past camera in slow motion, vapour cone, BRAHMOS title stamps in
But here's the strange part, the engine that keeps it this fast has no fan, no compressor and no turbine. So how does it fly? || vis=x-ray flash through the body: a hollow pipe where an engine "should" be; "?" chip

## 2. Open it || shot=explode
The name comes from two rivers, India's Brahmaputra and Russia's Moskva, because the two countries agreed to build it together in nineteen ninety-eight. || number=1998; vis=official map asset, India and Russia, two rivers draw as glowing lines and merge into the wordmark
It's about eight metres long and weighs around three thousand kilograms, so it's nearly as long as a city bus. || number=8.4 m · 3,000 kg; vis=missile beside a bus at true scale, then the skin turns to glass
Inside are five sections, and at the very front is the {Seeker}, its eye, followed by the {Guidance System}, its brain, and then the {Warhead}. || vis=explode: nose sections slide out, each glows as it's named (lime seeker, lime guidance, orange warhead)
Behind them sits the {Ramjet Engine}, which keeps it fast, and at the back is the {Booster}, which gets it off the ground. || vis=ramjet (cyan) and booster (orange) slide out; the stack holds, then re-assembles

## 3. Launch || shot=launch
BrahMos lives inside a sealed {Canister}, which is both its storage box and its launch tube. A twelve-wheeled truck carries three of them and raises them upright to fire. || number=3 per truck; vis=missile slides into the canister, lid locks; 12x12 truck at dusk raises three canisters to vertical
[pause]
Then the {Booster} ignites, and it's a solid fuel rocket, a lot like a festival rocket, with its fuel packed in as a solid block. || vis=cap blows off, a column of fire and smoke; inset cutaway: the solid fuel grain in orange
As it leaves the canister, the missile tips over toward its target, and within a few seconds it's going faster than sound. || chip=SUPERSONIC; vis=slow-motion pitch-over arc, a shock cone forms at the nose, the HUD speed needle passes MACH 1
Then the booster drops away, and the real engine takes over. || vis=speed ramp into slow motion: booster separates and tumbles away, the ramjet lights
[pause]
But that raises a question. If the missile already has an engine, why carry a heavy booster at all? || vis=freeze frame, booster circled, chip "WHY?"

## 4. Ramjet || shot=focus
The answer is the {Ramjet Engine}, one of the simplest engines ever built, because it has no moving parts at all. || chip=ZERO MOVING PARTS; vis=lengthwise cutaway, the ramjet duct glows
A normal jet engine uses fans and a compressor to squeeze the air, and a turbine at the back to spin them. || vis=split screen: turbofan cutaway with spinning blades vs the empty ramjet pipe
A ramjet does the squeezing with speed alone, kind of like the wind that pushes against your face on a fast motorbike. || vis=inset: rider seen from behind, air streaks compressing; back to the duct, cyan air pours in
The air hits the {Intake Cone} in the nose and forms shock waves, and every shock squeezes the air tighter and heats it up. || vis=macro on the cone, oblique shock lines appear one by one, the air ramps from cyan to orange; tag=illustrative
Liquid fuel is sprayed into that hot, squeezed air, it burns and expands, and it blasts out of the {Nozzle} to push the missile forward. || vis=fuel spray rings, the flame front fills the chamber, exhaust leaves the nozzle, thrust arrow
[pause]
There's a catch, though. The air only gets squeezed if the missile is already moving fast, so a ramjet sitting still produces no thrust at all. || vis=graph draws itself: thrust vs speed, zero at rest, rising after MACH 1
That's why the booster pushes it past the speed of sound first, and the ramjet then holds it at nearly Mach two point eight. || number=MACH 2.8; vis=graph: the orange booster segment hands over to the cyan ramjet segment

## 5. Guidance || shot=focus
Speed is only half the job, because hitting the right target at that speed is the work of the {Guidance System}. || vis=camera flies into the mid-body, the guidance bay glows lime
It can cruise as high as fifteen kilometres, where an inertial system keeps counting where it is. Satellite navigation corrects its small errors, just like the map on your phone. || number=15 km; vis=flight profile side view; a ghost path drifts, satellite pings snap it back; phone map blue dot inset
So why would a missile this fast fly so low? For the final stretch it drops down and skims the sea, only about ten metres above the waves. || number=≈10 m; vis=dive to the sea, chase cam inches above the waves, spray trail
That's where the curve of the Earth helps, because a ship's radar can only see something that low from about thirty kilometres away. || number=≈30 km; vis=radar horizon diagram: curved Earth, the beam line, the missile hidden under the curve; tag=illustrative
[pause]
As it closes in, the {Seeker} wakes up, sends out its own radio waves, and locks on using the echo that comes back. || vis=the seeker emits lime radar rings, an echo returns, a LOCK bracket snaps onto a ship silhouette
In the last moments it can weave in an S shape or climb and dive steeply, which makes it much harder to stop. || vis=top view S-weave drawn in lime; side view pop-up and steep dive
That's why it's called fire and forget. Once it's launched, the missile makes every decision on its own. || chip=FIRE AND FORGET; vis=the launcher truck lowers its canisters and drives off

## 6. Speed is the weapon || shot=dive
But the real power of BrahMos isn't only its {Warhead}, it's the speed, and that comes down to one simple rule of physics. || vis=push into the warhead, fade to night blue, space for the formula
The energy of a moving object grows with the square of its speed. Twice the speed gives four times the energy, and three times the speed gives nine. || number=E = ½ m v²; vis=the formula writes itself, v² glows; a bar grows 1 → 4 → 9
That's why BrahMos hits with roughly nine times the kinetic energy of a typical subsonic cruise missile. || number=9×; vis=two energy bars, the BrahMos bar slams to 9x
Think of a cricket ball tossed gently, and the same ball bowled three times faster, and you can feel the difference. || vis=inset: the same ball slow vs fast, impact ripple nine times bigger
[pause]
Speed also steals time. The last thirty kilometres take a subsonic missile about two minutes, but BrahMos covers them in around thirty seconds. || number=≈2 min vs ≈30 s; vis=race bars over the sea; back to the hook's radar, clock ticking; tag=illustrative

## 7. From everywhere || shot=return
So where can it be fired from? Almost anywhere, from ships, from trucks, from under water and from the air. || chip=LAND · SEA · AIR · UNDERWATER; vis=four quick panels, each launch in turn
The air version weighs two and a half thousand kilograms, and it's the heaviest weapon the Sukhoi thirty fighter has ever carried. || number=2,500 kg; vis=Su-30MKI belly with BrahMos-A, release, drop, the booster lights
Its range started at two hundred ninety kilometres, India now has versions that reach about five hundred, and one with around eight hundred is in development. || number=290 → 500 → 800 km; vis=official India map, range rings grow from the coast; outer ring dotted "in development"

## 8. Made in India || shot=return
In May twenty twenty-five, after Operation Sindoor, India's Prime Minister publicly confirmed that BrahMos had been used. || chip=OPERATION SINDOOR · MAY 2025; vis=night launch silhouette, a headline-style card (no target map)
That same month a new factory opened in Lucknow, and today about eighty percent of the missile is made in India. || number=≈80%; vis=factory line, a bar fills to 80%
Other countries are buying it too, the Philippines already has it on its coast, and Vietnam and Indonesia have reportedly signed deals as well. || vis=globe: Philippines lights (deployed), Vietnam and Indonesia light (reported)

## 9. Close || shot=sea
So BrahMos is really a flying pipe, a bit like a blowtorch that breathes its own speed. A booster lifts it, a ramjet with no moving parts keeps it near Mach three, and a brain hides it below the radar. || vis=one continuous x-ray fly-through nose to nozzle, air → shock → flame; the three systems light orange, cyan, lime
[long pause]
And that ship we started with had just half a minute. So tell me, what would you do with those thirty seconds? || vis=back to the night radar, clock at 0:00, freeze; end card "Tell us in the comments"
