"""The ants_gui module implements a GUI for Ants vs. SomeBees.

You should not feel that you need to read and understand this file, because all
of the game logic is instead contained within ants.py.  We have provided some
comments so that interested students can extend the graphics.

=== Optional reading beyond this point ===

The GUI for this game has a fixed layout specified by a series of global names
that are constant throughout execution.  From a design perspective, global
names are a fine solution for holding constants; most problems associated with
global variables arise in programs that assign to global names.

The GUI layout itself is divided into a control panel that lists all
implemented ants and a play area populated with places.

The Hive is handled as a special case so that the player can visually inspect
how many bees remain in the hive.
"""

import ants
import graphics
from graphics import shift_point
from ucb import *
from math import pi
import math
import os
import random

STRATEGY_SECONDS = 3
INSECT_FILES = {'Worker': 'img/ant_harvester.gif',
                'Thrower': 'img/ant_thrower.gif',
                'Long': 'img/ant_longthrower.gif',
                'Short': 'img/ant_shortthrower.gif',
                'Harvester': 'img/ant_harvester.gif',
                'Fire': 'img/ant_fire.gif',
                'Bodyguard': 'img/ant_weeds.gif',
                'Hungry': 'img/ant_hungry.gif',
                'Slow': 'img/ant_freeze.gif',
                'Stun': 'img/ant_stun.gif',
                'Ninja': 'img/ant_ninja.gif',
                'Wall': 'img/ant_wall.gif',
                'Scuba': 'img/ant_scuba.gif',
                'Queen': 'img/ant_queen.gif',
                'Bee': 'img/bee.gif',
                'Remover': 'img/remover.gif'}
TUNNEL_FILE = 'img/tunnel.gif'
ANT_IMAGE_WIDTH = 66
ANT_IMAGE_HEIGHT = 71
BEE_IMAGE_WIDTH = 58
PANEL_PADDING = (2, 4)
PLACE_PADDING = (10, 10)
PLACE_POS = (40, 180)
PANEL_POS = (20, 40)
CRYPT = 650
MESSAGE_POS = (120, 20)
HIVE_HEIGHT = 300
PLACE_MARGIN = 10
LEAF_START_OFFSET = (30, 30)
LEAF_END_OFFSET = (35, 30)
LEAF_COLORS = {'Thrower': 'ForestGreen',
               'Short': 'Green',
               'Long': 'DarkGreen',
               'Slow': 'LightBlue',
               'Stun': 'Red',
               'Scuba': 'Blue',
               'Queen': 'Purple'}


