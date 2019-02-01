from collections import OrderedDict
from math import log, sqrt

import numpy
import pandas as pd
from six.moves import cStringIO as StringIO

import bokeh.palettes
from bokeh.plotting import figure, show, output_file

# read in reads
reads = []
animals = set([])
tubes = {}
with open("reads.csv", "r") as f:
    for l in f:
        ts = l.strip().split(",")
        timestamp, animal_id, tube_id = float(ts[0]), ts[1], int(ts[2])
        animals.add(animal_id)
        if tube_id not in tubes:
            tubes[tube_id] = {}
        tubes[tube_id][animal_id] = tubes[tube_id].get(animal_id, 0) + 1
        reads.append([timestamp, animal_id, tube_id])

animals = sorted(list(animals))
animal_colors = bokeh.palettes.viridis(len(animals))
#animal_colors = [
#    bokeh.palettes.Viridis256[i] for i in
#    numpy.linspace(0, 255, len(animals)).astype('int')]

max_reads_per_tube = max([max(t.values()) for t in tubes.values()])


width = 800
height = 800
inner_radius = 90
outer_radius = 300 - 10

minr = 0
maxr = numpy.ceil(max_reads_per_tube / 1000.) * 1000.
a = (outer_radius - inner_radius) / (maxr - minr)
b = inner_radius - a * minr

def rad(mic):
    return a * mic + b
    #return a * numpy.sqrt(np.log(mic * 1E4)) + b

big_angle = 2.0 * numpy.pi / len(tubes)
small_angle = big_angle / (len(animals) + 1)

p = figure(plot_width=width, plot_height=height, title="",
    x_axis_type=None, y_axis_type=None,
    x_range=(-420, 420), y_range=(-420, 420),
    min_border=0, outline_line_color="black",
    background_fill_color="#ffffff")

p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

# annular wedges (1 per tube)
angles = numpy.pi/2 - big_angle/2 - numpy.arange(len(tubes))*big_angle
#colors = [gram_color[gram] for gram in df.gram]
#colors = '#f2fedc'
colors = '#f1e6e0'
p.annular_wedge(
    0, 0, inner_radius, outer_radius, -big_angle+angles, angles, color=colors,
)

# circular axes and lables
nlines = int(maxr / 1000) + 1
labels = numpy.linspace(0, maxr, nlines)
radii = a * labels + b
p.circle(0, 0, radius=radii, fill_color=None, line_color="#c8a48c")
p.text(0, radii, [str(int(r)) for r in labels],
       text_font_size="10pt", text_align="center", text_baseline="middle")
#p.text(0, [radii[-1], ], [str(int(labels[-1])), ],
#       text_font_size="8pt", text_align="center", text_baseline="middle")

# small wedges (per animal)
for (aid_i, aid) in enumerate(animals):
    values = numpy.array([tubes[i].get(aid, 0) for i in range(len(tubes))])
    small_angle_offset = aid_i + 0.5
    p.annular_wedge(0, 0, inner_radius, rad(values),
                    -big_angle+angles+small_angle_offset * small_angle,
                    -big_angle+angles+(small_angle_offset + 1) * small_angle,
                    color=animal_colors[aid_i])

# radial axes
p.annular_wedge(0, 0, inner_radius-10, outer_radius+10,
                -big_angle+angles, -big_angle+angles, color="black")

# tube labels
ts = numpy.arange(0, len(tubes), dtype='f8') / len(tubes) * numpy.pi * 2.
r = inner_radius - 12
txs = numpy.sin(ts) * r
tys = numpy.cos(ts) * r
p.text(
    txs, tys, [str(i) for i in range(len(tubes))],
    text_font_size="9pt", text_align="center", text_baseline="middle")

# draw out path for each animal
radius = inner_radius - 20
for (aid_i, aid) in enumerate(animals):
    ts = numpy.array([r[2] for r in reads if r[1] == aid], dtype='f8')
    ts /= len(tubes)
    ts *= numpy.pi * 2.
    # convert tubes to xys
    r = radius - aid_i * 2
    xs = numpy.sin(ts) * r
    ys = numpy.cos(ts) * r
    p.line(xs, ys, color=animal_colors[aid_i], line_width=1, line_alpha=0.3)
                
output_file("reads_per_tube.html", title="blockparty reads per tube")

show(p)