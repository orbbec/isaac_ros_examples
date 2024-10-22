# SPDX-FileCopyrightText: NVIDIA CORPORATION & AFFILIATES
# Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import os
from typing import Any, Dict

from ament_index_python import get_package_share_directory
from isaac_ros_examples import IsaacROSLaunchFragment
import launch
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import rclpy
from launch.actions import GroupAction, OpaqueFunction

WIDTH = 1280
HEIGHT = 720


class IsaacROSOrbbecMonoRectDepthLaunchFragment(IsaacROSLaunchFragment):

    @staticmethod
    def get_interface_specs() -> Dict[str, Any]:
        return {
            'camera_resolution': {'width': 640, 'height': 480},
            'camera_frame': 'camera_color_optical_frame',
            'focal_length': {
                # Approximation - most RealSense cameras should be close to this value
                'f_x': 366.0,
                # Approximation - most RealSense cameras should be close to this value
                'f_y': 366.0
            }
        }

    @staticmethod
    def get_composable_nodes(interface_specs: Dict[str, Any]) -> Dict[str, ComposableNode]:
        orbbec_config_file_path = os.path.join(
            get_package_share_directory('isaac_ros_orbbec'),
            'config', 'camera_params.yaml'
        )

        return {
            'camera_node': ComposableNode(
                package='orbbec_camera',
                plugin='orbbec_camera::OBCameraNodeDriver',
                name='orbbec_camera',
                namespace='',
                parameters=[
                    orbbec_config_file_path
                ],
                remappings=[
                            ('color/image_raw', 'image_rect'),
                            ('color/camera_info', 'camera_info_rect'),
                            ('depth/image_raw', 'aligned_depth_to_color/image_raw'),
                           ]
            ),
            # Orbbec depth is in uint16 and millimeters. Convert to float32 and meters
            'convert_metric_node': ComposableNode(
                package='isaac_ros_depth_image_proc',
                plugin='nvidia::isaac_ros::depth_image_proc::ConvertMetricNode',
                name='convert_metric',
                remappings=[
                    ('image_raw', 'aligned_depth_to_color/image_raw'),
                    ('image', 'depth')
                ]
            ),
        }

    # @staticmethod
    # def get_launch_actions(interface_specs: Dict[str, Any]) -> \
    #         Dict[str, launch.actions.OpaqueFunction]:

    #   package_dir = get_package_share_directory('orbbec_camera')
    #   launch_file_dir = os.path.join(package_dir, 'launch')
    #   config_file_dir = os.path.join(package_dir, 'config')
    #   config_file_path = os.path.join(config_file_dir, 'camera_params.yaml')

    #   orbbec_camera_launch_no_compose = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(launch_file_dir, 'gemini_330_series.launch.py')
    #     ),
    #     launch_arguments={
    #         'camera_name': 'orbbec_camera',
    #         'config_file_path': config_file_path,
    #     }.items()
    #   )

    #   def launch_orbbec_camera(context, *args, **kwargs):
    #       return [GroupAction([orbbec_camera_launch_no_compose])]

    #   return {
    #       'orbbec_camera_launch_no_compose': OpaqueFunction(function=launch_orbbec_camera)
    #   }

def generate_launch_description():
    return launch.LaunchDescription(
      )
