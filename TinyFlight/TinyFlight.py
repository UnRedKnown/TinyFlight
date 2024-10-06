# change parasite drag depending on configuration, ldg gear position
# make RWR
# fix altitude
# MAKE SURE that all calculations involving relative area based on AoA, use Arel and not wingarea (yeah just go through all the math ffs)

import pygame
import math
from _3DEngine import Engine
from PhysEngine import Physics

pygame.init()
screen = pygame.display.set_mode((128, 128))
pygame.display.set_caption('TinyFlight')

green = (0, 255, 0)
skyblue = (135, 206, 235)
black = (0, 0, 0)

warnings = []
framecounter = 0
blinkstate = 0
hdg = 45
spd = 0
pitch = 0
roll = 0
gs = 0
aoa = 0
pitchrate = 10
rollrate = 50
alt = 0
x = 0
y = 0
z = 0
altspd = 0
throttle = 0
sound = 0
font = pygame.font.Font(r"C:\Users\Administrator\Downloads\TC3x5numbers-Regular.ttf", 5)
test = pygame.image.load(r"C:\Users\Administrator\Downloads\testflight.bmp")
imagerect = test.get_rect()
radarmode = 0
mode = 0
modes = ['TXI', 'FLY', 'WPN']
abtoggle = 0
velocity = 0
temperature = 288.15
engine = Engine(screen, 128, 128)
physics = Physics()
engine.makeTerrain([20,20],[0,0],2)

# Constants for the HUD
SQUARE_START_X, SQUARE_START_Y = 37, 37
SQUARE_SIZE = 54
CENTER_X = SQUARE_START_X + SQUARE_SIZE // 2
CENTER_Y = SQUARE_START_Y + SQUARE_SIZE // 2
LINE_SPACING = 5
TEXT_OFFSET = 6
MAX_LINES = 5
INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8

# Example F-22 Raptor, clean config
abmaxthrust = 312000
maxthrust = 232000
minweight = 193191 + 80442
weight = 0
wingarea = 78.04
wingspan = 13.56
aspectratio = (wingspan ** 2) / wingarea
oswaldefficiency = 0.82
wingangle = 42
liftslope = (2 * math.pi * aspectratio) / (2 + math.sqrt(4 + (aspectratio**2) * (1 + (math.tan(math.radians(wingangle))**2))))
# average
thickchordratio = 5.105
# estimate
liftcoef0 = 0.15
parasitedrag =  0.0348
someclfactor = 0.09
baselineclmax = 1.2

# And all of that converted to a list for the Physics engine
raptor = [maxthrust, abmaxthrust, minweight, weight, wingarea, wingspan, oswaldefficiency, wingangle, thickchordratio, liftcoef0, parasitedrag, baselineclmax]

# Artificial horizon
def rotate_point(px, py, ox, oy, angle):
    cos_theta, sin_theta = math.cos(angle), math.sin(angle)
    px, py = px - ox, py - oy
    return px * cos_theta - py * sin_theta + ox, px * sin_theta + py * cos_theta + oy
def draw_rotated_text(surface, text, pos, angle, color, font_size=12):
    font = pygame.font.SysFont(None, font_size)
    text_surface = pygame.transform.rotate(font.render(text, True, color), angle)
    text_rect = text_surface.get_rect(center=pos)
    surface.blit(text_surface, text_rect.topleft)