class AntsGUI(object):
    """GUI-based interactive strategy that logs all colony updates."""

    def __init__(self):
        self.initialized = False

    def initialize_colony_graphics(self, colony):
        """Create canvas, control panel, places, and labels."""
        self.initialized = True
        self.canvas = graphics.Canvas()
        self.food_text = self.canvas.draw_text('Food: 1  Time: 0', (20, 20))
        self.ant_text = self.canvas.draw_text('Ant selected: None', (20, 140))
        self._click_rectangles = list()
        self._init_control_panel(colony)
        self._init_places(colony)

        start_text = self.canvas.draw_text('CLICK TO START', MESSAGE_POS)
        self.canvas.wait_for_click()
        self.canvas.clear(start_text)


    def _init_control_panel(self, colony):
        """Construct the control panel of available ant types."""
        self.ant_type_selected = None
        self.ant_type_frames = []  # rectangle ids of frames.
        panel_pos = PANEL_POS
        for name, ant_type in colony.ant_types.items():
            width = ANT_IMAGE_WIDTH + 2 * PANEL_PADDING[0]
            height = ANT_IMAGE_HEIGHT + 6 + 2 * PANEL_PADDING[1]
            def on_click(colony, frame, name=name):
                self.ant_type_selected = name
                self._update_control_panel(colony)

            frame = self.add_click_rect(panel_pos, width, height, on_click)
            self.ant_type_frames.append((name, frame))
            img_pos = shift_point(panel_pos, PANEL_PADDING)
            self.canvas.draw_image(img_pos, INSECT_FILES[name])
            cost_pos = shift_point(panel_pos, (width / 2, ANT_IMAGE_HEIGHT + 4
                + PANEL_PADDING[1]))
            food_str = str(ant_type.food_cost)
            self.canvas.draw_text(food_str, cost_pos, anchor="center")
            panel_pos = shift_point(panel_pos, (width + 2, 0))


    def _init_places(self, colony):
        """Construct places in the play area."""
        self.place_points = dict()
        # self.images: place_name -> insect instance -> image id
        self.images = {'AntQueen': dict()}
        place_pos = PLACE_POS
        width = BEE_IMAGE_WIDTH + 2 * PLACE_PADDING[0]
        height = ANT_IMAGE_HEIGHT + 2 * PLACE_PADDING[1]
        rows = 0
        for name, place in colony.places.items():
            if place.name == 'Hive':
                continue  # Handled as a special case later
            if place.exit.name == 'AntQueen':
                row_offset = (0, rows * (height + PLACE_MARGIN))
                place_pos = shift_point(PLACE_POS, row_offset)
                rows += 1
            def on_click(colony, frame, name=name):
                ant_type = self.ant_type_selected
                existing_ant = colony.places[name].ant
                if ant_type == 'Remover':
                    if existing_ant is not None:
                        print("colony.remove_ant('{0}')".format(name))
                        colony.remove_ant(name)
                        self._update_places(colony)
                elif ant_type is not None:
                    try:
                        print("colony.deploy_ant('{0}', '{1}')".format(name,
                                                                       ant_type))
                        colony.deploy_ant(name, ant_type)
                        self._update_places(colony)
                    except Exception as e:
                        print(e)
            color = 'Blue' if place.name.startswith('water') else 'White'
            frame = self.add_click_rect(place_pos, width, height, on_click,
                                             color=color)
            self.canvas.draw_image(place_pos, TUNNEL_FILE)
            self.place_points[name] = place_pos
            self.images[name] = dict()
            place_pos = shift_point(place_pos, (width + PLACE_MARGIN, 0))

        # Hive
        self.images[colony.hive.name] = dict()
        self.place_points[colony.hive.name] = (place_pos[0] + width,
                                               HIVE_HEIGHT)
        for bee in colony.hive.bees:
            self._draw_insect(bee, colony.hive.name, True)


    def add_click_rect(self, pos, width, height, on_click, color='White'):
        """Construct a rectangle that can be clicked."""
        frame_points = graphics.rectangle_points(pos, width, height)
        frame = self.canvas.draw_polygon(frame_points, fill_color=color)
        self._click_rectangles.append((pos, width, height, frame, on_click))
        return frame

    def strategy(self, colony):
        """The strategy function is called by the ants.AntColony each turn."""
        if not self.initialized:
            self.initialize_colony_graphics(colony)
        elapsed = 0  # Physical time elapsed this turn
        while elapsed < STRATEGY_SECONDS:
            self._update_control_panel(colony)
            self._update_places(colony)
            msg = 'Food: {0}  Time: {1}'.format(colony.food, colony.time)
            self.canvas.edit_text(self.food_text, text=msg)
            pos, el = self.canvas.wait_for_click(STRATEGY_SECONDS - elapsed)
            elapsed += el
            if pos is not None:
                self._interpret_click(pos, colony)

        # Throw leaves at the end of the turn
        has_ant = lambda a: hasattr(a, 'ant') and a.ant
        for ant in colony.ants + [a.ant for a in colony.ants if has_ant(a)]:
            if ant.name in LEAF_COLORS:
                self._throw(ant, colony)
            elif ant.name == 'Ninja':
                self._throw_dart(ant, colony)

    def _interpret_click(self, pos, colony):
        """Interpret a click position by finding its click rectangle."""
        x, y = pos
        for corner, width, height, frame, on_click in self._click_rectangles:
            cx, cy = corner
            if x >= cx and x <= cx + width and y >= cy and y <= cy + height:
                on_click(colony, frame)

    def _update_control_panel(self, colony):
        """Reflect the game state in the control panel."""
        for name, frame in self.ant_type_frames:
            cost = colony.ant_types[name].food_cost
            color = 'White'
            if cost > colony.food:
                color = 'Gray'
            elif name == self.ant_type_selected:
                color = 'Blue'
                msg = 'Ant selected: {0}'.format(name)
                self.canvas.edit_text(self.ant_text, text=msg)
            self.canvas._canvas.itemconfigure(frame, fill=color)

    def _update_places(self, colony):
        """Reflect the game state in the play area.

        This function handles several aspects of the game:
          - Adding Ant images for newly placed ants
          - Moving Bee images for bees that have advanced
          - Moving insects out of play when they have expired
        """
        for name, place in colony.places.items():
            if place.name == 'Hive':
                continue
            current = self.images[name].keys()

            # Add/move missing insects
            if place.ant is not None:
                if hasattr(place.ant, 'container') and place.ant.container \
                    and place.ant.ant and place.ant.ant not in current:
                    container = self.images[name][place.ant]
                    self._draw_insect(place.ant.ant, name, behind=container)
                if place.ant not in current:
                    self._draw_insect(place.ant, name)
            for bee in place.bees:
                if bee not in current:
                    for other_place in colony.places.values():
                        if other_place.exit is place:
                            break
                    else:
                        other_place = colony.hive
                    image = self.images[other_place.name].pop(bee)
                    pos = shift_point(self.place_points[name], PLACE_PADDING)
                    self.canvas.slide_shape(image, pos, STRATEGY_SECONDS)
                    self.images[name][bee] = image

            # Remove expired insects
            valid_insects = set(place.bees + [place.ant])
            if place.ant is not None and hasattr(place.ant, 'container') and \
                place.ant.container:
                valid_insects.add(place.ant.ant)
            for insect in current - valid_insects:
                if not place.exit or insect not in self.images[place.exit.name]:
                    image = self.images[name].pop(insect)
                    pos = (self.place_points[name][0], CRYPT)
                    self.canvas.slide_shape(image, pos, STRATEGY_SECONDS)

    def _draw_insect(self, insect, place_name, random_offset=False, behind=0):
        """Draw an insect and store the ID of its image."""
        image_file = INSECT_FILES[insect.name]
        pos = shift_point(self.place_points[place_name], PLACE_PADDING)
        if random_offset:
            pos = shift_point(pos, (random.randint(-10, 10), random.randint(-50, 50)))
        image = self.canvas.draw_image(pos, image_file, behind=behind)
        self.images[place_name][insect] = image

    def _throw(self, ant, colony):
        """Animate a leaf thrown at a Bee."""
        bee = ant.nearest_bee(colony.hive)  # nearest_bee logic from ants.py
        if bee:
            start = shift_point(self.place_points[ant.place.name], LEAF_START_OFFSET)
            end = shift_point(self.place_points[bee.place.name], LEAF_END_OFFSET)
            animate_leaf(self.canvas, start, end, color=LEAF_COLORS[ant.name])

    def _throw_dart(self, ant, colony):
        """Animate a dart thrown by a Ninja ant."""
        if ant.has_target(colony):
            start = shift_point(self.place_points[ant.place.name], LEAF_START_OFFSET)
            end = shift_point((self.place_points[colony.hive.name][0], self.place_points[ant.place.name][1]), LEAF_END_OFFSET)
            animate_dart(self.canvas, start, end)

