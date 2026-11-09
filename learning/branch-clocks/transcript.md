# Transcript - How do Digital and Analog Clocks Work? (Branch Education)

Source: https://www.youtube.com/watch?v=oEC5fIw0bL0 - EngineX transcribe (large-v3, word-aligned). Single narrator (Phil Lee).

**[00:00.21 - 00:20.92]** Inside almost every piece of technology is a tiny clock that ticks at a rate of over a billion times a second, generating a digital heartbeat that is critical to regulating the execution of code, the movement of data in the processor and memory, the generation of wireless signals for transmitting data, and much more.

**[00:21.70 - 00:27.18]** So then, how do we generate a clock that precisely pulses at less than half a nanosecond?

**[00:28.72 - 00:43.79]** It might seem counterintuitive, but this billions of times a second heartbeat, or gigahertz clock signal, is incredibly similar to how a ten dollar analog wall clock ticks through the seconds, minutes, and hours of the day.

**[00:44.39 - 00:58.64]** In order to explore how a gigahertz technological heartbeat is generated, let's open a wall clock, see how it works, and then see how the same technology is used to produce your desktop computer's gigahertz clock signal.

**[00:59.10 - 01:00.70]** So let's jump right in.

**[01:10.13 - 01:15.36]** Inside this ten dollar wall clock are five unique systems that enable it to work.

**[01:17.10 - 01:21.12]** The most recognizable is the gear train made from eight gears.

**[01:21.70 - 01:30.44]** At the beginning of the gear train, a driver gear is rotated by an electromagnet, which provides the force to rotate the clock hands.

**[01:30.96 - 01:37.61]** This electromagnet is composed of a coil of wire, which uses electrical current to generate a magnetic field.

**[01:38.33 - 01:42.57]** and a strip of iron to channel that magnetic field to the drive gear.

**[01:43.23 - 01:58.16]** Every second, the electromagnet switches directions, thus causing the magnet inside the driver gear to rotate one hundred and eighty degrees in order to align its permanent magnet with the fields produced by the electromagnet.

**[01:58.56 - 02:03.29]** Therefore, the driver gear rotates fully around once every two seconds.

**[02:03.97 - 02:12.27]** Most of the gears in the gear train are composed of compound gears, each of which has two different gears, one on top of the other.

**[02:13.03 - 02:30.79]** To move the second hand, which is mounted on a shaft through the clock center, we go through a twelve to forty-eight gear reduction and then an eight to sixty gear reduction, thereby reducing one revolution every two seconds down to one every sixty seconds.

**[02:31.27 - 02:42.59]** The minute hand is also mounted on a shaft through the center and is driven through an eight to sixty-four gear reduction to the idler, followed by eight to sixty to the minute hand.

**[02:43.11 - 02:54.97]** And finally, the hour hand is driven via a fifteen to forty-five reduction to the idler and a ten to forty gear reduction to produce one rotation every twelve hours.

**[02:55.97 - 03:04.00]** As a result, we have three shafts rotating to which the hands of the clock are mounted, each rotating at different speeds.

**[03:05.32 - 03:07.88]** The last gear is used to set the time.

**[03:08.36 - 03:15.00]** And interestingly, this gear has thirteen teeth on it and rotates once every sixty-nine minutes.

**[03:15.64 - 03:20.91]** As in the name, the time setting gear directly rotates the minute and hour hands.

**[03:21.38 - 03:35.15]** However, the gear with the second hand doesn't move because the two parts of the compound gear slip from the high torque required to rotate the second hand, fifty-two times per rotation of the time setting gear.

**[03:35.79 - 03:37.46]** Now that we've covered the gear train,

**[03:38.18 - 03:45.94]** Let's dive into the quartz crystal oscillator and see what makes this clock nearly identical to the digital clock in your computer.

**[03:46.52 - 03:57.17]** Inside this metal cylinder is a quartz crystal tuning fork with wires printed onto the side, which travel along the legs to the outside of the metal canister.

**[03:58.11 - 04:02.84]** let's focus on a single side with wires printed on the left and right.

**[04:03.29 - 04:17.10]** Inside the quartz is a crystal lattice of one silicon for every two oxygen atoms, which forms a network of covalent bonds, with electrons being more attracted to the oxygen due to their electronegativity.

**[04:17.54 - 04:28.15]** When you cut a slice of quartz in a particular direction, you can see repeating sections of a crystal lattice with a hexagonal organization of oxygen and silicon.

**[04:28.53 - 04:43.82]** When a negative charge is applied to the printed wires, an electric field is directed to the crystal lattice, and the negatively charged oxygen atoms are pushed away, whereas the positively charged silicon is pulled towards the wire.

**[04:44.34 - 04:52.82]** The combined movement of all the oxygen moving away and the silicon moving towards the wire results in a lengthening of the crystal lattice.

**[04:53.46 - 05:01.19]** Conversely, when a positive charge is applied, oxygen moves toward the positive charge and the silicon away.

**[05:01.58 - 05:04.99]** And as a result, the crystal lattice shrinks in length.

