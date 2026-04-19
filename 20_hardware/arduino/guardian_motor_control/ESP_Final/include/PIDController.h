#pragma once

class PIDController {
  private:
    float Kp, Ki, Kd;
    float integral;
    float error_prior;
    float iteration_time;
    float max_integral;

  public:
    PIDController(float p, float i, float d, float dt, float max_i);
    float compute(float desired_velocity, float actual_velocity);
};