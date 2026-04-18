#include <Arduino.h>
#include "PIDController.h"

// =============================================================================
// PIN DEFINITIONS — ESP32 Feather V2, FRONT board
// =============================================================================
// Front Left (M1)
const int ENCODER_FL_A = 34; 
const int ENCODER_FL_B = 39;
const int PWM_FL = 25;       
const int DIR_FL = 26;       
const int PWM_CH_FL = 0;

// Front Right (M2)
const int ENCODER_FR_A = 15; 
const int ENCODER_FR_B = 32;
const int PWM_FR = 33;       
const int DIR_FR = 27;       
const int PWM_CH_FR = 1;

// =============================================================================
// ENCODER TICKS
// =============================================================================
volatile long ticks_FL = 0; long prev_ticks_FL = 0;
volatile long ticks_FR = 0; long prev_ticks_FR = 0;

// =============================================================================
// VELOCITY FILTERS
// =============================================================================
float vel_history_FL[4] = {0, 0, 0, 0}; int vel_index_FL = 0;
float vel_history_FR[4] = {0, 0, 0, 0}; int vel_index_FR = 0;

// =============================================================================
// PID CONTROLLERS — Tuned for 20ms Loop
// =============================================================================
// Kp = 0.02, Ki = 0.005, Kd = 0.0, dt = 0.02
PIDController pidFL(0.05f, 0.005f, 0.0f, 0.02f, 15000.0f);
PIDController pidFR(0.05f, 0.005f, 0.0f, 0.02f, 15000.0f);

// =============================================================================
// TARGET SPEEDS (ticks/sec)
// =============================================================================
float target_FL = 0.0f; // Spin at a healthy speed
float target_FR = 0.0f;    // Test the deadband (should be dead silent)

// =============================================================================
// HARDWARE TIMER
// =============================================================================
hw_timer_t * timer = NULL;
volatile bool run_pid_flag = false;
void IRAM_ATTR onTimer() { run_pid_flag = true; }

// =============================================================================
// ENCODER ISRs
// =============================================================================
void IRAM_ATTR readEncoderFL() { if (digitalRead(ENCODER_FL_B)) ticks_FL--; else ticks_FL++; }
void IRAM_ATTR readEncoderFR() { if (digitalRead(ENCODER_FR_B)) ticks_FR++; else ticks_FR--; }

// =============================================================================
// TIMERS
// =============================================================================
unsigned long last_print_time = 0;

// =============================================================================
// VELOCITY HELPER
// =============================================================================
float computeVelocity(long cur, long &prev, float* history, int &index) {
  float raw = (cur - prev) / 0.02f; // Matched to 20ms timer
  prev = cur;
  if (raw >  5000.0f) raw =  5000.0f;
  if (raw < -5000.0f) raw = -5000.0f;
  history[index] = raw;
  index = (index + 1) % 4;
  return (history[0] + history[1] + history[2] + history[3]) / 4.0f;
}

// =============================================================================
// SETUP
// =============================================================================
void setup() {
  Serial.begin(115200);
  Serial.println("=== 2 Motor PID Test (FL + FR) ===");
  Serial.println("time_ms,target_FL,vel_FL,pwm_FL,target_FR,vel_FR,pwm_FR");

  // Encoder pins
  pinMode(ENCODER_FL_A, INPUT_PULLUP); pinMode(ENCODER_FL_B, INPUT_PULLUP);
  pinMode(ENCODER_FR_A, INPUT_PULLUP); pinMode(ENCODER_FR_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_FL_A), readEncoderFL, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_FR_A), readEncoderFR, RISING);

  // Motor pins
  pinMode(DIR_FL, OUTPUT); pinMode(DIR_FR, OUTPUT);
  ledcSetup(PWM_CH_FL, 5000, 8); ledcAttachPin(PWM_FL, PWM_CH_FL);
  ledcSetup(PWM_CH_FR, 5000, 8); ledcAttachPin(PWM_FR, PWM_CH_FR);

  // Stop both motors on boot
  ledcWrite(PWM_CH_FL, 0);
  ledcWrite(PWM_CH_FR, 0);

  // 20ms hardware timer
  timer = timerBegin(0, 80, true);
  timerAttachInterrupt(timer, &onTimer, true);
  timerAlarmWrite(timer, 20000, true);
  timerAlarmEnable(timer);
}

// =============================================================================
// LOOP
// =============================================================================
void loop() {
  if (run_pid_flag) {
    run_pid_flag = false;

    // 1. Safely read ticks
    noInterrupts();
    long cur_FL = ticks_FL;
    long cur_FR = ticks_FR;
    interrupts();

    // 2. Compute velocities
    float vel_FL = computeVelocity(cur_FL, prev_ticks_FL, vel_history_FL, vel_index_FL);
    float vel_FR = computeVelocity(cur_FR, prev_ticks_FR, vel_history_FR, vel_index_FR);

    // 3. Run PID with Deadband
    float out_FL = 0.0f;
    float out_FR = 0.0f;

    if (target_FL == 0.0f) {
      out_FL = 0.0f;
    } else {
      out_FL = pidFL.compute(target_FL, vel_FL); // Restored!
    }

    if (target_FR == 0.0f) {
      out_FR = 0.0f;
    } else {
      out_FR = pidFR.compute(target_FR, vel_FR); // Restored!
    }

    // 4. Constrain outputs securely
    out_FL = constrain(out_FL, -255.0f, 255.0f);
    out_FR = constrain(out_FR, -255.0f, 255.0f);

    // 5. Apply to motors (Bidirectional)
    // FL: forward = LOW
    digitalWrite(DIR_FL, out_FL >= 0 ? LOW : HIGH);
    ledcWrite(PWM_CH_FL, (int)abs(out_FL));      // Restored!

    // FR: inverted vs FL — forward = HIGH
    digitalWrite(DIR_FR, out_FR >= 0 ? HIGH : LOW); 
    ledcWrite(PWM_CH_FR, (int)abs(out_FR));      // Restored!

    // 6. Send encoder ticks to host every 50ms
    if (millis() - last_print_time >= 50) {
      last_print_time = millis();
      Serial.printf("ENC:M1:%ld M2:%ld\n", ticks_FL, ticks_FR);
    }
  }
}it