**[05:05.33 - 05:15.28]** This lengthening and shrinking along the length of the crystal lattice, called a piezoelectric effect, causes the leg of this tuning fork to move back and forth.

**[05:16.21 - 05:26.26]** As mentioned before, when a voltage is applied, the tuning fork lengthens and bends outward, and when the voltage is turned off, the quartz bounces backwards.

**[05:26.72 - 05:39.91]** The crystal bounces back and forth, creating positive and negative voltages, with the frequency of oscillation being dependent on the orientation of the crystal lattice, as well as the shape and dimension of the cut crystal.

**[05:40.41 - 05:49.50]** The purpose of having two legs is to create a vibrational mode wherein the prongs vibrate and resonate together while the base doesn't move.

**[05:50.22 - 05:57.86]** Frequently, manufacturers add small amounts of metal to the ends of the crystal to tune it to the desired frequency.

**[05:58.40 - 06:06.91]** However, to get a crystal to continuously oscillate, a changing voltage needs to be repeatedly applied to the wires on the legs.

**[06:07.39 - 06:21.33]** Specifically, this voltage needs to match the movement of the crystal such that the peak positive voltage is aligned with the movement of the crystal in one direction and the opposite when the crystal moves in the other direction.

**[06:21.67 - 06:27.52]** Kind of like pushing a kid on a swing set when it's at its low point, but in both directions.

**[06:28.00 - 06:42.44]** To do that, we use an integrated circuit with an inverter to form a feedback loop and two capacitors to assist in the timing of the voltage from the inverter and feedback loop, thus producing a resonant movement in the crystal.

**[06:42.92 - 06:48.52]** This is a rather complicated circuit to fully explain, but here's one way of thinking about it.

**[06:48.94 - 06:56.12]** An inverter on its own flips the input from a one to an output of a zero and vice versa.

**[06:56.85 - 07:10.11]** However, if we loop an inverter back in on itself, depending on the physical design of the inverter, the output will continuously flip between one and zero, a few picoseconds per cycle.

**[07:10.73 - 07:16.01]** And if we add the crystal tuning fork and capacitors in the path of the feedback loop,

**[07:16.69 - 07:30.45]** then the flipping between one and zero and back is regulated by the geometry and movement of the prongs of the crystal oscillator tuning fork and the filling and emptying of the charges in both of the capacitors.

**[07:31.00 - 07:41.72]** For this wall clock, the time it takes is thirty point fifty-two microseconds per cycle, resulting in thirty-two thousand seven hundred and sixty-eight cycles per second.

**[07:42.30 - 07:49.30]** The signal is then fed to another section in the integrated circuit, where a binary counter counts each cycle.

**[07:50.02 - 08:01.90]** And after thirty-two thousand seven hundred and sixty-eight cycles, which takes one second, the signal is sent to the electromagnetic controller, telling it to flip the direction of the electromagnet.

**[08:02.20 - 08:10.35]** thereby rotating the driver gear around one hundred and eighty degrees and moving the hands of the clock forward by one second.

**[08:10.95 - 08:26.62]** One thing to note is that if your clock is either fast or slow, it's most likely because the crystal oscillator doesn't oscillate exactly at thirty-two point seven six eight kilohertz due to the geometry and incorrect resonant frequency of tines.

**[08:27.32 - 08:39.40]** These crystals typically have twenty parts per million accuracies, meaning it can gain or lose at most one point seven seconds a day or ten and a half minutes a year.

**[08:40.92 - 08:49.87]** As mentioned earlier, this wall clock is composed of a set of systems, with each falling under a different domain of science and engineering.

**[08:50.19 - 08:55.06]** These topics are rather complex and typically covered by college courses.

**[08:55.62 - 09:01.44]** But instead of paying thousands of dollars, there's a free and easy way to learn.

**[09:02.07 - 09:04.01]** And that's with this video's sponsor,

**[09:04.63 - 09:25.11]** brilliant.org brilliant reimagines how courses are taught instead of boring hour-long lectures or textbooks that put you to sleep brilliant uses fun and interactive modules with thousands of lessons from basics to advanced topics and new lessons added every month

**[09:25.63 - 09:38.27]** For example, in a single afternoon, you can learn about gear trains, then dive into oscillations and classical mechanics, followed by chemistry and understanding how batteries store energy.

**[09:38.87 - 09:45.36]** And finally, you can finish it up with an exploration of logic circuits and how computers work.

**[09:45.88 - 09:51.18]** Whatever your skill level, Brilliant customizes its content to fit your needs.

**[09:51.72 - 09:54.26]** and for you to learn at your own pace.

**[09:54.74 - 10:06.79]** For the fans of branch education, we recommend you check out their course on how technology works with lessons such as how GPS works or how computer memory works.

**[10:07.65 - 10:12.92]** We can't emphasize enough how important it is to be a lifelong learner.

**[10:13.26 - 10:21.86]** So, for the viewers of this channel, Brilliant is offering a free, thirty-day trial with access to all their thousands of lessons.

**[10:22.44 - 10:30.33]** Additionally, Brilliant is offering twenty percent off an annual subscription to the first two hundred people who sign up.