def draw_dashed_line(surface, color, start_pos, end_pos, width=1, dash_length=4, space_length=4, gap_length=10):
    x1, y1, x2, y2 = *start_pos, *end_pos
    total_length = math.hypot(x2 - x1, y2 - y1)
    half_gap = gap_length / 2
    dash_total_length = dash_length + space_length
    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
    gap_offset_x = half_gap * (x2 - x1) / total_length
    gap_offset_y = half_gap * (y2 - y1) / total_length
    start_gap_x, start_gap_y = mid_x - gap_offset_x, mid_y - gap_offset_y
    end_gap_x, end_gap_y = mid_x + gap_offset_x, mid_y + gap_offset_y

    def draw_segment(start, end):
        segment_length = math.hypot(end[0] - start[0], end[1] - start[1])
        num_dashes = int(segment_length / dash_total_length)
        for i in range(num_dashes + 1):
            dash_start = (
                start[0] + (end[0] - start[0]) * i * dash_total_length / segment_length,
                start[1] + (end[1] - start[1]) * i * dash_total_length / segment_length
            )
            dash_end = (
                start[0] + (end[0] - start[0]) * (i * dash_total_length + dash_length) / segment_length,
                start[1] + (end[1] - start[1]) * (i * dash_total_length + dash_length) / segment_length
            )
            if math.hypot(dash_end[0] - start[0], dash_end[1] - start[1]) > segment_length:
                dash_end = end
            pygame.draw.line(surface, color, dash_start, dash_end, width)

    draw_segment((x1, y1), (start_gap_x, start_gap_y))
    draw_segment((end_gap_x, end_gap_y), (x2, y2))
def compute_out_code(x, y, min_x, min_y, max_x, max_y):
    code = INSIDE
    if x < min_x:
        code |= LEFT
    elif x > max_x:
        code |= RIGHT
    if y < min_y:
        code |= BOTTOM
    elif y > max_y:
        code |= TOP
    return code
def cohen_sutherland_clip(x1, y1, x2, y2, min_x, min_y, max_x, max_y):
    outcode1 = compute_out_code(x1, y1, min_x, min_y, max_x, max_y)
    outcode2 = compute_out_code(x2, y2, min_x, min_y, max_x, max_y)
    accept = False

    while True:
        if outcode1 == 0 and outcode2 == 0:
            accept = True
            break
        elif (outcode1 & outcode2) != 0:
            break
        else:
            x, y = 0.0, 0.0
            outcode_out = outcode1 if outcode1 != 0 else outcode2
            if outcode_out & TOP:
                x = x1 + (x2 - x1) * (max_y - y1) / (y2 - y1)
                y = max_y
            elif outcode_out & BOTTOM:
                x = x1 + (x2 - x1) * (min_y - y1) / (y2 - y1)
                y = min_y
            elif outcode_out & RIGHT:
                y = y1 + (y2 - y1) * (max_x - x1) / (x2 - x1)
                x = max_x
            elif outcode_out & LEFT:
                y = y1 + (y2 - y1) * (min_x - x1) / (x2 - x1)
                x = min_x

            if outcode_out == outcode1:
                x1, y1 = x, y
                outcode1 = compute_out_code(x1, y1, min_x, min_y, max_x, max_y)
            else:
                x2, y2 = x, y
                outcode2 = compute_out_code(x2, y2, min_x, min_y, max_x, max_y)

    return (x1, y1), (x2, y2) if accept else None
