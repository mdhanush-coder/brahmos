# Transcript - How to Make Smooth Camera Animations in Blender (Blender To Browser)

Source: https://www.youtube.com/watch?v=dFK3C83k4Wo  
Transcribed with EngineX `transcribe/transcribe` (large-v3, word-aligned). Single speaker (narrator), so no speaker labels.

**[00:20.86 - 00:23.26]** Alright, so let's start by grabbing a model.

**[00:23.68 - 00:26.11]** I'm gonna use BlenderKit, but you can use any model.

**[00:26.66 - 00:30.59]** Now that we have our model, let's create an infinite backdrop.

**[00:31.29 - 00:35.29]** Add a plane, then extrude the back edge and simply bevel it.

**[00:36.27 - 00:44.08]** And by the way, make the scale a bit larger, so it covers the whole scene, because when we move the camera around, it might go out of the frame.

**[00:45.00 - 01:12.94]** and i'm just going to split the window so i can see the timeline more clearly now this is where the main part begins i'm going to add a camera and place it in front of the chair so so the chair comes in the center for this entire animation i'll keep the focal length at but you can use whatever works for you once that's done i'll highly recommend organizing your scene by naming everything properly

**[01:13.72 - 01:18.30]** Since I'm only using this camera for the first shot, I'll name it short one.

**[01:20.00 - 01:27.20]** Also, let's put this camera into a collection, so you can name it whatever you like, but I'll go with short one.

**[01:28.34 - 01:38.43]** For the camera moments, I won't rely too much on the camera itself, instead I'll add an empty, name it whatever I like, and place it in the short one collection.

**[01:39.73 - 02:05.60]** now since we want the camera to move around the model i'm not going to rotate the camera directly instead i'll parent it to the empty so when i rotate the empty the camera follows in a nice circular motion which is exactly what we want all right let's start with the first shot we begin with an entry animation where the camera slowly moves toward the subject to reveal the product

**[02:07.08 - 02:11.56]** Then the exit animation kicks in and that's where we transition to the next shot.

**[02:12.44 - 02:18.43]** Since we already have the end position, I will move the playhead to around frame forty or fifty.

**[02:18.84 - 02:22.73]** Then hover over the location and press I to add a keyframe.

**[02:23.01 - 02:24.79]** You can also use K if you prefer.

**[02:25.19 - 02:31.83]** Then I will go back to frame one, pull the camera slightly backwards, and add another keyframe.

**[02:33.01 - 02:35.16]** And honestly, it already looks pretty good.

**[02:37.75 - 02:46.42]** Now for the exit animation, since the movement starts slowly, I'll begin it a bit earlier around frame forty, and add a rotation keyframe.

**[02:47.34 - 02:56.87]** I'll keep the duration around fifteen frames, so I'll move fifty fifth, increase the Z rotation by about thirty degrees, and insert another keyframe.

**[02:58.85 - 03:03.41]** All right, this looks good to me, so I will move over to the graph editor.

**[03:03.96 - 03:08.22]** Then I will lock the X and Y axis so they don't interfere.

**[03:08.52 - 03:13.81]** And to make the graph easier to work with, you can press normalize and then hit home on your keyboard.

**[03:14.51 - 03:20.09]** After that, I will select these two handles in the graph and scale them along the X axis.

**[03:20.99 - 03:25.50]** Then I will play the animation and adjust the handle based on what looks good.

**[03:26.24 - 03:31.98]** By the way, if you scale them too much, the motion becomes too fast and it's all about finding the right balance.

**[03:35.74 - 03:40.78]** Now I think fifteen frames is a bit too short, so I will increase it to twenty frames.

**[03:44.59 - 03:49.75]** And I feel like thirty degrees is a bit too low, so I'm going to push it up to forty degrees.

**[03:54.24 - 03:56.52]** Now let's start working on the second shot.

**[03:57.18 - 04:02.73]** I will duplicate both the empty and the camera then move the empty to the next focus area of the model.

**[04:05.15 - 04:11.16]** Also don't forget to rename the empty and the camera and move them into a new collection called shot two.

**[04:13.99 - 04:19.25]** Also the camera currently has the same keyframes as shot one, so I'm going to delete them as well.

**[04:20.23 - 04:24.01]** Now I want to write down some values to keep my animation consistent.

**[04:25.19 - 04:27.93]** And it will also help speed up my workflow.

**[04:29.24 - 04:31.96]** Alright, so here are the main values I'll be using.

**[04:32.52 - 04:36.23]** First, the rotation for each transition, which is forty degrees.

**[04:37.13 - 04:40.63]** Second, the duration of each transition, which is twenty frames.

**[04:41.27 - 04:45.55]** And third, when the transition starts, which is after forty frames.

**[04:47.04 - 04:50.84]** Alright, let's delete the previous keyframes and start with the new one.

**[04:52.75 - 05:03.29]** Now to switch between cameras, we need to find the point where the motion is the fastest, which is usually right in the middle between the keyframes in shot one.