**[10:31.19 - 10:35.15]** Just go to brilliant.org slash branch education.

**[10:35.63 - 10:37.65]** The link is in the description below.

**[10:38.61 - 10:53.66]** Let's move on and see how smartphones and computers generate a clock between one to five gigahertz, which is thirty to one hundred and fifty thousand times faster than a single oscillation of this quartz crystal tuning fork.

**[10:54.14 - 10:59.93]** Let's look again at this inverter loop back upon itself and add two more inverters into the loop.

**[11:00.43 - 11:02.49]** thus creating a ring oscillator.

**[11:02.95 - 11:09.24]** Due to the odd number of inverters, the output rapidly oscillates between a one and a zero.

**[11:09.74 - 11:17.39]** These inverters can operate incredibly quickly and can easily reach the gigahertz frequency range and higher.

**[11:18.03 - 11:36.42]** However, the issue is that this ring oscillator's frequency is highly dependent on temperature, as well as the physical geometry and electrical properties of the transistors, and thus has a frequency range of plus or minus, or more, from the desired frequency.

**[11:36.84 - 11:46.68]** Therefore, to stabilize the output frequency of a ring oscillator to less than a few parts per million accuracy, we use a circuit called a phase locked loop.

**[11:47.22 - 11:51.62]** This is a complicated circuit, but here's the general idea of how it works.

**[11:52.46 - 11:54.62]** On the right, we have the ring oscillator.

**[11:55.29 - 12:07.30]** And when we add some additional circuitry, depending on the input voltage, the output frequency changes, and the ring oscillator is now called a voltage-controlled oscillator, or VCO.

**[12:07.82 - 12:14.26]** On the left, we have a sixteen megahertz crystal oscillator similar to the tuning fork crystal oscillator.

**[12:14.60 - 12:22.68]** But by changing the crystal's geometry and placing electrodes on the top and bottom, we get a crystal with a faster resonant frequency.

**[12:23.14 - 12:30.10]** And again, this crystal is placed in a feedback loop of its own to produce a stable resonant frequency.

**[12:30.66 - 12:39.97]** In the middle is a frequency and phase comparator that outputs a signal equal to the difference between the crystal and the voltage-controlled oscillator.

**[12:40.66 - 12:50.59]** Next, an integrator takes the output from the phase comparator and turns it into a steady voltage and uses it to drive the voltage-controlled ring oscillator.

**[12:51.31 - 13:06.82]** Finally, this frequency is fed back into the frequency and phase comparator, and as it is, the feedback loop will drive the ring oscillator to match and be identical to the output from the sixteen megahertz crystal oscillator loop.

**[13:07.24 - 13:18.07]** However, since we want to get, for example, a two point four gigahertz signal, which is one hundred and fifty times that of the sixteen megahertz crystal oscillator,

**[13:18.35 - 13:21.34]** We add a frequency divider into the feedback loop.

**[13:21.78 - 13:32.07]** This frequency divider is just like the one in the wall clock that took thirty two thousand seven hundred and sixty eight cycles per second and turned it into a one hertz signal.

**[13:32.69 - 13:35.89]** Rather now, we're dividing by one hundred and fifty.

**[13:36.47 - 13:43.88]** Next, the signal is sent to the frequency and phase comparator, which wants the two signals to be identical.

**[13:44.28 - 14:03.98]** However, by having them different, it outputs a signal which goes through the integrator, turning it into a steady voltage and driving the voltage-controlled oscillator up to a higher frequency, which will be exactly one hundred and fifty times that of the sixteen megahertz crystal, which is two point four gigahertz.

**[14:04.68 - 14:18.42]** Using this phase locked loop, we have an incredibly fast frequency generator producing a signal that is exactly one hundred and fifty times that of a reliably manufactured and temperature stable quartz crystal.

**[14:18.94 - 14:25.78]** Additionally, if we want to change the desired frequency, we have the binary counter divide by a different number.

**[14:26.40 - 14:30.93]** thus changing the amount the sixteen megahertz crystal is multiplied by.

**[14:31.49 - 14:41.31]** And in fact, all smartphones do this when not actively in use, in order to reduce the clock frequency of their processor and conserve battery life.

**[14:42.54 - 14:45.39]** That's pretty much it for clocks and crystal oscillators.

**[14:45.93 - 14:54.09]** One thing to note is that sometimes MEMS oscillators are used in smartphones to save space instead of crystal oscillators.

**[14:54.39 - 14:57.14]** And we'll dive into MEMS in a future episode.

**[14:57.82 - 15:08.88]** We believe the future will require a strong emphasis on engineering education, and we're thankful to all our Patreon and YouTube membership sponsors for supporting this dream.

**[15:09.52 - 15:15.49]** If you want to support us on YouTube memberships or Patreon, you can find the links in the description.

**[15:16.15 - 15:24.66]** This is Branch Education, and we create three-D animations that dive deeply into the technology that drives our modern world.

**[15:25.08 - 15:30.21]** Watch another Branch video by clicking one of these cards or click here to subscribe.

**[15:30.77 - 15:32.25]** Thanks for watching to the end.
