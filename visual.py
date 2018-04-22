import numpy as np

big_cube = np.zeros((20, 20, 20), dtype=np.uint32)

def draw_line(start, dest, subplot, size=20, axis='z'):
    increment = [(dest[0]-start[0])/size, (dest[1]-start[1])/size, (dest[2]-start[2])/size]
    for i in range(0, size):
        subplot.scatter(xs=start[0], ys=start[1], zs=start[2], c='green')
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


def create_voxel_cube(subplot, size=20):
    #ma = np.ones(shape=(size, size, size))
    ma = np.zeros(shape=(size, size, size))
    return ma


def draw_voxel_cube(subplot, cube):
    subplot.voxels(cube, edgecolors="k")


def delete_voxel_line(start, dest, cube, length=50):
    result = []
    dest = np.array(dest)
    start = np.array(start)
    for j in range(50):
        diff = ((dest-start)/50)*j
        r = np.int32(np.round(diff+start))
        result.append(r)
        cube[r[0]][r[1]][r[2]] = 0
        if j is 49:
            cube[r[0]][r[1]][r[2]] = 1


def get_voxel_map(camera, list_of_points, length=50):
    global big_cube
    camera = np.array(camera)
    list_of_points = np.array(list_of_points)
    for j in range(len(list_of_points)):
        delete_voxel_line(start=camera, dest=list_of_points[j], cube=big_cube)
    ncube = np.ndarray.flatten(big_cube)
    # the first result (cube) is the 3d cube, the second (ncube) is the 1d array
    return ncube

# Here is some example code for how to run it
'''
# Starting up matplotlib
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')


ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')
s = [0,0,0]


# draw_3d_square(start_bottom_corner=s, subplot=ax)
print("Finished computation")


# draw_voxel_cube(subplot=ax)
c = create_voxel_cube(subplot=ax)
for i in range(5):
    delete_voxel_line(start=(0, 10, 0), dest=(5, 5+i, 5), subplot=ax, cube=c)


draw_voxel_cube(subplot=ax, cube=c)


plt.show()
'''
