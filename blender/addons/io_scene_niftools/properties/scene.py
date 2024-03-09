""" Nif User Interface, custom nif properties for objects"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright © 2016, NIF File Format Library and Tools contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the NIF File Format Library and Tools
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****


import bpy
from bpy.props import PointerProperty, IntProperty, EnumProperty, StringProperty, FloatProperty, CollectionProperty
from bpy.types import PropertyGroup
from itertools import chain

from nifgen.formats.nif.versions import available_versions, set_game

from io_scene_niftools.utils.decorators import register_classes, unregister_classes


class DummyClass: pass


dummy_context = DummyClass()
dummy_context.bs_header = DummyClass()
primary_games = list(chain.from_iterable(version.primary_games for version in available_versions if version.supported))
all_games = list(chain.from_iterable(version.all_games for version in available_versions if version.supported))
game_version_map = {}


def populate_version_map(iterable, version_map):
	for game in iterable:
		if game not in version_map:
		    dummy_context.version = 0
		    dummy_context.user_version = 0
		    dummy_context.bs_header.bs_version = 0
		    set_game(dummy_context, game)
		    game_version_map[game.name] = (dummy_context.version, dummy_context.user_version, dummy_context.bs_header.bs_version)


populate_version_map(primary_games, game_version_map)
populate_version_map(all_games, game_version_map)
game_version_map["UNKNOWN"] = (0, 0, 0)

# noinspection PyUnusedLocal
def update_version_from_game(self, context):
    """Updates the Scene panel's numerical version fields if its game value has been changed"""
    self.nif_version, self.user_version, self.user_version_2 = game_version_map[self.game]

class Scene(PropertyGroup):
    nif_version: IntProperty(
        name='Version',
        description="The Gamebryo Engine version used",
        default=0
    )

    user_version: IntProperty(
        name='User Version',
        description="Studio specific version, used to denote versioning from game to game",
        default=0
    )

    user_version_2: IntProperty(
        name='User Version 2',
        description="Studio specific version, used to denote versioning from game to game",
        default=0
    )

    # For which game to export.
    game: bpy.props.EnumProperty(
        items=[('UNKNOWN', 'UNKNOWN', 'No game selected')] + [
            (member.name, member.value, "Export for " + member.value)
            for member in sorted(
                [member for member in set(all_games)], key=lambda x: x.name)
        ],
        name="Game",
        description="For which game to export",
        default='UNKNOWN',
        update=update_version_from_game)

    def is_bs(self):
        return self.game in ('OBLIVION',
                            'FALLOUT_3',
                            'FALLOUT_NV',
                            'SKYRIM',
                            'SKYRIM_SE',
                            )

    def is_fo3(self):
        return self.game in ('FALLOUT_3', 'FALLOUT_NV')

    def is_skyrim(self):
        return self.game in ('SKYRIM', 'SKYRIM_SE')

    scale_correction: bpy.props.FloatProperty(
        name="Scale Correction",
        description="Changes size of mesh to fit onto Blender's default grid",
        default=0.1,
        min=0.001, max=100.0, precision=2)


CLASSES = [
    Scene
]


def register():
    register_classes(CLASSES, __name__)

    bpy.types.Scene.niftools_scene = bpy.props.PointerProperty(type=Scene)


def unregister():
    del bpy.types.Scene.niftools_scene

    unregister_classes(CLASSES, __name__)
