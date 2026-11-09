# Transcript - Import a CAD model and create an Exploded View animation in Blender 3.0 (Derek Elliott)

Source: https://www.youtube.com/watch?v=KFb4r8UVO0A  
Transcribed with EngineX `transcribe/transcribe` (large-v3, word-aligned). Single speaker (narrator), so no speaker labels.

**[00:00.43 - 00:01.77]** Hello, everyone, and welcome.

**[00:01.85 - 00:03.53]** I'm Derek Elliott from dirk.com.

**[00:03.61 - 00:11.98]** And today, I've got a quick video showing how I would import a CAD model, split it up into pieces, and then create an exploded view animation.

**[00:12.16 - 00:16.88]** This is a really popular look that a lot of people ask for when it comes to product animation in particular.

**[00:17.06 - 00:20.69]** Whether or not there's actually a good reason for doing this, I'm not so sure about.

**[00:20.71 - 00:22.29]** But hey, it does look pretty cool.

**[00:22.73 - 00:35.44]** It's basically the same thing that we did with the camera animation portion of my cell phone tutorial, but with a little more attention given to part separation, keeping track of origin points, some shape key deformation to make this little clip pop.

**[00:35.82 - 00:36.58]** Yeah, things like that.

**[00:36.76 - 00:42.50]** Now, of course, if you want to follow along, you'll have to have a model to work with, really just anything with multiple parts.

**[00:42.52 - 00:44.28]** It doesn't have to be a CAD model.

**[00:44.64 - 00:46.04]** CAD models are just usually kind of

**[00:46.58 - 00:50.18]** Disgusting with too many parts and great for this type of animation.

**[00:50.64 - 01:03.03]** Now unfortunately I won't be able to provide the file for this particular one like I normally would on my Patreon since it does have some proprietary details but the methods we'll cover should get you pretty well up to speed on the basic process.

**[01:03.39 - 01:10.53]** Now just really quick the model I'm using is of a mechanical leveling device for a smartphone or action camera called GravGrip.

**[01:10.89 - 01:21.51]** It was designed by a guy named Kevin Thomas, who reached out to me a long time ago about making a Kickstarter ad for its launch and yada, yada, yada raised over a million dollars.

**[01:21.71 - 01:26.77]** And it is a product that you can buy super cool thing and great for this type of animation.

**[01:27.09 - 01:31.33]** So definitely check that out if you're into it, but let's jump into the video.

**[01:35.56 - 01:41.10]** All right, so I'm in a pretty default Blender, three point oh beta scene here.

**[01:41.12 - 01:43.10]** We've got the default cube and everything.

**[01:43.14 - 01:46.44]** I'm going to get rid of those and go ahead and import my CAD model.

**[01:47.04 - 01:51.50]** This is one that I believe was exported from either Fusion three sixty or maybe SOLIDWORKS.

**[01:52.00 - 01:55.36]** I have to follow up on the details there, but let's go and import.

**[01:55.66 - 01:56.90]** It's going to be an OBJ.

**[01:57.88 - 02:03.34]** OBJ, I've found, tends to be the easiest format to work with between CAD files and Blender.

**[02:04.00 - 02:06.20]** People just always seem to be able to export it.

**[02:06.89 - 02:09.55]** And yeah, it's just a pretty common file format.

**[02:10.17 - 02:14.13]** If you're working with something like a STEP file, then that might be something that you

**[02:14.91 - 02:39.62]** Need to get an add-on for I do actually have an add-on called stepper Which will allow me to import step files and works really well But uh for the most part I've never had too much issue with people exporting OBJ files for me now for some reason they usually come in You know bigger than they should be or just bigger than that You know, it's scaled obviously proportionally, but I find that I almost always need to scale things down by like point one and

**[02:40.50 - 02:44.77]** and then sometimes even point one again to get it to a more reasonable size.

**[02:44.87 - 02:47.73]** But I think I'll leave it at the previous scale.

**[02:47.81 - 02:52.07]** So that's just to get things working a little bit better with my existing grid.

**[02:52.09 - 02:57.25]** I basically want to be able to move things and have them snap along the grid.

**[02:57.33 - 03:01.30]** But of course, with most CAD projects, everything's going to be pretty well to scale.

**[03:01.40 - 03:04.26]** So if you need to check the scale, that's something you can do.

