# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Author: Adhi Hargo (cadmus.sw@gmail.com)

import bpy
import os
from bpy.types import Operator, Macro
from bpy.props import BoolProperty, BoolVectorProperty, EnumProperty,\
    FloatProperty, StringProperty, PointerProperty

bl_info = {
    "name": "Import Rig",
    "author": "Adhi Hargo",
    "version": (1, 0, 0),
    "blender": (2, 68, 0),
    "location": "Scene > Import Rig",
    "description": "Import a group, create rig proxy and append rig script.",
    "warning": "",
    "wiki_url": "https://github.com/adhihargo/import_rig",
    "tracker_url": "https://github.com/adhihargo/import_rig/issues",
    "category": "Object"}

class ADH_ImportRig(Macro):
    """Import a group, create rig proxy and append rig script."""
    bl_idname = 'object.adh_import_rig'
    bl_label = 'Import Rig'
    bl_options = {'MACRO', 'REGISTER', 'UNDO'}

class ADH_LinkAppend(Operator):
    """Link/append data from another file."""
    bl_idname = 'wm.adh_link_append'
    bl_label = 'Import Rig'
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        obj = context.active_object

        if obj and obj.type == 'EMPTY' and obj.dupli_group != None:
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        bpy.ops.wm.link_append('INVOKE_DEFAULT')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class ADH_CreateRigProxy(Operator):
    "If active object is a group containing a rig, proxy the rig."
    bl_idname = 'object.adh_create_rig_proxy'
    bl_label = 'Create Rig Proxy'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not (obj and obj.dupli_group):
            return {'CANCELLED'}

        group = obj.dupli_group
        for o in group.objects:
            if o.type == 'ARMATURE':
                bpy.ops.object.proxy_make(object = o.name)
                context.active_object.name = group.name + "_rig"
                bpy.ops.object.posemode_toggle()
                break

        return {'FINISHED'}

class ADH_AppendRigScript(Operator):
    "Given active object's group, append every script from the group's file."
    bl_idname = 'object.adh_append_rig_script'
    bl_label = 'Append Rig Script'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not (obj and obj.dupli_group):
            return {'CANCELLED'}

        group = obj.dupli_group
        group_libpath = group.library.filepath
        script_list = None

        with bpy.data.libraries.load(group_libpath, link=True, relative=True)\
                as (data_from, data_to):
            script_list = [t for t in data_from.texts if t.endswith('.py')]
            data_to.texts.extend(script_list)
        if not script_list:
            return {'FINISHED'}

        prev_type = context.area.type
        context.area.type = 'TEXT_EDITOR'
        prev_text = context.space_data.text
        for script in script_list:
            context.space_data.text = bpy.data.texts[script]
            try:
                bpy.ops.text.run_script()
            except:
                self.report({'WARNING'}, 'Unable to run script "%s"' % script)
        context.space_data.text = prev_text
        context.area.type = prev_type
        
        return {'FINISHED'}

class SCENE_PT_adh_scene_panel(bpy.types.Panel):
    bl_label = 'Import Rig'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    
    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)
        row = column.row()
        row.operator("object.adh_import_rig")

def register():
    bpy.utils.register_module(__name__)
    ADH_ImportRig.define("WM_OT_adh_link_append")
    ADH_ImportRig.define("OBJECT_OT_adh_append_rig_script")    
    ADH_ImportRig.define("OBJECT_OT_adh_create_rig_proxy")

def unregister():
    bpy.utils.unregister_module(__name__)
    