def leaf_coords(pos, angle, length):
    """Return the coordinates of a leaf polygon."""
    angles = [angle - pi, angle - pi/2, angle, angle + pi/2]
    distances = [length/3, length/2, length, length/2]
    return [graphics.translate_point(pos, a, d) for a, d in zip(angles, distances)]

def animate_leaf(canvas, start, end, duration=0.3, color='ForestGreen'):
    """Define the animation frames for a thrown leaf."""
    length = 40
    leaf = canvas.draw_polygon(leaf_coords(start, 0, length),
            color='DarkGreen', fill_color=color, smooth=1)
    num_frames = duration / graphics.FRAME_TIME
    increment = tuple([(e-s) / num_frames for s, e in zip(start, end)])
    def points_fn(frame_count):
        nonlocal start
        angle = pi / 8 * frame_count
        cs = leaf_coords(start, angle, length)
        start = shift_point(start, increment)
        return cs
    canvas.animate_shape(leaf, duration, points_fn)
    canvas._canvas.after(int(1000*duration) + 1, lambda: canvas.clear(leaf))

def dart_coords(pos, angle, length):
    """Return the coordinates of a leaf polygon."""
    angles = [angle-pi, angle-pi*3/4, angle-pi/2, angle-pi/4, angle, angle+pi/4, angle+pi/2, angle+pi*3/4]
    distances = [length, length/5, length, length/5, length, length/5, length, length/5]
    return [graphics.translate_point(pos, a, d) for a, d in zip(angles, distances)]

def animate_dart(canvas, start, end, duration=0.5, color='Black'):
    """Define the animation frames for a thrown leaf."""
    length = 40
    dart = canvas.draw_polygon(dart_coords(start, 0, length),
            color='DarkGreen', fill_color=color, smooth=1)
    num_frames = duration / graphics.FRAME_TIME
    increment = tuple([(e-s) / num_frames for s, e in zip(start, end)])
    def points_fn(frame_count):
        nonlocal start
        angle = pi / 8 * frame_count
        cs = dart_coords(start, angle, length)
        start = shift_point(start, increment)
        return cs
    canvas.animate_shape(dart, duration, points_fn)
    canvas._canvas.after(int(1000*duration) + 1, lambda: canvas.clear(dart))

@main
def run(*args):
    ants.start_with_strategy(args, AntsGUI().strategy)