**[03:04.36 - 03:07.40]** But for our purposes, we're going to be talking more about the animation here.

**[03:08.02 - 03:10.18]** And of course, you can always scale things after the fact.

**[03:10.26 - 03:17.09]** Now, just for the sake of making myself feel a little better, the scale on this object right now is point one because we scaled it down.

**[03:17.11 - 03:19.05]** So I'm going to press control A and apply the scale.

**[03:19.61 - 03:22.22]** So now this is, like I said, a CAD file.

**[03:22.24 - 03:26.52]** And it came with some of these different parts were probably hidden before.

**[03:27.46 - 03:34.94]** And so, you know, they shouldn't have necessarily exported, but this is completely common when I'm receiving CAD files to kind of just have extra stuff in there.

**[03:35.00 - 03:36.65]** And this is all just one piece.

**[03:36.67 - 03:39.47]** So you might be thinking, you know, how are we going to make an exploded view?

**[03:39.87 - 03:42.35]** We need to like go in and separate all these pieces.

**[03:42.43 - 03:44.11]** And yeah, that's basically exactly what we're going to do.

**[03:44.87 - 03:52.96]** So what I want to do first is sometimes you can pick different parts by like OBJ files could sometimes have different parts.

**[03:53.56 - 03:55.56]** Materials already assigned.

**[03:55.60 - 03:57.94]** See there, you can see we could select those objects that way.

**[03:58.74 - 04:01.53]** You know, something here was powder coat black.

**[04:02.17 - 04:02.61]** Select.

**[04:02.67 - 04:04.43]** Looks like that's a small piece on the GoPro.

**[04:04.75 - 04:11.09]** And I should say that this, I'll probably cover it in the intro, but this is the GravGrip hydraulic stabilizer.

**[04:11.24 - 04:12.74]** It's no batteries or anything.

**[04:12.78 - 04:14.10]** It's kind of just a camera stabilizer.

**[04:14.76 - 04:15.18]** leveler.

**[04:15.22 - 04:18.84]** It's a pretty cool project I work on with a guy named Kevin for a Kickstarter.

**[04:19.42 - 04:22.12]** And yeah, it did really well and he's selling it.

**[04:22.14 - 04:24.22]** So if you want to buy this, you can.

**[04:24.32 - 04:26.92]** But yeah, it's a good example for this exploitive view.

**[04:26.94 - 04:33.10]** So what I'm going to do is press tab to go into edit mode and then I'm going to select everything.

**[04:33.12 - 04:41.16]** I don't think I really need to do that, but I'm going to press P and separate by loose parts and tabbing back out of edit mode.

**[04:41.20 - 04:41.98]** Now you'll see that

**[04:42.42 - 04:44.77]** It has kind of successfully separated this.

**[04:45.21 - 04:50.23]** You can see we've got some issues here where the cameras, for example, weren't separate.

**[04:51.11 - 04:51.97]** But that's okay.

**[04:52.03 - 04:56.37]** And to see those separate parts a little easier, I'm going to go up here into this top drop down.

**[04:56.71 - 04:58.38]** And then Blender has this mode called Random.

**[04:58.75 - 05:08.74]** which will just randomly assign kind of these pastel colors to different parts of the model, which is really helpful for differentiating them all and just kind of seeing what those separate parts are.

**[05:08.78 - 05:15.99]** So with that done, I'll also turn on this cavity option just because it kind of highlights our edges a little bit better and that looks nice, I think.

**[05:16.93 - 05:33.20]** But yeah, what I want to do now is just go through and start deleting all these things So circle selecting is the way I usually like to do that But you'll see that you know I can kind of drag across and it won't always get everything and that's because right now everything has the same Origin which is right here at that point.

**[05:33.26 - 05:43.02]** So, you know if I scroll over that it's gonna get everything but what I'll do to make the selection process a little easier just right click and then set origin to geometry and

**[05:43.40 - 06:10.70]** and what that's going to do is assign origins you can see all these little dots here are now assigned to kind of the average location of all the the vertices that make up those different parts so now i can just go in here i'm just going to delete the the phone delete the gopro delete that now sometimes when you're doing this you may have yeah so there's these little parts sometimes you can avoid having these get separated in different pieces if you remove doubles when you start the file

**[06:11.75 - 06:13.81]** But that's not always a good thing.

