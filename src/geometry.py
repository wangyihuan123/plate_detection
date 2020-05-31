import cv2
import math
import numpy as np


def point_dist_from_plane(centroid, direction, point):
    v = [point[0] - centroid[0], point[1] - centroid[1], point[2] - centroid[2]]
    return direction.dot(v)


def normalize(vector):
    length = vector_length(vector)
    if length > 0:
        return vector / length
    else:
        return vector


def vector_length(vector):
    x = vector[0]
    y = vector[1]
    z = vector[2]
    return math.sqrt(x * x + y * y + z * z)


def points_centroid(points):
    p_sum = np.zeros(3)
    for point in points:
        p_sum += point

    centroid = p_sum * (1.0 / len(points))

    return centroid


def plane_from_points(points):
    if len(points) < 3:
        return None, None

    centroid = points_centroid(points)

    xx = 0.0
    xy = 0.0
    xz = 0.0
    yy = 0.0
    yz = 0.0
    zz = 0.0

    for p in points:
        r = p - centroid
        xx += r[0] * r[0]
        xy += r[0] * r[1]
        xz += r[0] * r[2]
        yy += r[1] * r[1]
        yz += r[1] * r[2]
        zz += r[2] * r[2]

    det_x = yy * zz - yz * yz
    det_y = xx * zz - xz * xz
    det_z = xx * yy - xy * xy

    det_max = max(det_z, det_y, det_x)

    if det_max <= 0.0:
        return None, None

    direction = np.zeros(3)
    if det_max == det_x:
        direction[0] = det_x
        direction[1] = xz * yz - xy * zz
        direction[2] = xy * yz - xz * yy
    elif det_max == det_y:
        direction[0] = xz * yz - xy * zz
        direction[1] = det_y
        direction[2] = xy * xz - yz * xx
    else:
        direction[0] = xy * yz - xz * yy
        direction[1] = xy * xz - yz * xx
        direction[2] = det_z

    return centroid, normalize(direction)


def axis_angles_from_normal(vector):

    pitch = math.asin(-vector[1])
    yaw = math.atan2(vector[0], vector[2])
    roll = 0.0  # no roll - ambiguous
    return pitch, yaw, roll


def bounding_box_from_points(points):
    x_coordinates, y_coordinates = zip(*points)
    x1, y1 = (min(x_coordinates), min(y_coordinates))
    x2, y2 = (max(x_coordinates), max(y_coordinates))
    return x1, y1, x2 - x1, y2 - y1


def plane_from_pointsV2(points):

    n = len(points)

    if n < 3:
        return None

    p_sum = np.zeros(3)
    for point in points:
        p_sum += point

    centroid = p_sum * (1.0 / n)

    xx = 0.0
    xy = 0.0
    xz = 0.0
    yy = 0.0
    yz = 0.0
    zz = 0.0

    for p in points:
        r = p - centroid
        xx += r[0] * r[0]
        xy += r[0] * r[1]
        xz += r[0] * r[2]
        yy += r[1] * r[1]
        yz += r[1] * r[2]
        zz += r[2] * r[2]

    xx /= n
    xy /= n
    xz /= n
    yy /= n
    yz /= n
    zz /= n

    weighted_dir = np.zeros(3)
    axis_dir = np.zeros(3)

    det_x = yy * zz - yz * yz
    axis_dir[0] = det_x
    axis_dir[1] = xz * yz - xy * zz
    axis_dir[2] = xy * yz - xz * yy
    weight = det_x * det_x

    if weighted_dir.dot(axis_dir) < 0.0:
        weight = -weight
    weighted_dir += axis_dir * weight

    axis_dir = np.zeros(3)
    det_y = xx * zz - xz * xz
    axis_dir[0] = xz * yz - xy * zz
    axis_dir[1] = det_y
    axis_dir[2] = xy * xz - yz * xx
    weight = det_y * det_y

    if weighted_dir.dot(axis_dir) < 0.0:
        weight = -weight
    weighted_dir += axis_dir * weight

    axis_dir = np.zeros(3)
    det_z = xx * yy - xy * xy
    axis_dir[0] = xy * yz - xz * yy
    axis_dir[1] = xy * xz - yz * xx
    axis_dir[2] = det_z
    weight = det_z * det_z
    if weighted_dir.dot(axis_dir) < 0.0:
        weight = -weight
    weighted_dir += axis_dir * weight

    return centroid, normalize(weighted_dir)


