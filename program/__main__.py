# This program reads from your gcode file. As long as you've added your `
# TO USE ME:
# 1. Open your GCode file. Find where your repeating section of GCode starts and ends. This may be easiest to do by searching for `G1 Z...` lines.
# 2. Separate your GCode's contents such that:
#   1. A "pre" repetition section containing all the gcode required before the main, repeating, body of gcode.
#   2. A line reading only `; <repetition>` (without the ` characters)
#   3. The gcode you wan't repeated
#   4. `; </repetition>`
#   5. A "post" repetition section which contains all of your normal the post-pring gcode
# 3. Edit the 3 initialization values below. They should be all you need. Numerical values are in mm, obviously.

print_height_per_repetition = 1.1  # The z-directional thickness per-repetition. Should be accurate to the (layer-height * layer-count) after slicing, *not* accurate to the STL (though your slicer will try to make these equivalent).
airgap_between_repetitions = 0.35   # The gap between repetitions. Tweak this to ensure relatively easy separation between clips, without damaging the first-layer quality of each individual clip.

# 4. If you want different filenames or stack counts, change the filenames below.
# This script defaults to producing "stacking_clips_test.gcode" and "100_clips.gcode".
# The "_test" gcode file produces 4 repetitions including 4 of the automatically generated, repeating clips.
# The "100_clips" gcode file makes 100 clips, once you're confident that the test produces good results.

gcode_file_i_want_read = "../gcode/working_example.gcode"
files_i_want_output = [
    ("../gcode/stacking_clips_test.gcode", 4),
    ("../gcode/100_clips.gcode", 100),
]

# You likely don't need to change anything else, but feel free to monkey with the code below.

import re


def write_repeated_gcode(file, count):
    with open(file, "w") as gcode_out:
        with open(gcode_file_i_want_read, "r") as gcode_in:
            gcode_out.writelines(read_until(gcode_in, "<repetition>"))
            repetition_start_pos = gcode_in.tell()

            for clip_number in range(0, count):
                gcode_in.seek(repetition_start_pos)
                replace = build_replacement(clip_number)
                for line in read_until(gcode_in, "</repetition>"):
                    gcode_out.write(replace(line))

            gcode_out.writelines(gcode_in.readlines())


def read_until(i_file, until):
    while True:
        line = i_file.readline()
        if until in line:
            return None
        yield line


def build_replacement(clip_number):

    # Match all "G1 Z##.###...." lines, upper or lower case. Remembers the "G1 Z" segment, extract the "##.###" segment.
    pattern = r"([Gg]1 .*[zZ])([\d\.]+)"

    height_offset = clip_number * (print_height_per_repetition + airgap_between_repetitions)

    def format_line(line):
        match = re.search(pattern, line)
        if not match:
            return line

        # Swap the original Z-value out for the stacked-height version, change nothing else.
        return "{}{:.3f}\n".format(match.group(1), height_offset + float(match.group(2)))

    return format_line


if __name__ == '__main__':
    for filename, stack_size in files_i_want_output:
        write_repeated_gcode(filename, stack_size)