**[06:13.88 - 06:15.78]** Sometimes with these CAD models, there can be

**[06:16.85 - 06:42.00]** you know geometry in here like there's these bearings that are perfectly aligned with the housing that they're in and if you remove doubles to remove overlapping geometry then it might accidentally connect pieces that you wanted to be separate so just be careful when you're doing remove doubles sometimes it's best to just try separating by loose parts first and then and then if you need to you can remove doubles on individual pieces after the fact

**[06:43.10 - 06:44.52]** But this, for example, is a little logo.

**[06:44.54 - 06:47.23]** I know that this is supposed to be part of the mold here.

**[06:47.25 - 06:50.81]** So I'm just going to press Control J to join those together.

**[06:51.23 - 06:58.46]** But this is kind of the first step to creating an exploded view like this would be to just sort of get your model cleaned up to the point you want.

**[06:59.02 - 07:01.16]** and remove any additional pieces.

**[07:01.58 - 07:05.88]** And then the next thing we're going to do is just kind of organize, just make sure we kind of understand the model.

**[07:06.58 - 07:10.12]** So what I'll do is just press, I'm actually going to turn on my little gizmo here.

**[07:10.49 - 07:15.11]** I can hold control and that's going to be really helpful for putting this back together.

**[07:15.51 - 07:18.73]** If I know I'm moving things at defined increments, it's going to be easier too.

**[07:19.43 - 07:48.64]** line them back up than if i just did that because then that you know to get it back would be you know i wasn't sure exactly where it was so holding ctrl to work with the grid and if you do need to adjust the grid you can you can change it up here and then also for those of you who are concerned about the scale of objects the units are in this tab right here the scene tab scene properties tab but i'm just going to kind of pull all these different things apart and just sort of get a little bit of feel for the model so this is kind of a pin that holds everything together

**[07:49.16 - 07:52.23]** I believe that is overmolded into that part.

**[07:52.25 - 08:01.69]** So those are actually, they're separate pieces, it looks like, at least in the CAD file they are, but I might just go ahead and join them or at least, yeah, I'll just join them.

**[08:01.71 - 08:07.50]** And if I needed to assign different materials, which I've select this one, select that one, control J to join them.

**[08:08.04 - 08:12.80]** If I needed to assign different materials to those, then what I can do is just pressing L.

**[08:13.99 - 08:41.99]** we'll select islands and when we did that initial command which was to separate everything into individual parts that's basically what it's doing it's just going in and selecting mesh islands that are not connected to other parts of the mesh and joining them together so we've also got a bearing here so i'm going to pull this back and just kind of pulling the model apart getting it to a point where i can sort of understand all the different parts and pieces here you can see we've got this ball that goes in here this is a weight set that's used to adjust the um

**[08:42.47 - 08:44.93]** the balance of the camera on the mount here.

**[08:45.69 - 08:47.55]** This is actually an old version of the grab grip.

**[08:47.97 - 08:54.89]** The new versions don't even have that, but I'm going to select all these pieces, maybe these, and then I'm going to parent that to that.

**[08:55.12 - 08:57.08]** So let's parent those objects.

**[08:57.10 - 08:59.02]** Now this part, yeah, it kind of rotates in there.

**[08:59.16 - 09:07.12]** I don't think that's really going to be crucial to the exploded view, but in case we do want to rotate, we want it to rotate about this kind of ball joint there.

**[09:07.16 - 09:09.47]** So I'm going to assign a new origin.

**[09:09.50 - 09:10.59]** And the way I'm going to do that is just

**[09:11.16 - 09:22.61]** finding some good geometry where I know would be the center of that, Shift S, snap my cursor to selected, tapping out of edit mode and then right click, set origin to three D cursor.

**[09:22.95 - 09:26.62]** Now when I rotate that, it's going to rotate as it should kind of along that.

**[09:27.00 - 09:30.26]** Now there might be a couple other places where we want to do a similar type of thing.

**[09:30.62 - 09:34.60]** For example, this, you know, if I wanted to rotate it, I would want it to rotate on this axis.

**[09:34.62 - 09:37.23]** But right now, the origin has been placed over here.

**[09:37.28 - 09:46.73]** And when we do that snap origin to geometry, that's just going to take the average of all these points and kind of put it right in the middle to what it assumes is kind of the average.

