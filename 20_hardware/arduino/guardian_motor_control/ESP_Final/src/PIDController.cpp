#include "PIDController.h"

PIDController::PIDController(float p, float i, float d, float dt, float max_i) {
    Kp = p; Ki = i; Kd = d;
    iteration_time = dt; max_integral = max_i;
    integral = 0.0f; error_prior = 0.0f;
}

float PIDController::compute(float desired_velocity, float actual_velocity) {
    float error = desired_velocity - actual_velocity;
    integral = integral + (error * iteration_time);

    if (integral > max_integral) integral = max_integral;
    else if (integral < -max_integral) integral = -max_integral;

    float derivative = (error - error_prior) / iteration_time;

    float output = (Kp * error) + (Ki * integral) + (Kd * derivative);
    error_prior = error;

    return output;
}