def distance(p1, p2):
    xSqr = (p1[0] - p2[0]) * (p1[0] - p2[0])
    ySqr = (p1[1] - p2[1]) * (p1[1] - p2[1])
    if len(p1) == 3 and len(p2) == 3:
        zSqr = (p1[2] - p2[2]) * (p1[2] - p2[2])
        return math.sqrt(xSqr + ySqr + zSqr)

    return math.sqrt(xSqr + ySqr)


def midpoint(p1, p2):
    return [
        (p1[0] + p2[0]) / 2.0,
        (p1[1] + p2[1]) / 2.0
    ]


def linePointAtMagnitude(p1, p2, magnitude):
    t = magnitude / distance(p1, p2)

    x = (1.0 - t) * p1[0] + (t * p2[0])
    y = (1.0 - t) * p1[1] + (t * p2[1])

    return (x, y)


def degToRad(degrees):
    return degrees * (math.pi / 180.0)


def pointsToEdges(points):

    count = len(points)
    edges = []

    for i in range(0, count):
        nextIndex = i + 1

        if nextIndex >= count:
            nextIndex = 0

        edges.append([
            points[i],
            points[nextIndex]
        ])

    return edges


# [[x, y], [x, y], [x, y], [x, y]]
def polygonCentroid2D(points):

    centroid = [0.0, 0.0]

    signedArea = 0.0

    x0 = 0.0
    y0 = 0.0
    x1 = 0.0
    y1 = 0.0
    pArea = 0.0  # Partial signed area

    numPoints = len(points)

    # Iterate over all the points except the last one
    for i in range(0, numPoints - 1):
        x0 = points[i][0]
        y0 = points[i][1]
        x1 = points[i + 1][0]
        y1 = points[i + 1][1]
        pArea = (x0 * y1) - (x1 * y0)
        signedArea += pArea
        centroid[0] += (x0 + x1) * pArea
        centroid[1] += (y0 + y1) * pArea

    # Do the last and the first manually
    x0 = points[numPoints - 1][0]
    y0 = points[numPoints - 1][1]
    x1 = points[0][0]
    y1 = points[0][1]
    pArea = (x0 * y1) - (x1 * y0)
    signedArea += pArea
    centroid[0] += (x0 + x1) * pArea
    centroid[1] += (y0 + y1) * pArea

    signedArea *= 0.5
    centroid[0] /= (6.0 * signedArea)
    centroid[1] /= (6.0 * signedArea)

    return centroid


def resizePolygon(polygon, factor):

    centroid = polygonCentroid2D(polygon)

    resized_polygon = []

    for point in polygon:
        new_x = (point[0] - centroid[0]) * factor + centroid[0]
        new_y = (point[1] - centroid[1]) * factor + centroid[1]
        resized_polygon.append([new_x, new_y])

    return resized_polygon


# center origin
def inflateRectangle(rec, ratio=1.1):
    x, y, w, h = rec
    mag = int(((w + h) / 2) * (ratio - 1.0))
    return (max(x - mag, 0), max(y - mag, 0), w + (mag * 2), h + (mag * 2))


# axis aligned only
def pointInBox(box, point):
    x1, y1, x2, y2 = box
    x, y = point

    if x1 <= x and x <= x2 and y1 <= y and y <= y2:
        return True

    return False


#      |
#      |
#      |
# -----+----->
#      |
#      |
#      v
def imageToCartesian(point, resolution):
    w, h = resolution
    ci_x = point[0] - (w / 2)
    ci_y = point[1] - (h / 2)
    return [ci_x, ci_y]


def cartesianToImage(point, resolution):
    w, h = resolution
    ci_x = point[0] + (w / 2)
    ci_y = point[1] + (h / 2)
    return [ci_x, ci_y]


def projectPoints(img_coords, model_points, points_to_project, res):
    """Project points from one plane to another. This is based on knowing some
       models coordinates in the image and projecting where another set of
       points on the model should be img_coords is an array of the image points
       corrosponing to the model_points model_points is the known model points
       of img_coords points_to_project are points relative to the model points
       that you want to projects onto the image plane described by the
       relationship between img_coords and model_points res is a tuple of
       (rows, columns) relative to the img_coords
    """
    ci_d_points = [imageToCartesian(point, res) for point in img_coords]
    H, status = cv2.findHomography(
        np.float32(model_points), np.float32(ci_d_points), 0, 1)
    new_points = cv2.perspectiveTransform(np.float32([points_to_project]), H)
    new_points = new_points[0]
    return [cartesianToImage(point, res) for point in new_points]
