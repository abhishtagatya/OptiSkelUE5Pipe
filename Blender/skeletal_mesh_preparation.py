import bpy

PROGRAM_NAME = "OptiSkelUE5Pipe-SKMPrep"

#region DATA
SKP_CHAIN_MATERIAL = {
    "Spine": {
        "bones": ["Spine"],
        "material_data": {
            "color": (230, 25, 75)
        }
    },
    "Neck": {
        "bones": ["Neck"],
        "material_data": {
            "color": (245, 130, 48)
        }
    },
    "Head": {
        "bones": ["Head"],
        "material_data": {
            "color": (255, 225, 25)
        }
    },
    "LeftClavicle": {
        "bones": ["LeftShoulder"],
        "material_data": {
            "color": (210, 245, 60)
        }
    },
    "LeftArm": {
        "bones": ["LeftArm", "LeftForeArm", "LeftHand"],
        "material_data": {
            "color": (60, 180, 75)
        }
    },
    "RightClavicle": {
        "bones": ["RightShoulder"],
        "material_data": {
            "color": (90, 240, 240)
        }
    },
    "RightArm": {
        "bones": ["RightArm", "RightForeArm", "RightHand"],
        "material_data": {
            "color": (0, 130, 200)
        }
    },
    "LeftLeg": {
        "bones": ["LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase"],
        "material_data": {
            "color": (145, 30, 180)
        }
    },
    "RightLeg": {
        "bones": ["RightUpLeg", "RightLeg", "RightFoot", "RightToeBase"],
        "material_data": {
            "color": (240, 50, 230)
        }
    },
    "Default": {
        "bones": [],
        "material_data": {
            "color": (128, 128, 128)
        }
    }
}
#endregion

