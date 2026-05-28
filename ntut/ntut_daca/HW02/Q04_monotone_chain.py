# Design a reasonably efficient algorithm for computing the length of the shortest path between A and B. 
# Note that the path cannot cross inside the fenced area but it can go along the fence.

import math

def distance(p1, p2):
    # calcs the euclidean distance between two points
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def path_length(hull):
    # sums the lengths of all line segments in a chain
    return sum(distance(hull[i], hull[i+1]) for i in range(len(hull) - 1))

def cross(o, a, b):
    # 2D cross product to determine the turn direction 
    # + = counter clockwise
    # - = clockwise
    # 0 = collinear
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def shortest_path_around(A, B, P):
    # combine the A, B, and polygon vertices, then sort primarily by X, and then by Y
    points = sorted([A, B] + P)

    # make lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # make upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # return the shorter of the two paths
    return min(path_length(lower), path_length(upper))