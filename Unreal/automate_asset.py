import unreal

def auto_skm_to_ikr(skm, fpathext = "Rigs"):
    """
    Automate Creating IK Rigs for a Skeletal Mesh
    
    :param skm: Skeletal Mesh Asset
    :param fpathext: (Optional) Folder Name
    """
    log_indexer = "[AutoSKM2IKR-Python]"

    fname = unreal.EditorAssetLibrary.get_fname(skm)
    fpath = unreal.EditorAssetLibrary.get_path_name(skm).split(".")[0].replace(str(fname),"")
    unreal.log("Name: {0}, Path: {1}".format(fname, fpath))

    # Use the asset tools
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    # Create the IK Rig Asset
    unreal.log(log_indexer + ": " + "Creating IK Rig Asset")
    ikr = asset_tools.create_asset(asset_name='IKR_{0}'.format(fname),
        package_path=fpath + fpathext, asset_class=unreal.IKRigDefinition,
        factory=unreal.IKRigDefinitionFactory())
    
    # Get the IK Rig Asset Controller
    unreal.log(log_indexer + ": " + "Controlling IK Rig Asset")
    ikr_asset_controller = unreal.IKRigController.get_controller(ikr)
    ikr_asset_controller.set_skeletal_mesh(skm)
    fbik_index = ikr_asset_controller.add_solver(unreal.IKRigFBIKSolver)

    # Set IK Goals
    unreal.log(log_indexer + ": " + "Creating IK Goals")
    ikr_asset_controller.add_new_goal("LeftArm_Goal", "LeftHand_end")
    ikr_asset_controller.add_new_goal("RightArm_Goal", "RightHand_end")
    ikr_asset_controller.add_new_goal("LeftLeg_Goal", "LeftToeBase")
    ikr_asset_controller.add_new_goal("RightLeg_Goal", "RightToeBase")

    ikr_asset_controller.add_bone_setting("Spine", 0)
    ikr_asset_controller.add_bone_setting("Spine1", 0)
    ikr_asset_controller.add_bone_setting("LeftShoulder", 0)
    ikr_asset_controller.add_bone_setting("RightShoulder", 0)
    ikr_asset_controller.add_bone_setting("LeftForeArm", 0)
    ikr_asset_controller.add_bone_setting("RightForeArm", 0)
    ikr_asset_controller.add_bone_setting("RightLeg", 0)
    ikr_asset_controller.add_bone_setting("LeftLeg", 0)

    # Set Spine settings
    unreal.log(log_indexer + ": " + "Adjusting Bone Settings")
    spine_setting = ikr_asset_controller.get_bone_settings("Spine", 0)
    spine_setting.rotation_stiffness = 1
    spine1_setting = ikr_asset_controller.get_bone_settings("Spine1", 0)
    spine1_setting.rotation_stiffness = 1

    # other bone settings
    LeftShoulder_setting = ikr_asset_controller.get_bone_settings("LeftShoulder", 0)
    LeftShoulder_setting.rotation_stiffness = 1

    RightShoulder_setting = ikr_asset_controller.get_bone_settings("RightShoulder", 0)
    RightShoulder_setting.rotation_stiffness = 1

    LeftForeArm_setting = ikr_asset_controller.get_bone_settings("LeftForeArm", 0)
    LeftForeArm_setting.use_preferred_angles  = True
    LeftForeArm_setting.preferred_angles = unreal.Vector(0,0,90)

    RightForeArm_setting = ikr_asset_controller.get_bone_settings("RightForeArm", 0)
    RightForeArm_setting.use_preferred_angles  = True
    RightForeArm_setting.preferred_angles = unreal.Vector(0,90,0)

    LeftLeg_setting = ikr_asset_controller.get_bone_settings("LeftLeg", 0)
    LeftLeg_setting.use_preferred_angles  = True
    LeftLeg_setting.preferred_angles = unreal.Vector(0,-90,0)

    RightLeg_setting = ikr_asset_controller.get_bone_settings("RightLeg", 0)
    RightLeg_setting.use_preferred_angles  = True
    RightLeg_setting.preferred_angles = unreal.Vector(0,-90,0)

    # Set the FBIK Attributes
    unreal.log(log_indexer + ": " + "Set IK Solver")
    fbik = ikr_asset_controller.get_solver_at_index(fbik_index)
    fbik.root_behavior=unreal.PBIKRootBehavior.PRE_PULL
    # fbik.allow_stretch=True

    # Set the Root Bone solver
    unreal.log(log_indexer + ": " + "Set Root Bone")
    ikr_asset_controller.set_root_bone("Hips", 0)

    # Set the Retarget Root
    unreal.log(log_indexer + ": " + "Set Retarget Root")
    ikr_asset_controller.set_retarget_root("Hips")

    # Set the Retargetting Chains
    ikr_asset_controller.add_retarget_chain("Spine","Spine","Spine1","")
    ikr_asset_controller.add_retarget_chain("Neck","Neck","Neck","")
    ikr_asset_controller.add_retarget_chain("Head","Head","Head","")
    ikr_asset_controller.add_retarget_chain("LeftClavicle","LeftShoulder","LeftShoulder","")
    ikr_asset_controller.add_retarget_chain("LeftArm","LeftArm","LeftHand_end","LeftArm_Goal")
    ikr_asset_controller.add_retarget_chain("RightClavicle","RightClavicle","RightClavicle","")
    ikr_asset_controller.add_retarget_chain("RightArm","RightArm","RightHand_end","RightArm_Goal")
    ikr_asset_controller.add_retarget_chain("LeftLeg","LeftUpLeg","LeftToeBase","LeftLeg_Goal")
    ikr_asset_controller.add_retarget_chain("RightLeft","RightUpLeg","RightToeBase","RightLeg_Goal")

    # Save the Asset
    unreal.EditorAssetLibrary.save_asset(ikr.get_path_name())
    return ikr