class SkeletalMeshPreparation:

    def __init__(self, 
                 mesh_primitive: str = "CUBE", 
                 mesh_size: float = 0.5, 
                 mesh_color_method: str = "CHAIN",
                 armature_rename: bool = False):
        self.mesh_primitive = mesh_primitive
        self.mesh_size = mesh_size
        self.mesh_color_method = mesh_color_method
        self.armature_rename = armature_rename

    def create_primitive_adapter(self):
        """
        Adapter method to create Blender primitives
        """
        if self.mesh_primitive == "CUBE":
            bpy.ops.mesh.primitive_cube_add(size=self.mesh_size, location=(0, 0, 0))
            return
        if self.mesh_primitive == "SPHERE":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=self.mesh_size, location=(0, 0, 0), segments=16, ring_count=8)

    def get_materials_by_method(self, bone_name: str) -> bpy.types.Material:
        """
        Get Existing Material by Defined Mesh Coloring Method
        """
        if self.mesh_color_method == "CHAIN":
            chain_group = self.find_bone_chain_group(bone_name)
            return self.get_materials_skp_chain(chain_group)
    
    def get_materials_skp_chain(self, bone_name: str) -> bpy.types.Material:
        """
        Get Existing Material by Skeletal Mesh Placeholder Chain Grouping (Specific for UE5)
        """
        mat_name = self.construct_material_name(bone_name)
        if mat_name not in bpy.data.materials:
            mat_name = self.construct_material_name("Default")
        return bpy.data.materials[mat_name]
        
    def find_bone_chain_group(self, bone_name: str) -> str:
        """
        Find the Bone's Chain Group
        """
        prefixes = bone_name.split("_")
        if len(prefixes) > 1:
            bone_name = prefixes[1]

        for key, value in SKP_CHAIN_MATERIAL.items():
            if any(bone_name.startswith(core_name) for core_name in value["bones"]):
                return key
        return "Default"
    
    def create_materials_by_method(self):
        """
        Create Materials by Defined Mesh Coloring Method
        """
        if self.mesh_color_method == "CHAIN":
            self.create_materials_skp_chain()
            return
        return

    def create_materials_skp_chain(self):
        """
        Create Materials by Skeletal Mesh Placeholder Chain Grouping (Specific for UE5)
        """
        for key, value in SKP_CHAIN_MATERIAL.items():
            mat_name = self.construct_material_name(key)
            if mat_name not in bpy.data.materials:
                mat = bpy.data.materials.new(name=mat_name)
                mat.use_nodes = True
                p_bsdf = mat.node_tree.nodes.get("Principled BSDF")

                if p_bsdf:
                    mat_color = (
                        value["material_data"]["color"][0]/255, 
                        value["material_data"]["color"][1]/255, 
                        value["material_data"]["color"][2]/255, 1.0
                    )
                    p_bsdf.inputs["Base Color"].default_value = mat_color
                    mat.diffuse_color = mat_color

    def construct_material_name(self, key):
        """
        Construct Material Name by Key
        """
        return f"M_{self.__class__.__name__}_{self.mesh_color_method}_{str(key)}"
    
    def rename_armature(self, part_name) -> str:
        """
        Rename an Armature Object Parts by Stripping Prefixes.
        """
        prefixes = part_name.split("_")
        if len(prefixes) > 1:
            return prefixes[1]
        return part_name

    def place_mesh_armature_bone_tip(self, selected_armature):
        """
        Place Primitives with Material on Armature's Bone's Tip Position
        """

        # Check that Object is an Armature
        if selected_armature is None or selected_armature.type != "ARMATURE":
            print(PROGRAM_NAME + ": " + f"Couldn't find an Armature named {selected_armature_name}.")
            return
        
        # Set to Object Mode
        if bpy.ops.object.mode_set.poll():
            if bpy.context.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")

        bpy.ops.object.select_all(action="DESELECT")

        # Rename Armature Pose
        if (self.armature_rename):
            selected_armature.data.name = self.rename_armature(selected_armature.data.name)

        # Iterate for All Bones in the Armature
        for pose_bone in selected_armature.pose.bones:

            # Rename Bone (remove OptiTrack Prefix)
            bone_name = pose_bone.name
            if (self.armature_rename):
                pose_bone.name = self.rename_armature(pose_bone.name)
                bone_name = pose_bone.name
            
            # Create Primitive as Placeholder for UE5 SKM
            self.create_primitive_adapter()
            pobj = bpy.context.active_object
            pobj.name = f"P_{bone_name}"
            
            # Place the Primitive to the Bone
            bone_world_matrix = selected_armature.matrix_world @ pose_bone.matrix
            pobj.matrix_world = bone_world_matrix

            bpy.ops.object.select_all(action="DESELECT")
            pobj.select_set(True)
            selected_armature.select_set(True)
            bpy.context.view_layer.objects.active = selected_armature

            # Set Material based on SKM Chain for Primitive
            proxy_material = self.get_materials_by_method(bone_name)

            if pobj.data.materials:
                pobj.data.materials[0] = proxy_material
            else:
                pobj.data.materials.append(proxy_material)
            
            # Constraint place Primitive as a Child of the Bone
            pobj.parent = selected_armature
            pobj.parent_type = 'BONE'
            pobj.parent_bone = bone_name
            
            pobj_contraint = pobj.constraints.new(type="CHILD_OF")
            pobj_contraint.target = selected_armature
            pobj_contraint.subtarget = bone_name

            bpy.ops.object.select_all(action="DESELECT")
            pobj.select_set(True)
            bpy.context.view_layer.objects.active = pobj
            
            bpy.ops.constraint.childof_set_inverse(constraint=pobj_contraint.name, owner="OBJECT")

            pobj.scale = (self.mesh_size, self.mesh_size, self.mesh_size)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            
            bpy.ops.object.select_all(action="DESELECT")
            pobj.select_set(True)
            bpy.context.view_layer.objects.active = pobj
            
            bpy.ops.constraint.apply(constraint=pobj_contraint.name, owner="OBJECT")
            
            print(PROGRAM_NAME + f": Created P_{bone_name} attached to {bone_name} of {selected_armature}.")
    
    def run(self, selected_armature):
        """
        Run the Skeletal Mesh Placeholder
        """
        print(PROGRAM_NAME + f": Running Skeletal Mesh Placeholder Program")
        self.create_materials_by_method()
        self.place_mesh_armature_bone_tip(selected_armature)
        if (self.armature_rename):
            selected_armature.name = self.rename_armature(selected_armature.name)

if __name__ == "__main__":
    smp = SkeletalMeshPreparation(mesh_primitive="CUBE", mesh_size=2.0, armature_rename=True)
    for obj in bpy.context.selected_objects:
        smp.run(selected_armature=obj)