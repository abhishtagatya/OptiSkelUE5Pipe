from datetime import datetime

import unreal

def console_log(message, indexer="Default"):
    unreal.log(f"[{indexer}]: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {message}")

def auto_skm_to_ikr(skm, fpathext="Rigs"):
    """
    Automate Creating IK Rigs for a Skeletal Mesh
    
    :param skm: Skeletal Mesh Asset
    :param fpathext: (Optional) Folder Name
    """
    log_indexer = "AutoSKM2IKR-Python"

    fname = unreal.EditorAssetLibrary.get_fname(skm)
    fpath = unreal.EditorAssetLibrary.get_path_name(skm).split(".")[0].replace(str(fname),"")

    # Use the asset tools
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    # Create the IK Rig Asset
    console_log(message="Creating IK Rig Asset", indexer=log_indexer)
    ikr = asset_tools.create_asset(asset_name='IKR_{0}'.format(fname),
        package_path=fpath + fpathext, asset_class=unreal.IKRigDefinition,
        factory=unreal.IKRigDefinitionFactory())
    
    # Get the IK Rig Asset Controller
    console_log(message="Controlling IK Rig Asset", indexer=log_indexer)
    ikr_asset_controller = unreal.IKRigController.get_controller(ikr)
    ikr_asset_controller.set_skeletal_mesh(skm)
    fbik_index = ikr_asset_controller.add_solver(unreal.IKRigFBIKSolver)

    # Set IK Goals
    console_log(message="Creating IK Goals", indexer=log_indexer)
    ikr_asset_controller.add_new_goal("LeftArm_Goal", "LeftHand")
    ikr_asset_controller.add_new_goal("RightArm_Goal", "RightHand")
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
    console_log(message="Adjusting Bone Settings", indexer=log_indexer)
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
    LeftForeArm_setting.use_preferred_angles = True
    LeftForeArm_setting.preferred_angles = unreal.Vector(0,0,90)

    RightForeArm_setting = ikr_asset_controller.get_bone_settings("RightForeArm", 0)
    RightForeArm_setting.use_preferred_angles = True
    RightForeArm_setting.preferred_angles = unreal.Vector(0,90,0)

    LeftLeg_setting = ikr_asset_controller.get_bone_settings("LeftLeg", 0)
    LeftLeg_setting.use_preferred_angles = True
    LeftLeg_setting.preferred_angles = unreal.Vector(0,-90,0)

    RightLeg_setting = ikr_asset_controller.get_bone_settings("RightLeg", 0)
    RightLeg_setting.use_preferred_angles = True
    RightLeg_setting.preferred_angles = unreal.Vector(0,-90,0)

    # Set the FBIK Attributes
    console_log(message="Setting IK Solver", indexer=log_indexer)
    fbik = ikr_asset_controller.get_solver_at_index(fbik_index)
    fbik.root_behavior=unreal.PBIKRootBehavior.PRE_PULL
    fbik.allow_stretch=True

    # Set the Root Bone solver
    console_log(message="Setting Retarget Root Bone", indexer=log_indexer)
    ikr_asset_controller.set_root_bone("Hips", 0)

    # Set the Retarget Root
    ikr_asset_controller.set_retarget_root("Hips")

    # Set the Retargetting Chains
    ikr_asset_controller.add_retarget_chain("Spine","Spine","Spine1","")
    ikr_asset_controller.add_retarget_chain("Neck","Neck","Neck","")
    ikr_asset_controller.add_retarget_chain("Head","Head","Head","")

    ikr_asset_controller.add_retarget_chain("LeftClavicle","LeftShoulder","LeftShoulder","")
    ikr_asset_controller.add_retarget_chain("RightClavicle","RightShoulder","RightShoulder","")

    ikr_asset_controller.add_retarget_chain("LeftArm","LeftArm","LeftHand","LeftArm_Goal")
    ikr_asset_controller.add_retarget_chain("RightArm","RightArm","RightHand","RightArm_Goal")

    ikr_asset_controller.add_retarget_chain("LeftLeg","LeftUpLeg","LeftToeBase","LeftLeg_Goal")
    ikr_asset_controller.add_retarget_chain("RightLeg","RightUpLeg","RightToeBase","RightLeg_Goal")

    # Save the Asset
    console_log(message="Finished Successfully", indexer=log_indexer)
    unreal.EditorAssetLibrary.save_asset(ikr.get_path_name())
    return ikr

def create_pin_bone_item(bone_to, bone_from):
    pbd = unreal.PinBoneData()
    pbd.set_editor_property("bone_to_pin", bone_to)
    pbd.set_editor_property("bone_to_pin_to", bone_from)
    return pbd


