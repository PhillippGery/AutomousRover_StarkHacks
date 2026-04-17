/**
 * Copyright (c) 2022 LXRobotics GmbH.
 * Author: Alexander Entinger <alexander.entinger@lxrobotics.com>, Jonas Wuehr
 * Contributors: https://github.com/107-systems/l3xz_teleop/graphs/contributors.
 */

#ifndef SWEEP_SCANNER_NODE
#define SWEEP_SCANNER_NODE

/**************************************************************************************
 * INCLUDE
 **************************************************************************************/

#include <rclcpp/rclcpp.hpp>

#include <sensor_msgs/msg/laser_scan.hpp>

#include <sweep/sweep.hpp>

#include <string>

/**************************************************************************************
 * CLASS DECLARATION
 **************************************************************************************/

class SweepScannerNode : public rclcpp::Node
{
public:
    SweepScannerNode();
   ~SweepScannerNode();

private:
  rclcpp::Publisher<sensor_msgs::msg::LaserScan>::SharedPtr _lidar_pub;
   
  std::string _frame_id;
  int _rotation_speed, _sample_rate;

  std::shared_ptr<sweep::sweep> _scanner;

  std::thread _scanner_thread;
  std::atomic<bool> _scanner_thread_active;

  void scannerThreadFunc();
};

#endif // SWEEP_SCANNER_NODE