**[09:46.77 - 09:50.67]** But with all this threading down here, it's kind of a more dense area.

**[09:50.75 - 09:52.25]** So it's kind of pulled our origin there.

**[09:52.91 - 09:57.02]** Anyways, to get it back to about where I want, I want it to kind of be in the middle of this circle.

**[09:57.10 - 10:00.66]** So I'm just going to select some, you know, a logical place.

**[10:00.78 - 10:03.38]** And hopefully your CAD file is as clean as this.

**[10:03.78 - 10:05.88]** Sometimes they're not so clean.

**[10:05.90 - 10:09.04]** This one's not too bad, but this is an exported CAD model.

**[10:09.06 - 10:14.15]** So, you know, some stuff is a little bit funky, but it's overall, it's really easy to work with.

**[10:14.17 - 10:14.71]** Not too bad.

**[10:15.27 - 10:17.99]** But that's going to be what I assume is the top and bottom of that circle.

**[10:18.07 - 10:18.57]** Exactly.

**[10:18.63 - 10:20.85]** So Shift S, cursor two selected.

**[10:21.37 - 10:35.98]** then set the origin to the three cursor now if I was going to rotate this you know it's going to rotate on that axis so that's making me think too that we probably want to parent this object to this so let's parent that keep transform

**[10:37.22 - 10:38.20]** So that's together.

**[10:38.68 - 10:43.18]** And then this one, let's parent to this as well.

**[10:43.28 - 10:44.75]** Control P object.

**[10:45.35 - 10:47.21]** So now this is all together.

**[10:47.23 - 10:49.65]** Now this I think actually is part of that.

**[10:49.69 - 10:53.33]** Maybe another overmold situation, but let's just do it as a parent.

**[10:53.51 - 10:55.43]** And then so now is this all together?

**[10:55.51 - 10:57.74]** Okay, so the last thing would be to connect this ball.

**[10:58.10 - 10:59.64]** Control P object, keep transform.

**[11:00.06 - 11:04.24]** So again, I'm just trying to kind of understand my model and the different parts here.

**[11:05.20 - 11:10.20]** You don't need to parent everything, especially if you're just going to be doing like a linear axis animation.

**[11:10.26 - 11:15.87]** But in case I want to do some rotation here, I want these to be moving sort of logically with it.

**[11:16.73 - 11:19.23]** So let's pull that back.

**[11:19.37 - 11:21.97]** So I think that bearing is on the back side.

**[11:22.67 - 11:24.15]** And then we've got all these parts in here.

**[11:24.17 - 11:26.09]** And this is kind of the meat of the device.

**[11:26.21 - 11:30.45]** So putting this all together here, that caps out there.

**[11:31.11 - 11:34.03]** And then we've got this part with a little gear on the end of it.

**[11:34.49 - 11:41.76]** And now when I do the animation, I'll probably have to figure out a way to maybe move that out of the way so that we can have, you know, there's no clipping when that passes through there.

**[11:42.78 - 11:44.66]** But yeah, just trying to understand the model.

**[11:44.68 - 11:46.00]** This is kind of the first step.

**[11:46.58 - 11:49.80]** You know, if you are the one who actually made the model, you might not need to do this.

**[11:49.86 - 12:00.93]** But for me, anytime I'm handed CAD data and I'm going to be animating it, the first thing I do is just, you know, massive inspection of the model, just trying to understand the different parts and pieces, make sure I understand how it works.

**[12:01.71 - 12:04.13]** so that when I'm doing an exploded view like this, it all makes sense.

**[12:04.19 - 12:12.13]** But with this all out there, I think that looks like we've got everything how we want, got every part separated.

**[12:12.15 - 12:17.04]** You know, if you needed to go in and separate things more, you could, but this all looks pretty good.

**[12:18.16 - 12:25.88]** So what I want to do now is, you know, I could probably just leave it all apart like that because that kind of looks nice.

**[12:25.92 - 12:27.70]** So maybe we'll actually do that.

**[12:27.74 - 12:30.20]** So let's say on maybe frame thirty,

**[12:30.89 - 12:33.61]** we're going to have it look like this.

**[12:33.75 - 12:37.49]** Well, I guess these would be, you know, maybe these would be a little bit lower.

**[12:38.49 - 12:41.35]** And then, you know, I'm not gonna do it that way.