**[05:04.19 - 05:14.05]** So I will place the playhead at the middle around frame fifty, select the shot two camera and press control plus B to assign it.

**[05:15.47 - 05:19.77]** Then I will go back to frame one and assign the shot one camera as well.

**[05:21.17 - 05:41.89]** now if you play the animation you can see the cameras are switching perfectly now based on my notes i should be using a rotation of forty degrees but that value was for the exit animation and since we are working on the entry animation i'll use the negative forty instead

**[05:43.65 - 05:52.14]** After that, the short transition starts at frame forty, so I will place the playhead at frame forty and insert a rotation keyframe.

**[05:53.12 - 06:01.87]** Since the transition lasts twenty frames, I will move forward to frame sixty and reset the rotation back to zero, and insert another keyframe.

**[06:03.53 - 06:29.00]** now it's time for the graph editor luckily i have a free add-on called relative ease which lets you copy and paste easing really easily and you can use it too so i will just copy the easings from shot one and paste it into shot two now if you play the animation you can see the transition between the two cameras is much smoother

**[06:32.54 - 06:36.92]** Now let's add another note, which is the duration of a single shot.

**[06:38.14 - 06:42.13]** After that, we don't want the animation to stop after the transition.

**[06:42.93 - 06:44.37]** We want it to keep moving.

**[06:45.03 - 06:52.05]** So what I'll do is continue the rotation until the next transition starts, which is after forty frames.

**[06:52.53 - 06:57.97]** So I will go to frame ninety and add another keyframe with a rotation of ten degrees.

**[07:00.98 - 07:04.34]** Alright, so the animation continues even after the transition.

**[07:05.11 - 07:07.20]** Next, let's work on the exit animation.

**[07:08.15 - 07:12.27]** Looking at the nodes, we just need to add another keyframe, twenty frames later.

**[07:13.43 - 07:21.69]** Since the transition requires forty degrees of rotation, and we already have ten degrees, I'll add forty more, bringing it to a total of fifty degrees.

**[07:22.53 - 07:25.67]** Now in the graph editor, I'll just copy and paste the easings.

**[07:28.53 - 07:32.85]** Now if you play the animation, you can see that the flow isn't smooth.

**[07:39.32 - 07:43.64]** There's a literal bump right after the transition which is because of the graph editor.

**[07:44.52 - 07:48.92]** To fix that and make the animation smoother, we need to remove that bump.

**[07:49.90 - 07:55.39]** So, I will select the middle point of the handles and rotate it until the bump disappears.

**[08:00.92 - 08:23.66]** now if i play the animation from the start you can see that it's much smoother than before from here i'll speed up the process since i have already explained the enter animation exit animation easing and everything else now we just need to repeat these steps

**[08:25.13 - 08:32.11]** First, I will duplicate the camera and the empty, then rename them to short three and place them into a new collection called short three.

**[08:33.99 - 08:38.55]** After that, I will duplicate all the keyframes and position the empty where I want the focus.

**[08:39.51 - 08:43.45]** Then I will assign the camera fifty frames after the last camera switch.

**[08:44.19 - 08:49.49]** Next, I will add keyframes for the entry animation with a rotation of negative forty degrees.

**[08:50.21 - 08:52.13]** Then I will copy and paste the easings.

**[08:53.32 - 09:00.08]** After that, I will add an extra ten degrees of rotation so the motion continues even after the transition.

**[09:00.60 - 09:05.62]** Then I will add another keyframe for the exit animation and apply easing to this part as well.

**[09:06.31 - 09:10.93]** Finally, I will smooth out the animation and that's it for the shot three.

**[09:19.01 - 09:24.29]** Now for the animation showcasing the back of the model, I won't rotate the model in this scene.

**[09:24.57 - 09:29.73]** Instead, I'll click this button and use full copy to create a duplicate of this scene.

**[09:30.91 - 09:35.17]** Now you can rotate the model here and continue with the same steps we just learned.

**[09:35.88 - 09:43.22]** Now what I'll do is speed up the tutorial since you just need to change the position of the empties from the previous shots.

**[09:44.02 - 09:47.96]** There is no need to delete or add anything, just move the empties.

**[10:06.50 - 10:15.37]** Lastly, once you are done with everything here, you can copy the full scene again and create another shot showcasing the front of the model one last time.

**[10:44.65 - 10:53.43]** Now I just realized that I forgot to add lights, so I'll quickly add an area light on the right side of the scene and increase the intensity.

**[10:53.93 - 10:54.89]** Nothing fancy here.

**[11:07.24 - 11:11.66]** Then I'll just duplicate the same light and position it on the left side of the model.

**[11:14.01 - 11:18.13]** And I don't want this light to affect the shadows, so I'll link it to the model only.

**[11:23.04 - 11:26.82]** And you can also just copy the lights and paste them into the other scenes.

**[11:31.36 - 11:35.23]** And then you can comment down below and subscribe to the channel if you like.

**[11:35.71 - 11:37.67]** And that's it for this tutorial.

**[11:38.13 - 11:39.07]** I hope you liked it.
