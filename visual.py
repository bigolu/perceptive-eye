import matplotlib.pyplot as plt
import numpy as np

def draw_line(start, dest, subplot, size=20, axis='z'):
    increment = [(dest[0]-start[0])/size, (dest[1]-start[1])/size, (dest[2]-start[2])/size]
    print("Start: "+str(start))
    for i in range(0, size):
        subplot.scatter(xs=start[0], ys=start[1], zs=start[2], c='green')
        print(start)
        # subplot.plot(start, ys=start[1], zs=start[2])
        start[0] += increment[0]
        start[1] += increment[1]
        start[2] += increment[2]


def draw_3d_square(start_bottom_corner, subplot, size=20):
   for i in range(0, size):
        for j in range(0, size):
            draw_line(
                start=[start_bottom_corner[0]+j, start_bottom_corner[1]+i, start_bottom_corner[2]],
                dest=[start_bottom_corner[0]+j, start_bottom_corner[1] +i, start_bottom_corner[2] + size],
                subplot=subplot,
                size=size
            )

