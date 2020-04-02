## GCode stacking program, or "I wish these mask-clips printed in bulk"

This will, with direction from you, **repeat parts in the Z-axis** up to however many repetitions you desire. It will accept arbitrary gcode, as long as the user has added repetition tags to said gcode, and will copy/paste the repeated gcode at incrementing layer heights. The repetition count, and layer-height per repetition, are also defined by the user via manual edit. 

**Warning 1**: This program may damage your printer. It _does not understand gcode_, and it _does not understand printers_. It will happy generate gcode which exceeds your Z limit, unless you calculate an appropriate repetition count. (Correct here is `height_per_layer` * **`repetition_count`** + `like 5mm of buffer margin?` < `z-limit` )

**Warning 2**: Stacking your parts will add curling-edges to the list of things to worry about: tall prints curl edges, and stacked parts are no exception.

**Warning 3**: This is not intended for newbies; to stack parts successfully, you'll need to reason your way through slicing details, and understand how to diagnose bridging issues. 


### Prerequisites:
* You have python installed (ideally Python3.x, but Taylor can make this compatible with Python2).
* You've copied at least `./program` and `./gcode` into a working directory. Easiest to clone everything.
* You have your favorite slicer ready.
* You have a good tool to pry apart loosely-bonded parts.
* Your 3D printer uses standard RepRap firmware style gcode. The author doesn't know of printers not using this style.
   * ... Or, you know enough Python to edit the included program to target your firmware's equivalent of `M1 Z...` commands.


### Steps to use:
1. Get a mask-clip model which stacks well. Model should be constant thickness, flexible enough to act as a strap, and robust enough to last under tension.
   * You can use the included `./stl/surgical_mask_strap_low`. Full disclosure, Taylor Deith made this by ditching conformity to achieve stacking/strength/flexibility/comfort. This design has been popular so far with care workers.
2. Get that model into your favorite slicer
3. Decide on the airgap you want between prints to ensure easy peal-ability parts. Rule of thumb for Taylor: `airgap = layer-height * 1.5`
4. **If you have first-layer effects you want removed from the repetition:** Place the model twice, one instance directly on top of the other, with the appropriate airgap between them.  
5. Slice that mask-clip model to:
   1. Print at a slower speed, and low temperature for (at least) the first layer of the part. It's wise to use whichever settings you use for bridging.
   2. Have a quick-print speed at high temperature for all the non-bridge layers, for maximum throughput.
   3. These distinct settings are made possible by (at least): 
      1. Using multiple processes in Simplify3D
      2. Using modifier boxes in PrusaSlicer
6. Copy your sliced model to `./gcode`.
7. Open `./program/__main__.py`. **Read and follow the instructions**.
   * The program **needs** to know which gcode file to read. Target it with `gcode_file_i_want_read`.
   * The program **wants** to know which gcode file(s) you want to output to, and how many repetitions each file contains - change these with `files_i_want_output`.
      * It's important to set the repetitions such that you won't exceed your printer's Z-stop.
      * The default is `./gcode/stacking_clips_test` with four repetitions, and `./gcode/100_clips` with a mysterious number of repetitions.   
   * There are two numbers you **need** to adjust, since the program needs to know about the total thickness of each repeating part in gcode.
   * There are two lines you **need** to add to your sliced gcode, since the program needs to know which segment of the gcode repeats.
      * The program identifies the start of this repeating section with a `; <repetition>` line in the gcode.
      * The program identifies the end of this repeating section with a `; </repetition>` line in the gcode.
      * You need to place these repetition tags manually. Searching the text for for `M1 Z`, or `layer` should help you find the appropriate spots.   
      * Look at `./gcode/working_example.gcode`. for what Taylor Deith actually used for his repetition.
8. Open a terminal in `./program`, and run `python3 .` or `python .` (or otherwise run Python against the program.)
9. Wait for completion, and print away!
   * You'll find the output files in `./gcode`. 
   * The program defaults to giving you a test file (with four repeats of the stack) and a production file (with 100 stacks). 
   * You'll want to verify that everything's gone smoothly by printing the test stack - other than the number of repetitions, the two files are identical; quality in the test print translates to quality in the production print.
    
    
### License
All included models and software provided under [DBAD] public license. 

[DBAD]: https://github.com/philsturgeon/dbad/blob/master/LICENSE.md
