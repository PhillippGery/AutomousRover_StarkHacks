/**
 * Copyright (c) 2022 LXRobotics GmbH.
 * Author: Alexander Entinger <alexander.entinger@lxrobotics.com>, Jonas Wuehr
 * Contributors: https://github.com/107-systems/l3xz_teleop/graphs/contributors.
 */

/**************************************************************************************
 * INCLUDE
 **************************************************************************************/

#include <l3xz_sweep_scanner/SweepScannerNode.hpp>

/**************************************************************************************
 * CTOR/DTOR
 **************************************************************************************/

SweepScannerNode::SweepScannerNode() try
: Node("l3xz_sweep_scanner")
, _scanner_thread{}
, _scanner_thread_active{false}
{
  declare_parameter("topic", "laser");
  declare_parameter("serial_port", "/dev/ttyUSB0");
  declare_parameter("rotation_speed", 1);
  declare_parameter("sample_rate", 500);
  declare_parameter("frame_id", "laser_frame");

  std::string const topic       = get_parameter("topic").as_string();
  std::string const serial_port = get_parameter("serial_port").as_string();
                      _frame_id = get_parameter("frame_id").as_string();
                _rotation_speed = get_parameter("rotation_speed").as_int();
                   _sample_rate = get_parameter("sample_rate").as_int();

  RCLCPP_INFO(get_logger(),
              "node config:\n  topic: %s\n  port : %s\n  speed: %d Hz\n  rate : %d Hz\n  frame: %s",
              topic.c_str(), serial_port.c_str(), _rotation_speed, _sample_rate, _frame_id.c_str());

  _scanner = std::make_shared<sweep::sweep>(serial_port.c_str());

  _lidar_pub = create_publisher<sensor_msgs::msg::LaserScan>(topic, 10);

  _scanner_thread = std::thread([this]() { this->scannerThreadFunc(); });
}
catch(sweep::device_error const & e)
{
  RCLCPP_ERROR(get_logger(), "%s", e.what());
}

SweepScannerNode::~SweepScannerNode()
{
  _scanner_thread_active = false;
  _scanner_thread.join();
}

/**************************************************************************************
 * PRIVATE MEMBER FUNCTIONS
 **************************************************************************************/

void SweepScannerNode::scannerThreadFunc() try
{
  _scanner_thread_active = true;

  RCLCPP_INFO(get_logger(), "configuring scanse sweep.");
  _scanner->set_motor_speed(_rotation_speed);

  while(!_scanner->get_motor_ready())
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

  _scanner->set_sample_rate(_sample_rate);
  _scanner->start_scanning();

  RCLCPP_INFO(get_logger(), "starting data acquisition.");

  while (_scanner_thread_active)
  {
    /* Obtain a full scan. */
    sweep::scan const scan = _scanner->get_scan();

    sensor_msgs::msg::LaserScan laser_scan_msg;
    /* Populate sensor_msgs/LaserScan header. */
    laser_scan_msg.header.frame_id = _frame_id;

    /* Populate sensor_msgs/LaserScan data. */
    float const samples_per_rotation = static_cast<float>(_sample_rate) / static_cast<float>(_rotation_speed);

    laser_scan_msg.angle_min       = 0.0;
    laser_scan_msg.angle_max       = 2.0 * M_PI;
    laser_scan_msg.angle_increment = laser_scan_msg.angle_max / samples_per_rotation;
    laser_scan_msg.time_increment  = 1.0 / static_cast<float>(_sample_rate);
    laser_scan_msg.range_min       = 0.0;
    laser_scan_msg.range_max       = 40.0;

    laser_scan_msg.ranges.assign(scan.samples.size(), std::numeric_limits<float>::infinity());

    size_t idx = 0;
    for (auto [angle_milli_deg, distance_cm, signal_strength] : scan.samples) {
      laser_scan_msg.ranges[idx] = static_cast<float>(distance_cm) / 100.0;
      idx++;
    }

    /* Publish the laser scan. */
    _lidar_pub->publish(laser_scan_msg);
  }

  _scanner->stop_scanning();
}
catch(sweep::device_error const & e)
{
  RCLCPP_ERROR(get_logger(), "%s", e.what());
  _scanner->stop_scanning();
}