**[12:41.39 - 12:45.70]** I'm just gonna put, I'm gonna put it all, I'm gonna put it all back together.

**[12:45.72 - 12:49.80]** So let's just, let's pull that in there, pull that in there.

**[12:49.82 - 12:53.04]** This builds character, putting it back together.

**[12:53.66 - 12:59.83]** It's kind of fun too because it's really easy when you hold ctrl to snap everything together.

**[13:00.61 - 13:04.14]** It's kind of just like a super easy Lego kit.

**[13:04.94 - 13:09.30]** So this is usually the way I actually like to do it is with it all assembled.

**[13:09.84 - 13:11.82]** And then I'll insert my first round of keyframes.

**[13:11.84 - 13:12.74]** So that's what I want to do now.

**[13:12.76 - 13:15.76]** I'm going to go to frame one, press A to select everything.

**[13:15.86 - 13:18.04]** And then down here I can go into my keying set.

**[13:18.66 - 13:20.88]** And for the active keying set, I'm going to do location.

**[13:21.88 - 13:22.44]** Select that.

**[13:22.82 - 13:25.52]** And now with all those selected, I can just press I.

**[13:26.06 - 13:31.62]** And now we'll insert keyframes on the selected keying set, which right here is location.

**[13:31.66 - 13:34.04]** So if I click on any of these, you can see they have

**[13:35.34 - 13:36.68]** location keyframes selected.

**[13:36.70 - 13:44.61]** So if I moved all this out of the way because there's a keyframe here, it's going to snap it back because it's all tied to that keyframe.

**[13:44.63 - 13:49.53]** And that's one thing that's really great about keyframes too, besides just using them for animation, obviously,

**[13:50.15 - 13:53.39]** You can kind of use them as save states to make sure things stay in place.

**[13:53.88 - 14:00.60]** Odd to that, sometimes when I'm just doing still renders is I'll actually add animation to the objects just to kind of hold them in different positions.

**[14:01.12 - 14:05.01]** But what I'm going to do now is just advance to a known frame.

**[14:05.03 - 14:09.95]** You could just go to frame one, honestly, but I'll go out one second or so, which is

**[14:10.79 - 14:17.38]** if I was in the thirty frames per second setting, which this is again Blender three point of beta.

**[14:17.48 - 14:23.44]** There's a I'm going to run into something that's confusing, but so far it looks pretty much like Blender two point nine.

**[14:23.46 - 14:24.28]** So we're in good shape.

**[14:25.12 - 14:27.67]** But now with all those together,

**[14:28.23 - 14:31.05]** I'm going to start doing the yeah, the exploded animation.

**[14:31.11 - 14:41.73]** So I think for that, what I want to do is use this little record button auto key, which is going to automatically insert keyframes when I move things.

**[14:41.77 - 14:43.05]** Now, let's see if that works.

**[14:43.08 - 14:44.01]** Let's drag that down.

**[14:44.13 - 14:48.02]** Okay, so it did, but it inserted keyframes for everything.

**[14:48.66 - 14:50.56]** And I really just want to do it for location.

**[14:50.58 - 14:53.92]** So yeah, I can do only active keying set.

**[14:53.94 - 14:55.78]** So now when we move this down,

**[14:56.66 - 15:03.96]** it's only going to do on the location and that's just to avoid, you know, I'm not going to be messing with the scale, um, the rotation I might do eventually, but I don't want to worry about it now.

**[15:04.92 - 15:10.20]** Um, so just, just inserting location key frames, and then maybe we, you know, we pull this one down too.

**[15:10.22 - 15:12.30]** Maybe these don't go as high.

**[15:12.64 - 15:22.38]** So now as I insert key frames, it's going to, uh, it's going to audit or sorry, when I move things, it's going to automatically insert key frames, which is really handy for doing this type of an animation.

**[15:22.40 - 15:25.49]** So maybe this whole thing, you know, slides down out of there.

**[15:26.07 - 15:27.73]** Maybe this slides down a little bit.

**[15:28.09 - 15:32.15]** So this basically screws in and it'll tighten on this part.

**[15:32.17 - 15:34.84]** This is what the GoPro and the phone and stuff connect to.

**[15:35.60 - 15:37.94]** So then maybe this comes all the way out.

**[15:38.92 - 15:39.98]** This comes out.

