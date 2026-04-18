/**
 * Copyright (c) 2022 LXRobotics GmbH.
 * Author: Alexander Entinger <alexander.entinger@lxrobotics.com>
 * Contributors: https://github.com/107-systems/l3xz_sweep_scanner/graphs/contributors.
 */

/**************************************************************************************
 * INCLUDE
 **************************************************************************************/

#include <l3xz_sweep_scanner/SweepScannerNode.hpp>

/**************************************************************************************
 * MAIN
 **************************************************************************************/

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);

  auto node = std::make_shared<SweepScannerNode>();

  try
  {
    rclcpp::spin(node);
    rclcpp::shutdown();
    return EXIT_SUCCESS;
  }
  catch(std::runtime_error const & e)
  {
    RCLCPP_ERROR(rclcpp::get_logger(node->get_name()), "%s", e.what());
    return EXIT_FAILURE;
  }
  catch(...)
  {
    RCLCPP_ERROR(rclcpp::get_logger(node->get_name()), "Unhandled exception caught.");
    return EXIT_FAILURE;
  }
}