def auto_ikr_to_rtg(ikr_source, ikr_target, rotator_source, rotator_target, fpathext="Retargets"):
    """
    Automate Creating Retarget Asset for a IK's
    
    :param ikr_source: IKR Source
    :param ikr_target: IKR Target
    :param rotator_source: Source Rotator
    :param rotator_target: Target Rotator
    :param fpathext: (Optional) Folder Name
    """
    log_indexer = "AutoRetarget-Python"

    fname_source = unreal.EditorAssetLibrary.get_fname(ikr_source)
    fname_target = unreal.EditorAssetLibrary.get_fname(ikr_target)
    fpath_source = unreal.EditorAssetLibrary.get_path_name(ikr_source).split(".")[0].replace(str(fname_source),"")

    source_name = str(fname_source).split("_")[1]
    target_name = str(fname_target).split("_")[1]

    # Use the asset tools
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    # Create the IK Rig Asset
    console_log(message="Creating RTG Asset", indexer=log_indexer)
    rtg = asset_tools.create_asset(asset_name='RTG_{0}-{1}'.format(source_name, target_name), 
        package_path=fpath_source + fpathext, asset_class=unreal.IKRetargeter, 
        factory=unreal.IKRetargetFactory())
    
    # Get the IK Rig Asset Controller
    console_log(message="Controlling Retarget Asset", indexer=log_indexer)
    rtg_asset_controller = unreal.IKRetargeterController.get_controller(rtg)
    rtg_asset_controller.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, ikr_source)
    rtg_asset_controller.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, ikr_target)

    console_log(message="Auto Mapping Chains", indexer=log_indexer)
    rtg_asset_controller.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)

    ignore_chain_list = [
        'Root', 
        # Left Fingers
        'LeftMiddleMetacarpal', 'LeftMiddle',
        'LeftPinkyMetacarpal', 'LeftPinky',
        'LeftRingMetacarpal', 'LeftRing',
        'LeftIndexMetacarpal', 'LeftIndex',
        'LeftThumb',
        # Right Fingers
        'RightMiddleMetacarpal', 'RightMiddle',
        'RightPinkyMetacarpal', 'RightPinky',
        'RightRingMetacarpal', 'RightRing',
        'RightIndexMetacarpal', 'RightIndex',
        'RightThumb',
    ]
    for item in ignore_chain_list:
        rtg_asset_controller.set_source_chain("None", item)

    # Rotating Root Offset
    console_log(message="Setting Rotation Offset for Root", indexer=log_indexer)
    rtg_asset_controller.set_rotation_offset_for_retarget_pose_bone("Hips", rotator_source.quaternion(), unreal.RetargetSourceOrTarget.SOURCE)
    rtg_asset_controller.set_rotation_offset_for_retarget_pose_bone("root", rotator_target.quaternion(), unreal.RetargetSourceOrTarget.TARGET)

    # Auto Align Bones
    console_log(message="Auto Aligning Bones to Target", indexer=log_indexer)

    rtg_asset_controller.auto_align_all_bones(unreal.RetargetSourceOrTarget.TARGET)
    
    # Clavicle to Hand Group
    #rtg_asset_controller.auto_align_bones(["LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand", "LeftHand_end"], unreal.RetargetAutoAlignMethod.CHAIN_TO_CHAIN, unreal.RetargetSourceOrTarget.SOURCE)
    #rtg_asset_controller.auto_align_bones(["RightShoulder", "RightArm", "RightForeArm", "RightHand", "RightHand_end"], unreal.RetargetAutoAlignMethod.CHAIN_TO_CHAIN, unreal.RetargetSourceOrTarget.SOURCE)

    # Leg to Toe Group
    #rtg_asset_controller.auto_align_bones(["LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase", "LeftHand_end"], unreal.RetargetAutoAlignMethod.CHAIN_TO_CHAIN, unreal.RetargetSourceOrTarget.SOURCE)
    #rtg_asset_controller.auto_align_bones(["RightUpLeg", "RightLeg", "RightFoot", "RightToeBase", "RightHand_end"], unreal.RetargetAutoAlignMethod.CHAIN_TO_CHAIN, unreal.RetargetSourceOrTarget.SOURCE)

    # Spine to Head Group
    #rtg_asset_controller.auto_align_bones(["Spine", "Spine1", "Neck", "Head"], unreal.RetargetAutoAlignMethod.CHAIN_TO_CHAIN, unreal.RetargetSourceOrTarget.SOURCE)

    # Add Retarget Op: Root Motion Generator
    console_log(message="Adding Retarget Operation: Root Motion", indexer=log_indexer)
    rmg_op_index = rtg_asset_controller.add_retarget_op(
        unreal.RootMotionGeneratorOp
    )
    rtg_rmg_op = rtg_asset_controller.get_retarget_op_at_index(rmg_op_index)
    
    rtg_rmg_op.set_editor_property("source_root_bone", "Hips")
    rtg_rmg_op.set_editor_property("target_root_bone", "root")
    rtg_rmg_op.set_editor_property("target_pelvis_bone", "pelvis")

    rtg_rmg_op.set_editor_property(
        "root_motion_source",
        unreal.RootMotionSource.GENERATE_FROM_TARGET_PELVIS
    )

    rtg_rmg_op.set_editor_property(
        "root_height_source",
        unreal.RootMotionHeightSource.SNAP_TO_GROUND
    )

    rtg_rmg_op.set_editor_property("rotate_with_pelvis", True)

    # Add Retarget Op: Pin Bones
    console_log(message="Adding Retarget Operation: Pin Bones", indexer=log_indexer)
    rtg_pb_index = rtg_asset_controller.add_retarget_op(
        unreal.PinBoneOp
    )
    rtg_pb_op = rtg_asset_controller.get_retarget_op_at_index(rtg_pb_index)

    rtg_pb_op.set_editor_property(
        "bones_to_pin",
        [
            create_pin_bone_item("ik_foot_root", "root"),
            create_pin_bone_item("ik_foot_l", "foot_l"),
            create_pin_bone_item("ik_foot_r", "foot_r"),
            create_pin_bone_item("ik_hand_root", "root"),
            create_pin_bone_item("ik_hand_gun", "hand_r"),
            create_pin_bone_item("ik_hand_l", "hand_l"),
            create_pin_bone_item("ik_hand_r", "hand_r"),
        ]
    )

    rtg_pb_op.set_editor_property(
        "pin_to",
        unreal.RetargetSourceOrTarget.TARGET
    )

    rtg_pb_op.set_editor_property(
        "pin_type",
        unreal.PinBoneType.FULL_TRANSFORM
    )

    rtg_pb_op.set_editor_property("maintain_offset", False)

    console_log(message="Finished Successfully", indexer=log_indexer)
    unreal.EditorAssetLibrary.save_asset(rtg.get_path_name())
    return rtg