**[15:40.14 - 15:44.00]** And now when you're doing this, you don't necessarily have to hold control to snap.

**[15:44.04 - 15:45.70]** In fact, I won't because I'm really going to just

**[15:46.46 - 15:47.12]** kind of eyeball it.

**[15:47.13 - 15:48.96]** I want it to visually look nice.

**[15:48.98 - 15:53.46]** It doesn't necessarily need to be, you know, exactly on a certain value.

**[15:54.32 - 15:58.34]** That's just handy when you're pulling everything apart so that you can get it back together properly.

**[15:58.40 - 16:04.25]** But this is kind of a nice, you know, you want to think a little bit about what your camera angle is going to be.

**[16:04.89 - 16:11.43]** But really today, I just want to focus on the actual animation, not so much the setup of everything else.

**[16:11.49 - 16:14.31]** So maybe this kind of comes out a little bit

**[16:15.73 - 16:17.21]** This comes out.

**[16:17.27 - 16:18.93]** Maybe this goes back a little bit.

**[16:19.77 - 16:20.39]** Bring that there.

**[16:21.39 - 16:24.91]** Something like that I think is working pretty decent for me.

**[16:24.98 - 16:27.92]** So those should have all had keyframes automatically inserted.

**[16:27.94 - 16:30.80]** So let's just make the whole thing just thirty frames.

**[16:31.40 - 16:32.18]** Press spacebar.

**[16:33.04 - 16:38.26]** And then bam, we got our exploded animation pretty much just like that.

**[16:38.40 - 16:39.26]** So working easily.

**[16:39.28 - 16:42.96]** If you wanted to have it come back together, let's just give ourselves some more frames.

**[16:43.04 - 16:45.00]** This is kind of an odd thing happening down there.

**[16:45.02 - 16:46.85]** It's kind of flashing.

**[16:46.87 - 16:49.71]** So I'm pressing C to circle select.

**[16:49.77 - 16:51.41]** And that's just selecting.

**[16:51.45 - 16:53.71]** Oh, I want to make sure I have all my objects selected.

**[16:54.45 - 16:56.49]** And then C to select all of those.

**[16:56.61 - 17:00.89]** Shift D. And then let's say maybe it only takes twenty frames to get back together.

**[17:00.93 - 17:02.05]** So our whole animation

**[17:03.01 - 17:05.61]** is, well, we'll leave it at sixty, so it kind of pauses for a second.

**[17:07.13 - 17:09.37]** So that's pretty much it for that.

**[17:09.61 - 17:11.49]** That's kind of how I would do an Explodive View animation.

**[17:12.13 - 17:15.38]** And this is obviously a little bit easier because it's just all linear animation.

**[17:15.84 - 17:23.22]** But if you want to add some detail to this, of course, these would technically screw in when they go up.

**[17:23.74 - 17:27.08]** There's no actual knurling on here, so you wouldn't really be able to see that.

**[17:27.52 - 17:34.87]** But you can add other little details like maybe this starts and ends with this rotation.

**[17:34.95 - 17:45.54]** And by the way, if you press I like we did earlier out here, but up in this field, it's going to insert it, but it'll just do it for the selected object, even if you have multiple selected.

**[17:45.99 - 18:14.51]** so let's have that start and finish at that eye and then maybe in the middle this whole thing kind of like rotates a little bit just to give it a little bit of interest now if we undo so let's just say yeah we're doing we're doing rotation now so let's go keying and do rotation so that didn't insert keyframes when I moved it because the active keying set was set to a location but just move that a tad and it'll automatically insert rotation keyframes

**[18:15.33 - 18:18.51]** So now that kind of just adding a little bit of interest there.

**[18:20.05 - 18:21.57]** Now, where else could we add some animation?

**[18:21.59 - 18:31.30]** We could actually add, you know, let's just, let's say at the beginning here, let's just go ahead and insert location keyframes for everything, or sorry, rotation keyframes.

**[18:31.38 - 18:39.02]** So with my keying set, set to rotation, just press I, and it should automatically insert all the keyframes for everything.

**[18:39.12 - 18:39.40]** Good.

**[18:39.96 - 18:41.00]** Now let's do it again down here.

**[18:41.02 - 18:43.15]** Oh, I only added three.

**[18:43.17 - 18:44.47]** I need to select everything, press I.

