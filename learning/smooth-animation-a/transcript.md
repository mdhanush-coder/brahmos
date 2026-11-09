# Transcript - The SECRET to Smooth Blender Animations - Easing & Graph Editor (ArtSyndrom3)

Source: https://youtu.be/4Mf2hgb1tP0  
Transcribed with EngineX `transcribe/transcribe` (large-v3, word-aligned). Single speaker (narrator), so no speaker labels.

**[00:00.09 - 00:03.52]** So here's a really simple animation in Blender but it looks like trash.

**[00:04.04 - 00:06.58]** But how can we make it look cool, smooth and professional?

**[00:06.92 - 00:11.14]** Well it all comes down to easing which controls the speed of your object's moment.

**[00:11.42 - 00:17.15]** So in this Blender Essentials tutorial we're gonna learn all about easing using the Graph Editor in Blender.

**[00:17.83 - 00:22.59]** So here in Blender, we have a really simple animation of this clock rotating and going up.

**[00:22.93 - 00:24.45]** Currently, we are in the Dope Sheet.

**[00:24.75 - 00:28.96]** So to quickly switch to the Graph Editor, all you need to do is press Control Tab.

**[00:29.56 - 00:34.16]** For the animation, the starting pointer is called In and the ending pointer is called Out.

**[00:34.76 - 00:37.68]** So now, let's talk about the big three of Easy.

**[00:38.24 - 00:49.85]** When we want to make change to any of a keyframe, the easiest way is to go back to the doobchir, select the keyframe and then switch back using control tab and then in the graph editor everything will be selected.

**[00:50.41 - 00:56.44]** Now I'm gonna press S and X to scale this keyframe here and as you can see the graph is increasing.

**[00:56.86 - 01:01.18]** So this animation is called the ease out animation with a smooth ending.

**[01:02.04 - 01:27.16]** similarly we can select the first keyframe press s and x to increase the keyframe in the front as well and this creates a ease in our animation which creates a quick whip like animation now similarly i'm gonna press ctrl z to go back and we can select the first keyframe increase it by using the scale again and this will create just the ease in animation having a slow start and ending quickly

**[01:27.60 - 01:32.80]** So now with the big three out of the way let's talk about how duration can change the easing.

**[01:32.82 - 01:35.20]** Here I use the G key to move the keyframe back.

**[01:35.88 - 01:38.96]** Now we can increase the easing by increasing the scale here.

**[01:39.50 - 01:44.61]** As you can see the motion is much slower now and creates a much smoother animation.

**[01:45.12 - 01:50.55]** But if we bring the same keyframe closer together even though a smooth animation it'll be really quick.

**[01:51.15 - 01:54.05]** Now let's see how we can make transition using the easing.

**[01:54.45 - 02:02.28]** So here I'm gonna select the first keyframe and increase it to be almost full and the ending keyframe we can scale it down to be almost zero.

**[02:02.72 - 02:08.26]** Now if we play the animation you can see it creates a really slow start with a quick ending.

**[02:08.74 - 02:11.14]** So using this principle we're gonna create a transition.

**[02:11.62 - 02:16.97]** Here I have a really basic setup switching from one camera to another going from left to right.

**[02:17.45 - 02:21.99]** But here if I play the animation without any easing applied to it, it looks really basic.

**[02:22.49 - 02:29.44]** So to make a cool transition out of it, we're gonna select the first keyframe of the first camera and increase it to be almost full.

**[02:30.06 - 02:34.14]** Then the ending point of the first camera and scale it down to be almost zero.

**[02:34.78 - 02:42.87]** Similarly we have to match the starting point of the second camera and make it almost zero and then increase the ending to be full.

**[02:43.43 - 02:48.91]** So it's going from a quick ease in to ease out animation switching from one camera to another.

**[02:49.37 - 02:54.09]** And as you can see it creates a quick motion helping in creating a cool transition.

**[02:54.55 - 03:00.35]** Now finally to make everything easier we have this Easer plugin which you can get from Blender Extension.

**[03:00.99 - 03:10.14]** Once you have installed the plugin you can press the N key to open the side panel and the Easer plugin will be available there with all the different type of easing presets.

**[03:10.60 - 03:14.68]** Now to use it go to graph editor and press A to select all the keyframes.

**[03:15.18 - 03:18.95]** And then here for example I'm gonna use the super smooth preset.

**[03:19.37 - 03:25.03]** Now if I play the animation it's already adjusted the easing for us to create a smooth animation.

**[03:25.37 - 03:28.60]** You can play around and switch between these other fun preset as well.

**[03:28.88 - 03:33.88]** Like here I'm using the overshoot and the spring preset to create cool and fun animation.

**[03:34.36 - 03:41.03]** so this completes our quick easing tutorial if you learned something new please like and subscribe and i'll see you in the next one