def generate_hud_lines(pitch_angle):
    hud_lines = []
    pitch_angle = int(pitch_angle)  # Ensure pitch_angle is an integer
    start_pitch = (pitch_angle // LINE_SPACING - (MAX_LINES // 2)) * LINE_SPACING
    end_pitch = start_pitch + ((MAX_LINES - 1) * LINE_SPACING)
    for pitch in range(start_pitch, end_pitch + 1, LINE_SPACING):
        line_y = CENTER_Y - (pitch - pitch_angle) * (SQUARE_SIZE / (2 * (90 // LINE_SPACING)))
        display_pitch = abs(pitch % 180 - 180 if pitch % 180 > 90 else pitch % 180)
        hud_lines.append((f"{display_pitch}", [(CENTER_X - SQUARE_SIZE // 2, line_y), (CENTER_X + SQUARE_SIZE // 2, line_y)], display_pitch == 0))
    return hud_lines
def draw_hud_lines(surface, roll_angle, pitch_angle):
    roll_rad = math.radians(roll_angle)
    hud_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
    hud_surface.set_colorkey(black)
    hud_surface.fill(black)

    hud_lines = generate_hud_lines(pitch_angle)
    for pitch_text, line, is_zero_pitch in hud_lines:
        (start_x, start_y), (end_x, end_y) = line
        new_start_x, new_start_y = rotate_point(start_x, start_y, CENTER_X, CENTER_Y, roll_rad)
        new_end_x, new_end_y = rotate_point(end_x, end_y, CENTER_X, CENTER_Y, roll_rad)
        clipped_line = cohen_sutherland_clip(new_start_x, new_start_y, new_end_x, new_end_y, SQUARE_START_X, SQUARE_START_Y, SQUARE_START_X + SQUARE_SIZE, SQUARE_START_Y + SQUARE_SIZE)

        if clipped_line:
            clipped_start, clipped_end = clipped_line
            if is_zero_pitch:
                draw_dashed_line(hud_surface, green, (clipped_start[0] - SQUARE_START_X, clipped_start[1] - SQUARE_START_Y), (clipped_end[0] - SQUARE_START_X, clipped_end[1] - SQUARE_START_Y), 1, dash_length=SQUARE_SIZE, space_length=0, gap_length=15)
            else:
                draw_dashed_line(hud_surface, green, (clipped_start[0] - SQUARE_START_X, clipped_start[1] - SQUARE_START_Y), (clipped_end[0] - SQUARE_START_X, clipped_end[1] - SQUARE_START_Y))

            text_angle = -roll_angle
            offset_x, offset_y = TEXT_OFFSET * math.cos(roll_rad), TEXT_OFFSET * math.sin(roll_rad)
            draw_rotated_text(surface, pitch_text, (clipped_start[0] - offset_x, clipped_start[1] - offset_y), text_angle, green)
            draw_rotated_text(surface, pitch_text, (clipped_end[0] + offset_x, clipped_end[1] + offset_y), text_angle, green)

    surface.blit(hud_surface, (SQUARE_START_X, SQUARE_START_Y))


# Hell
def get_rotation_matrix(pitch, yaw, roll):
    # Convert angles from degrees to radians
    pitch = math.radians(pitch)
    yaw = math.radians(yaw)
    roll = math.radians(roll)

    # Calculate the individual rotation matrices
    pitch_matrix = [
        [1, 0, 0],
        [0, math.cos(pitch), -math.sin(pitch)],
        [0, math.sin(pitch), math.cos(pitch)]
    ]

    yaw_matrix = [
        [math.cos(yaw), 0, math.sin(yaw)],
        [0, 1, 0],
        [-math.sin(yaw), 0, math.cos(yaw)]
    ]

    roll_matrix = [
        [math.cos(roll), -math.sin(roll), 0],
        [math.sin(roll), math.cos(roll), 0],
        [0, 0, 1]
    ]

    # Multiply the matrices yaw * pitch * roll (in that order)
    # First, calculate yaw_matrix * pitch_matrix
    combined_matrix = [
        [
            yaw_matrix[0][0] * pitch_matrix[0][0] + yaw_matrix[0][1] * pitch_matrix[1][0] + yaw_matrix[0][2] * pitch_matrix[2][0],
            yaw_matrix[0][0] * pitch_matrix[0][1] + yaw_matrix[0][1] * pitch_matrix[1][1] + yaw_matrix[0][2] * pitch_matrix[2][1],
            yaw_matrix[0][0] * pitch_matrix[0][2] + yaw_matrix[0][1] * pitch_matrix[1][2] + yaw_matrix[0][2] * pitch_matrix[2][2]
        ],
        [
            yaw_matrix[1][0] * pitch_matrix[0][0] + yaw_matrix[1][1] * pitch_matrix[1][0] + yaw_matrix[1][2] * pitch_matrix[2][0],
            yaw_matrix[1][0] * pitch_matrix[0][1] + yaw_matrix[1][1] * pitch_matrix[1][1] + yaw_matrix[1][2] * pitch_matrix[2][1],
            yaw_matrix[1][0] * pitch_matrix[0][2] + yaw_matrix[1][1] * pitch_matrix[1][2] + yaw_matrix[1][2] * pitch_matrix[2][2]
        ],
        [
            yaw_matrix[2][0] * pitch_matrix[0][0] + yaw_matrix[2][1] * pitch_matrix[1][0] + yaw_matrix[2][2] * pitch_matrix[2][0],
            yaw_matrix[2][0] * pitch_matrix[0][1] + yaw_matrix[2][1] * pitch_matrix[1][1] + yaw_matrix[2][2] * pitch_matrix[2][1],
            yaw_matrix[2][0] * pitch_matrix[0][2] + yaw_matrix[2][1] * pitch_matrix[1][2] + yaw_matrix[2][2] * pitch_matrix[2][2]
        ]
    ]

    # Then multiply the result by roll_matrix
    final_matrix = [
        [
            combined_matrix[0][0] * roll_matrix[0][0] + combined_matrix[0][1] * roll_matrix[1][0] + combined_matrix[0][2] * roll_matrix[2][0],
            combined_matrix[0][0] * roll_matrix[0][1] + combined_matrix[0][1] * roll_matrix[1][1] + combined_matrix[0][2] * roll_matrix[2][1],
            combined_matrix[0][0] * roll_matrix[0][2] + combined_matrix[0][1] * roll_matrix[1][2] + combined_matrix[0][2] * roll_matrix[2][2]
        ],
        [
            combined_matrix[1][0] * roll_matrix[0][0] + combined_matrix[1][1] * roll_matrix[1][0] + combined_matrix[1][2] * roll_matrix[2][0],
            combined_matrix[1][0] * roll_matrix[0][1] + combined_matrix[1][1] * roll_matrix[1][1] + combined_matrix[1][2] * roll_matrix[2][1],
            combined_matrix[1][0] * roll_matrix[0][2] + combined_matrix[1][1] * roll_matrix[1][2] + combined_matrix[1][2] * roll_matrix[2][2]
        ],
        [
            combined_matrix[2][0] * roll_matrix[0][0] + combined_matrix[2][1] * roll_matrix[1][0] + combined_matrix[2][2] * roll_matrix[2][0],
            combined_matrix[2][0] * roll_matrix[0][1] + combined_matrix[2][1] * roll_matrix[1][1] + combined_matrix[2][2] * roll_matrix[2][1],
            combined_matrix[2][0] * roll_matrix[0][2] + combined_matrix[2][1] * roll_matrix[1][2] + combined_matrix[2][2] * roll_matrix[2][2]
        ]
    ]

    return final_matrix
def move_forward(position, pitch, yaw, roll, distance):
    # Get the rotation matrix
    rotation_matrix = get_rotation_matrix(pitch, yaw, roll)

    # Forward vector in local space
    forward_vector = [0, 0, 1]

    # Calculate direction in world space
    direction = [
        rotation_matrix[0][0] * forward_vector[0] + rotation_matrix[0][1] * forward_vector[1] + rotation_matrix[0][2] * forward_vector[2],
        rotation_matrix[1][0] * forward_vector[0] + rotation_matrix[1][1] * forward_vector[1] + rotation_matrix[1][2] * forward_vector[2],
        rotation_matrix[2][0] * forward_vector[0] + rotation_matrix[2][1] * forward_vector[1] + rotation_matrix[2][2] * forward_vector[2]
    ]

    # Update position by moving forward in the direction
    new_position = [
        position[0] + direction[0] * distance,
        position[1] + direction[1] * distance,
        position[2] + direction[2] * distance
    ]

    return new_position
def adjust_pitch_heading(pitch, heading, roll, delta_angle):

    if roll == 90 or roll == 270:
        # Only heading changes
        heading += delta_angle
    else:
        # Both pitch and heading change
        cos_roll = math.cos(math.radians(roll))
        sin_roll = math.sin(math.radians(roll))

        # Adjust both pitch and heading
        pitch += delta_angle * cos_roll
        heading += delta_angle * sin_roll

    return pitch, heading

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                mode = (mode + 1) % 3

    # Conversion
    spd = velocity * 1.944
    alt = y * 3.281

    # Input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        ailerondeflection = 40
        roll += rollrate / 60
    elif keys[pygame.K_RIGHT]:
        ailerondeflection = -40
        roll -= rollrate / 60
    else:
        ailerondeflection = 0
    if keys[pygame.K_UP]:
        elevatordeflection = -45
        pitch = adjust_pitch_heading(pitch, hdg, roll, -(rollrate/60))[0]
        hdg = adjust_pitch_heading(pitch, hdg, roll, rollrate/60)[1]
    elif keys[pygame.K_DOWN]:
        elevatordeflection = 45
        pitch = adjust_pitch_heading(pitch, hdg, roll, rollrate/60)[0]
        hdg = adjust_pitch_heading(pitch, hdg, roll, -(rollrate/60))[1]
    else:
        elevatordeflection = 0
    if keys[pygame.K_z]:
        aoa -= 1
    if keys[pygame.K_x]:
        aoa += 1
    if keys[pygame.K_a]:
        throttle -= 1
    if keys[pygame.K_d]:
        throttle += 1

    # Number checks
    if alt < 0:
        alt = 0
    if hdg < 0:
        hdg = 359
    elif hdg > 359:
        hdg = 0
    if throttle < 0:
        throttle = 0
    elif throttle > 100:
        throttle = 100
    if roll < 0:
        roll = 359
    elif roll > 359:
        roll = 0
    if pitch < 0:
        pitch = 359
    elif pitch > 359:
        pitch = 0
    if 0 <= throttle <= 80:
        abtoggle = 0
    else:
        abtoggle = 1

    # Output
    velocity += acceleration / 60

    # Functions
    physicsvars = [y, aoa, velocity, throttle, elevatordeflection, ailerondeflection]
    physics.update_vars(physicsvars)
    physics.update_physics()

    # Drawing
    screen.fill(black)
    engine.renderWorld()
    screen.blit(test, imagerect)
    engine.rot = [math.radians(-pitch), math.radians(hdg), math.radians(roll)]
    x, y, z = move_forward(engine.pos, pitch, hdg, roll, velocity/800)
    engine.pos = [x, y, z]
    screen.blit(font.render(str(int(hdg)), False, green), (79 - len(str(int(hdg))) * 4, 20))
    screen.blit(font.render('ASL' if radarmode == 0 else 'RDR', False, green), (114, 47))
    screen.blit(font.render(str(int(alt//1)), False, green), (107, 57))
    screen.blit(font.render(str(int(spd//1)), False, green), (28 - len(str(int(spd//1))) * 4, 54))
    screen.blit(font.render(str(altspd), False, green), (127 - len(str(altspd) * 4), 122))
    screen.blit(font.render(modes[mode], False, green), (11, 120))
    screen.blit(font.render(str(round(machspeed, 2)), False, green), (11, 68))
    screen.blit(font.render(str(round(gs, 2)) if len(str(round(gs, 2))) < 4 else str(int(gs//1)), False, green), (11, 75))
    screen.blit(font.render(str(round(aoa, 2)) if len(str(math.fabs(round(aoa, 2)))) < 4 else str(int(aoa//1)), False, green), (11, 82))
    if int(aoa) not in range(-16, 18):
        if '[ STALL ]0' not in warnings: warnings.append('[ STALL ]0'), blinkstate == 1
    else:
        if '[ STALL ]0' in warnings: warnings.remove('[ STALL ]0')
    if -152 <= int(y) <= 0:
        if '[ ALTITUDE ]1' not in warnings: warnings.append('[ ALTITUDE ]1'), blinkstate == 1
    else:
        if '[ ALTITUDE ]1' in warnings: warnings.remove('[ ALTITUDE ]1')
    if warnings:
        warningy=128
        for i in warnings:
            warningy -= 7
            if blinkstate == 1:
                screen.blit(font.render(i[:-1], False, (255, 198, 0) if i[-1] == '0' else (255, 0, 0)), (64 - (len(i) * 4) / 2, warningy))

    draw_hud_lines(screen, roll, pitch)
    if abtoggle == 0:
        pygame.draw.line(screen, green, [4, 126], [4, 126 - (throttle / 20) * 4])
        pygame.draw.line(screen, green, [5, 126], [5, 126 - (throttle / 20) * 4])
    else:
        pygame.draw.line(screen, green, [4, 126], [4, 106])
        pygame.draw.line(screen, green, [5, 126], [5, 106])
    if framecounter % 15 == 0:
        blinkstate = (blinkstate + 1) % 2


    pygame.display.flip()
    pygame.time.Clock().tick(60)
    framecounter += 1
    print(physics.update_physics(1/60))

pygame.quit()