**[18:45.25 - 18:47.01]** OK, so now everything has a rotation keyframe.

**[18:47.03 - 18:52.11]** So maybe in the middle here, we can just let this all kind of go a little crazy.

**[18:52.29 - 18:54.75]** This will probably drive engineers wild.

**[18:54.81 - 19:03.28]** But let's just type F-three and search randomize transform, which will now open up this menu.

**[19:04.16 - 19:08.06]** which will allow me to randomize the rotation of everything just a little bit.

**[19:09.08 - 19:09.72]** Let me do that.

**[19:10.36 - 19:11.00]** Just kind of cool.

**[19:11.02 - 19:14.82]** And just of these selected pieces, I don't want there to be any clipping or anything.

**[19:14.88 - 19:19.48]** But now let's do, now with those selected, let's press I right there.

**[19:19.59 - 19:21.03]** And I should add all those keyframes.

**[19:21.69 - 19:24.87]** And since we had them on the front and the back, they should come right back together.

**[19:25.81 - 19:28.71]** Yeah, so just kind of a cool, cool thing.

**[19:29.19 - 19:32.07]** Now one last little detail that you might want to do with,

**[19:32.87 - 19:35.85]** You know, with this particular part, there's this little clip that goes in and out.

**[19:35.89 - 19:41.78]** So let's let's see if we can add maybe a shape key to simulate that clip depressing.

**[19:41.86 - 19:46.14]** So to add a shape key, what we're going to do is just hit this little plus sign right there.

**[19:46.50 - 19:52.40]** And now we'll add basically, you know, it'll remember the shape, you know, that shape as the basis.

**[19:52.44 - 19:56.86]** And then we do one more shape key and then we can just bring this little part down.

**[19:56.94 - 19:59.79]** So let's present all Z, by the way, to go into my

**[20:01.32 - 20:03.58]** X-ray view and then so I just selected one of these

**[20:04.10 - 20:11.92]** And then I want to, well, for one, we want to rotate this about sort of that curve right there.

**[20:12.02 - 20:19.70]** So I just selected two vertices, Shift S, cursor to selected, because that's about the axis where I want to rotate this whole part.

**[20:20.08 - 20:23.22]** And then I'm just going to select the top right here.

**[20:23.24 - 20:26.30]** And then Control plus will grow my selection.

**[20:27.46 - 20:32.85]** I'm just going to keep pressing that until it grows to maybe right about there is good.

**[20:33.42 - 20:35.68]** And then there's a couple of spots it didn't quite get.

**[20:35.72 - 20:38.36]** So let's circle select, add those.

**[20:39.98 - 20:41.66]** And yeah, it looks like I got a good amount there.

**[20:42.60 - 20:49.24]** And then what I'm gonna do is just press, uh, let's actually turn on proportional editing up here and select connected only.

**[20:49.96 - 20:55.21]** So now I can press R to rotate this and then let's rotate it about the three D cursor.

**[20:55.25 - 20:58.63]** So pressing period on my number pad or sorry, period on my keyboard.

**[20:59.33 - 21:00.89]** And then now I can kind of rotate that.

**[21:01.27 - 21:04.79]** So you can see there's this little clip that kind of fits into that slot there.

**[21:05.36 - 21:06.58]** And this is one thing that helps.

**[21:06.62 - 21:11.02]** Whenever you're working with somebody on this, you obviously need to talk about the model.

**[21:12.20 - 21:13.30]** So now I'll pull that down.

**[21:13.70 - 21:15.46]** And that's on my key one here.

**[21:15.48 - 21:20.02]** So now if I tab out of edit mode, we've got this little control that will adjust that.

**[21:20.50 - 21:22.42]** So maybe this whole animation, let's

**[21:23.61 - 21:24.95]** Let's actually pull out a graph editor.

**[21:24.97 - 21:27.44]** So up here, I want to go into my graph editor.

**[21:28.84 - 21:30.70]** And those are all the keyframes.

**[21:30.80 - 21:32.58]** For one, I'll normalize them.

**[21:33.51 - 21:34.37]** OK, so that's everything.

**[21:34.39 - 21:38.59]** A little bit confusing, but those are all our keyframes, so one to fifty.

**[21:39.01 - 21:46.10]** So maybe we have, for one thing, if you want to make this all a little bit longer, for example, maybe you want this to happen over a hundred and twenty frames.

