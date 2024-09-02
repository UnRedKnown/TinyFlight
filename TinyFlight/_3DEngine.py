import math
import random
from PerlinNoise import PerlinNoise


import pygame
class Clipping():
    def __init__(self, WIDTH, HEIGHT):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

    def point_in_triangle(self, p, p0, p1, p2):
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

        b1 = sign(p, p0, p1) < 0.0
        b2 = sign(p, p1, p2) < 0.0
        b3 = sign(p, p2, p0) < 0.0

        return ((b1 == b2) and (b2 == b3))

    def angle_sort(self, points):
        if not points:
            return []
        # Find the center of the points
        center = [sum([p[0] for p in points]) / len(points),
                  sum([p[1] for p in points]) / len(points)]

        # Define a custom comparison function based on the angle
        def compare(p1, p2):
            angle1 = math.atan2(p1[1] - center[1], p1[0] - center[0])
            angle2 = math.atan2(p2[1] - center[1], p2[0] - center[0])
            return angle1 - angle2

        # Sort the points based on the angles
        sorted_points = sorted(points, key=lambda p: compare(p, [0, 0]))

        return sorted_points

    def checkIn(self, point):
        if point[0] >= 0 and point[1] >= 0 and point[0] <= self.WIDTH and point[1] <= self.HEIGHT:
            return True

    def intersection_point(self, line1, line2):

        slope1, intercept1 = self.line_equation(*line1)
        slope2, intercept2 = self.line_equation(*line2)

        if slope1 == slope2:
            return None

        x_intersect = (intercept2 - intercept1) / (slope1 - slope2)
        y_intersect = slope1 * x_intersect + intercept1

        if -0.01 < x_intersect < 0.01:
            x_intersect = 0

        if self.WIDTH - 0.01 < x_intersect < self.WIDTH + 0.01:
            x_intersect = self.WIDTH

        if self.HEIGHT - 0.01 < y_intersect < self.HEIGHT + 0.01:
            y_intersect = self.HEIGHT

        return x_intersect, y_intersect

    def line_equation(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        X = (x2 - x1)
        Y = (y2 - y1)
        if X == 0:
            X = 0.00001
        if Y == 0:
            Y = 0.00001
        slope = Y / X
        intercept = y1 - slope * x1
        return slope, intercept
class Engine():

    class Math():
        def __init__(self,engine):
            self.engine = engine

        def giveColor(self,):
            pass

        def Translation(self, point, pos):
            x, y, z = point
            x += pos[0]
            y += pos[1]
            z += pos[2]
            return x, y, z

        def Rotation(self, point):
            x, y, z = point
            x, z = self.__rotate2D((x - self.engine.pos[0], z - self.engine.pos[2]), self.engine.rot[1])
            y, z = self.__rotate2D((y - self.engine.pos[1], z), self.engine.rot[0])
            x, y = self.__rotate2D((x, y), self.engine.rot[2])
            return [x, y, z]

        def __rotate2D(self,pos, rad):
            x, y = pos
            s, c = math.sin(rad), math.cos(rad)
            return x * c - y * s, y * c + x * s

        def Projection(self, point):
            x, y, _ = point
            # if point[2] < 0:
            #     if point[2] > 0.01:
            #         z = point[2]
            #     else:
            #         z = 0.01
            # else:
            #     if point[2] != 0:
            #         z = point[2]
            #     else:
            #         z = 0.01
            z = point[2]
            if z <= 0:
                z = 0.00001
            f = self.engine.fov / z
            x, y = x * f, y * f
            return x, y, z



        def rotate(self, pos, angles, origin=(0, 0, 0)):
            x, y, z = [p - o for p, o in zip(pos, origin)]
            cx, cy, cz = [math.cos(math.radians(a)) for a in angles]
            sx, sy, sz = [math.sin(math.radians(a)) for a in angles]

            y, z = y * cx - z * sx, y * sx + z * cx  # Rotate around x-axis
            x, z = x * cy + z * sy, -x * sy + z * cy  # Rotate around y-axis
            x, y = x * cz - y * sz, x * sz + y * cz  # Rotate around z-axis

            x, y, z = [p + o for p, o in zip((x, y, z), origin)]
            return [x, y, z]

        def calculateDis(self, points, poly):
            for poly1 in poly:
                polys = poly[poly1]
                for p in polys:
                    x, y, z = self.__find_centroid([points[o] for o in p[:3]])
                    self.engine.dist.append([abs(math.sqrt(
                        (self.engine.pos[0] - x) ** 2 + (self.engine.pos[1] - y) ** 2 + (self.engine.pos[2] - z) ** 2)),
                                             poly[poly1].index(p), poly1])

        def __find_centroid(self, vertices):
            x_coords = [vertex[0] for vertex in vertices]
            y_coords = [vertex[1] for vertex in vertices]
            z_coords = [vertex[2] for vertex in vertices]

            centroid_x = sum(x_coords) / len(vertices)
            centroid_y = sum(y_coords) / len(vertices)
            centroid_z = sum(z_coords) / len(vertices)

            return (centroid_x, centroid_y, centroid_z)

        def sortPolys(self):
            sorted_data = sorted(self.engine.dist, key=lambda x: x[0], reverse=True)
            self.engine.layering.clear()
            self.engine.layering = [x[0:3] for x in sorted_data]


    def __init__(self,WIN,WIDTH,HEIGHT):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.WIN = WIN
        self.clipping = Clipping(WIDTH,HEIGHT)


        self.mainPoints = []
        self.points = []
        self.polys = {}
        self.screenPoints = []
        self.dist = []
        self.layering = []
        self.cos = 0
        self.sin = 0

        self.pos = [0,0,0]
        self.rot = [0,0,0]
        self.fov = 50
        self.speed = 0.25
        self.center = [self.WIDTH//2,self.HEIGHT//2]
        self.fill = True

        self.math = self.Math(self)

    def renderWorld(self):
        self.screenPoints.clear()
        self.points.clear()
        self.dist.clear()
        self.layering.clear()

        for poly1 in self.polys:
            polys = self.polys[poly1]
            for poly in polys:
                for x in poly[:3]:
                    point = self.mainPoints[x]

                    p = self.math.Translation(point, poly[3])
                    p1 = self.math.Rotation(p)
                    p2 = self.math.Projection(p1)
                    self.points.append(p)
                    self.screenPoints.append((self.center[0] + p2[0], self.center[1] + p2[1], p2[2]))
        self.math.calculateDis(self.points, self.polys)
        self.math.sortPolys()
        radius = 70
        brightness = 75
        max_color_val = 255

        for l in self.layering:
            p = self.polys[l[2]][l[1]]

            points = [self.screenPoints[o][:2] for o in p[:3]]
            ppoints = [self.points[o][:3] for o in p[:3]]
            points = self.clip(points)
            if len(points) > 2:
                s = ((l[0] / radius) - 1) * -1

                r = max(p[4][0]//10, min(int(s * brightness + p[4][0]), max_color_val))
                g = max(p[4][1]//10, min(int(s * brightness + p[4][1]), max_color_val))
                b = max(p[4][2]//10, min(int(s * brightness + p[4][2]), max_color_val))
                if b != p[4][2]//10 or g != p[4][1]//10 or r != p[4][0]//10:
                    if self.is_triangle_visible(ppoints):
                        color = (r, g, b)
                        if self.fill:
                            pygame.draw.polygon(self.WIN, color, points)
                        else:
                            pygame.draw.polygon(self.WIN, color, points, 1)

    def is_triangle_visible(self, vertices):
        def compute_normal(v0, v1, v2):
            u = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
            v = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])
            normal = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
            return normal

        def dot_product(vec1, vec2):
            return vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2]

        v0, v1, v2 = vertices

        normal = compute_normal(v0, v1, v2)
        view_vector = (v0[0] - self.pos[0], v0[1] - self.pos[1], v0[2] - self.pos[2])
        if dot_product(normal, view_vector) < 0:
            return True
        else:
            return False


    def changePos(self,pos):
        self.pos[0] += pos[0]
        self.pos[1] += pos[1]
        self.pos[2] += pos[2]

    def changeRot(self,rot):
        self.rot[0] += rot[0]
        self.rot[1] += rot[1]
        self.rot[2] += rot[2]

    def setPos(self,pos):
        self.pos[0] = pos[0]
        self.pos[1] = pos[1]
        self.pos[2] = pos[2]

    def setRot(self,rot):
        self.rot[0] = rot[0]
        self.rot[1] = rot[1]
        self.rot[2] = rot[2]

    def moveCam(self):
        key = pygame.key.get_pressed()
        x, y = self.speed * math.sin(self.rot[1]), self.speed * math.cos(self.rot[1])
        if key[pygame.K_w]:
            self.pos[0] += x
            self.pos[2] += y
        if key[pygame.K_s]:
            self.pos[0] -= x
            self.pos[2] -= y
        if key[pygame.K_a]:
            self.pos[0] -= y
            self.pos[2] += x
        if key[pygame.K_d]:
            self.pos[0] += y
            self.pos[2] -= x
        if key[pygame.K_RIGHT]:
            self.rot[1] += 0.05  # Yaw
        if key[pygame.K_LEFT]:
            self.rot[1] -= 0.05  # Yaw
        if key[pygame.K_UP]:
            self.rot[0] -= 0.05  # Pitch
        if key[pygame.K_DOWN]:
            self.rot[0] += 0.05  # Pitch
        if key[pygame.K_e]:
            self.pos[1] -= self.speed
        if key[pygame.K_q]:
            self.pos[1] += self.speed

        if key[pygame.K_z]:  # Roll
            self.rot[2] -= 0.05
        if key[pygame.K_x]:  # Roll
            self.rot[2] += 0.05



    def addPoly(self, name, points, color, offset=[0, 0, 0], rotation=[0, 0, 0]):
        indices = [len(self.mainPoints), len(self.mainPoints) + 1, len(self.mainPoints) + 2]
        pos,pos1,pos2 = points
        self.mainPoints.extend([pos, pos1, pos2])

        if name in self.polys:
            self.polys[name].append(indices + [offset, color, rotation])
        else:
            self.polys[name] = []
            self.polys[name].append(indices + [offset, color, rotation])

    def moveModel(self, name, pos, rot, origin=(0, 0, 0)):
        for poly in self.polys[name]:
            poly[3][0] += pos[0]
            poly[3][1] += pos[1]
            poly[3][2] += pos[2]

            for x in poly[:3]:
                self.mainPoints[x] = self.math.rotate(self.mainPoints[x], rot, origin)

    def removeModel(self, name):
        if name not in self.polys:
            return  # Model not found

        # Collect points used by the model to remove
        points_to_remove = {i for poly in self.polys[name] for i in poly[:3]}

        # Remove the model
        del self.polys[name]

        # Keep only the points still in use
        used_points = {i for polys in self.polys.values() for poly in polys for i in poly[:3]}
        self.mainPoints = [point for i, point in enumerate(self.mainPoints) if i in used_points]

        # Create index mapping for remaining points
        index_map = {old_idx: new_idx for new_idx, old_idx in enumerate(used_points)}

        # Update polygons with new indices
        self.polys = {
            model_name: [
                [index_map[i] for i in poly[:3]] + poly[3:]
                for poly in polys if all(i in index_map for i in poly[:3])
            ]
            for model_name, polys in self.polys.items()
        }

    def makeTerrain(self, girdSize,pos, scale):
        self.removeModel('terrain')
        perlinNoise = PerlinNoise().generate_noise(girdSize[0], girdSize[1], pos,7)
        width = len(perlinNoise[0])
        height = len(perlinNoise)
        point_list = []
        for y in range(height):
            for x in range(width):
                h = ((perlinNoise[y][x] + 1) / 2) * 15
                point_list.append([x * scale, h * scale, y * scale])

        quads = []
        for y in range(height - 1):
            for x in range(width - 1):
                p1 = point_list[y * width + x]
                p2 = point_list[y * width + x + 1]
                p3 = point_list[(y + 1) * width + x]
                p4 = point_list[(y + 1) * width + x + 1]

                quads.append([p1, p2, p3])  # First triangle
                quads.append([p2, p4, p3])  # Second triangle

        for i, quad in enumerate(quads):
            # Calculate average height of the quad vertices
            avg_height = sum(point[1] for point in quad) / 3
            # Normalize the height to the range of 0-1
            normalized_height = avg_height / (15 * scale)

            # Calculate color based on the normalized height

            if normalized_height < 0.3:
                # White color for the highest parts
                color = (150, 150, 150)
            elif normalized_height < 0.4:
                # Gradient from gray to white for middle parts
                gray_value = int(255 * (normalized_height - 0.3) / 0.4)
                color = (gray_value, gray_value, gray_value)
            elif normalized_height < 0.7:
                green_value = int(255 * (0.7 - normalized_height) / .5)
                color = (0, 255 - green_value-20, 0)
            else:
                # Blue color for the lowest parts
                blue_value = int(255 * (0.7 - normalized_height) / 0.3)
                color = (0, 0, 255 - blue_value)

            self.addPoly('terrain', [quad[0], quad[1], quad[2]], color)

    def openFile(self, groupName, filePath, scale, rot, pos, color):
        vertices = []
        faces = []

        with open(filePath, 'r') as file:
            lines = file.readlines()

        for line in lines:
            if line.startswith('v '):
                parts = line.split()
                vertex = [float(parts[1]) * scale, float(parts[2]) * scale, float(parts[3]) * scale]
                vertices.append(vertex)
            elif line.startswith('f '):
                parts = line.split()
                face = [int(part.split('/')[0]) - 1 for part in parts[1:]]
                faces.append(face)

        for face in faces:
            poly_points = [vertices[index] for index in face]
            self.addPoly(groupName, poly_points, color, pos, rot)

    def clip(self, mainPoints):

        newPoints = mainPoints.copy()
        for wall in range(4):
            clipped = []
            notClipped = []
            walls = [[[0, 0], [0, self.HEIGHT]], [[self.WIDTH, 0], [0, 0]],
                     [[self.WIDTH, self.HEIGHT], [self.WIDTH, 0]],
                     [[0, self.HEIGHT], [self.WIDTH, self.HEIGHT]]]
            if self.clipping.point_in_triangle(walls[wall][0], mainPoints[0], mainPoints[1], mainPoints[2]):
                newPoints.append(walls[wall][0])

            for point in mainPoints:
                if wall == 0:
                    if point[0] > 0:
                        notClipped.append(point)
                    else:
                        clipped.append(point)
                elif wall == 1:
                    if point[1] > 0:
                        notClipped.append(point)
                    else:
                        clipped.append(point)

                elif wall == 2:
                    if point[0] < self.WIDTH:
                        notClipped.append(point)
                    else:
                        clipped.append(point)

                elif wall == 3:
                    if point[1] < self.HEIGHT:
                        notClipped.append(point)
                    else:
                        clipped.append(point)

            for item in clipped:
                for item1 in notClipped:
                    point = self.clipping.intersection_point([item, item1], walls[wall])
                    newPoints.append(point)

        finalPoints = []
        for item in newPoints:
            if self.clipping.checkIn(item):
                finalPoints.append(item)

        # for item in finalPoints:
        #     pygame.draw.circle(self.WIN,(255,255,255),item,5)

        finalPoints = self.clipping.angle_sort(finalPoints)
        return finalPoints
