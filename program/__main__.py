# This program reads from your gcode file. As long as you've added your `; <repetition>` lines.
# TO USE ME:
# 1. Open your GCode file. Find where your repeating section of GCode starts and ends. This may be easiest to do by searching for `G1 Z...` lines.
# 2. Separate your GCode's contents such that there is, in order:
#   1. A "pre" repetition section containing all the gcode required before the main, repeating, body of gcode.
#   2. A line reading only `; <repetition>` (without the ` characters)
#   3. The gcode you wan't repeated
#   4. `; </repetition>`
#   5. A "post" repetition section which contains all of your normal the post-print gcode
#   6. If you're lucky, your slicer will let you add these tags to end-of-print and layer-change gcode scripts, and you never need to open your gcode file manually - eg, Simplify3D.
# 3. Edit the 2 initialization values below. They should be all you need. Numerical values are in mm, obviously.

print_height_per_repetition = 1.0  # The z-directional thickness per-repetition. Should be accurate to the (layer-height * layer-count) after slicing, *not* accurate to the STL (though your slicer will try to make these equivalent).
airgap_between_repetitions = 0.35  # The gap between repetitions. Tweak this to ensure relatively easy separation between clips, without damaging the first-layer quality of each individual clip.

# 4. If you want different filenames or stack counts, change the filenames below.
#   This script defaults to producing "test_stack.gcode" and "100_stack.gcode".
#   The "test" gcode file produces 3 repetitions including 4 of the automatically generated, repeating clips.
#   The "100_stack" gcode file makes 100 clips, once you're confident that the test produces good results.

gcode_file_i_want_read = "../gcode/surgical_mask_strap.gcode"
files_i_want_output = [
    ("../gcode/test_stack.gcode", 3),
    ("../gcode/100_stack.gcode", 100),
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
                print_progress(file, clip_number, count)

            gcode_out.writelines(gcode_in.readlines())
    print_done(file, count)


def print_progress(file_name, progress_count, total_count):
    prog_separation = int(progress_count / total_count * 66)
    finished_decoration = "\033[1;32;100m"
    file_desc = "{} into `{}`".format(total_count, file_name).ljust(66, '.')
    prog_desc = "{}/{}".format(progress_count, total_count).rjust(7, '.')
    full_desc = file_desc + prog_desc
    print("\r{}{}\033[0m{}".format(
        finished_decoration,
        full_desc[:prog_separation],
        full_desc[prog_separation:]
    ), end='')


def print_done(file_name, total_count):
    file_desc = "{} into `{}`".format(total_count, file_name).ljust(66, '.')
    prog_desc = "Done!".rjust(7, '.')
    print("\r{}".format(
        file_desc + prog_desc
    ))


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
    counts = [int(f[1]) for f in files_i_want_output]
    mm_per_rep = print_height_per_repetition + airgap_between_repetitions
    print("\n\
Repeating {} with [{}] repetitions of {:0.3f}mm each.\n\
\033[1mMax Z height: ~{:0.3f}mm\033[0m.\n".format(
            gcode_file_i_want_read,
            ', '.join([str(c) for c in counts]),
            mm_per_rep,
            (max(counts) + 1) * mm_per_rep
        ))
    for filename, stack_size in files_i_want_output:
        write_repeated_gcode(filename, stack_size)
    print("Everything's wrapped up - happy printing.")