**[21:46.62 - 21:53.18]** You can just press A to select everything up here and then G and you wouldn't want to move it like that.

**[21:53.20 - 21:53.76]** That's pretty cool.

**[21:53.78 - 21:56.64]** But just G and X to slide along the time frame.

**[21:57.35 - 21:59.37]** And now it's just going to create some space on either side.

**[21:59.41 - 22:02.85]** And I can press S and X to scale those out.

**[22:03.21 - 22:04.81]** And that's just going to make our animation happen.

**[22:05.71 - 22:07.79]** a little bit slower, which is nice.

**[22:07.95 - 22:11.96]** And now it will give us an opportunity to add in some frames for the shape key here.

**[22:12.02 - 22:14.74]** So that animation doesn't start right now until frame twenty five.

**[22:15.38 - 22:23.92]** So maybe at frame twenty five, we have this fully depressed insert keyframe and then we'll pull it back a little bit.

**[22:25.10 - 22:41.04]** and we'll have that back to zero and with my auto keying on it's automatically adding keyframe for me which that worked a little bit weird be careful using that auto keying sometimes you can accidentally insert keyframes when you don't want to so then let's have that um

**[22:41.74 - 22:44.98]** So it clips down, then maybe when it goes out, pops back up.

**[22:45.30 - 22:47.70]** Keyframe automatically inserted, pops out.

**[22:48.10 - 22:54.26]** And then maybe right there, we'll have it still up, but then go forward a few frames.

**[22:54.58 - 22:59.34]** We'll have it go down, insert keyframe, and then we'll have it kind of snap back up.

**[22:59.52 - 22:59.76]** Boom.

**[23:00.08 - 23:02.80]** So now we've got this cool open up, click.

**[23:02.98 - 23:04.78]** Just kind of a simple thing.

**[23:04.82 - 23:07.42]** Hopefully I showed you a few different tools you could use there.

**[23:07.84 - 23:09.42]** You know, since we animated the...

**[23:10.24 - 23:13.25]** Or since we changed the origin here, maybe we want to add a little bit of animation to that.

**[23:14.15 - 23:18.15]** Just so maybe right here, it's got a little, what would that be?

**[23:18.17 - 23:21.05]** The X, which means we would need to parent this.

**[23:21.11 - 23:23.49]** Control P, Object, Key Transform.

**[23:24.27 - 23:27.75]** And we didn't parent everything inside, so that might actually be a bad idea.

**[23:28.23 - 23:29.93]** But you could parent everything.

**[23:29.95 - 23:35.00]** And then, of course, if you wanted to move your whole object, I would recommend adding an empty.

**[23:35.58 - 23:37.08]** So Shift-A, add an empty.

**[23:38.08 - 23:39.14]** You can add whatever you want.

**[23:39.58 - 23:43.78]** And then you just want to parent all the other parents to the empty.

**[23:43.80 - 23:45.02]** And then you can move the empty around.

**[23:45.06 - 23:47.22]** But I'll leave that for you to figure out.

**[23:47.24 - 23:49.82]** Definitely, if you have any questions, let me know in the comments.

**[23:50.50 - 23:58.65]** But really the magic happens up here in the graph editor if you really want to smooth things out, change some things, and you can add in some dynamic effects here.

**[23:59.07 - 24:01.35]** This is probably going to look absolutely bonkers.

**[24:01.83 - 24:06.63]** Okay, so you probably don't want to do that, but let's see if we could...

**[24:06.65 - 24:08.28]** I'm pressing T, by the way, to bring these up.

**[24:09.32 - 24:20.36]** That's kind of cool the bounce effect But yeah, I'll do another tutorial sometime going more in-depth into the graph editor But uh yeah for the most part maybe just leave it on bezier Looks pretty good.

**[24:20.92 - 24:26.34]** But yeah, there's your basic CAD file to exploded view animation won't talk much about the

**[24:27.44 - 24:57.01]** actual rendering of this because it's going to be highly dependent on your own model but yeah that's kind of how i would go about taking a cad model splitting it up adjusting origins as needed and then adding animation to the different parts to kind of show it off this is something that people ask for a lot in the freelance projects i do but yeah hope you all enjoyed it thanks for watching definitely check out grav grip very cool product there is a new version available this is the old one and yeah thanks for watching i'll see you next time
