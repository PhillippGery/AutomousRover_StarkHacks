#include <Arduino.h>
#include "PIDController.h"

// =============================================================================
// PIN DEFINITIONS — ESP32 Feather V2, REAR board
// =============================================================================
// Back Left (BL) — Matches ROS "M1"
const int ENCODER_BL_A = 34;
const int ENCODER_BL_B = 39;
const int PWM_BL = 25;
const int DIR_BL = 26;
const int PWM_CH_BL = 0;

// Back Right (BR) — Matches ROS "M2"
const int ENCODER_BR_A = 15;
const int ENCODER_BR_B = 32;
const int PWM_BR = 33;
const int DIR_BR = 27;
const int PWM_CH_BR = 1;

// =============================================================================
// ENCODER TICKS
// =============================================================================
volatile long ticks_BL = 0; long prev_ticks_BL = 0;
volatile long ticks_BR = 0; long prev_ticks_BR = 0;

// =============================================================================
// VELOCITY FILTERS
// =============================================================================
float vel_history_BL[4] = {0, 0, 0, 0}; int vel_index_BL = 0;
float vel_history_BR[4] = {0, 0, 0, 0}; int vel_index_BR = 0;

// =============================================================================
// PID CONTROLLERS — Tuned for 20ms Loop
// =============================================================================
PIDController pidBL(0.1f, 0.02f, 0.0f, 0.02f, 15000.0f);
PIDController pidBR(0.1f, 0.02f, 0.0f, 0.02f, 15000.0f);

// =============================================================================
// TARGET SPEEDS (ticks/sec) — set via serial
// =============================================================================
float target_BL = 0.0f;
float target_BR = 0.0f;

// =============================================================================
// SERIAL PARSING
// =============================================================================
String input_string = "";
unsigned long last_msg_time = 0;

// =============================================================================
// HARDWARE TIMER
// =============================================================================
hw_timer_t * timer = NULL;
volatile bool run_pid_flag = false;
void IRAM_ATTR onTimer() { run_pid_flag = true; }

// =============================================================================
// ENCODER ISRs
// =============================================================================
// NOTE: If a wheel runs away to max speed, flip the ++ and -- here!
void IRAM_ATTR readEncoderBL() { if (digitalRead(ENCODER_BL_B)) ticks_BL++; else ticks_BL--; }
void IRAM_ATTR readEncoderBR() { if (digitalRead(ENCODER_BR_B)) ticks_BR++; else ticks_BR--; }

// =============================================================================
// TIMERS
// =============================================================================
unsigned long last_print_time = 0;

// =============================================================================
// VELOCITY HELPER
// =============================================================================
float computeVelocity(long cur, long &prev, float* history, int &index) {
  float raw = (cur - prev) / 0.02f;
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

  // Encoder pins
  pinMode(ENCODER_BL_A, INPUT_PULLUP); pinMode(ENCODER_BL_B, INPUT_PULLUP);
  pinMode(ENCODER_BR_A, INPUT_PULLUP); pinMode(ENCODER_BR_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_BL_A), readEncoderBL, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_BR_A), readEncoderBR, RISING);

  // Motor pins
  pinMode(DIR_BL, OUTPUT); pinMode(DIR_BR, OUTPUT);
  ledcSetup(PWM_CH_BL, 5000, 8); ledcAttachPin(PWM_BL, PWM_CH_BL);
  ledcSetup(PWM_CH_BR, 5000, 8); ledcAttachPin(PWM_BR, PWM_CH_BR);
  ledcWrite(PWM_CH_BL, 0);
  ledcWrite(PWM_CH_BR, 0);

  // 20ms hardware timer
  timer = timerBegin(0, 80, true);
  timerAttachInterrupt(timer, &onTimer, true);
  timerAlarmWrite(timer, 20000, true);
  timerAlarmEnable(timer);

  last_msg_time = millis();
  Serial.println("BACK ready");
}

// =============================================================================
// LOOP
// =============================================================================
void loop() {

  // --- 1. RECEIVE COMMANDS ---
  // Matches "M1:xxx M2:xxx\n" (M1 goes to BL, M2 goes to BR)
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      float v1, v2; 
      if (sscanf(input_string.c_str(), "M1:%f M2:%f", &v1, &v2) == 2) {
        // Convert the incoming RPM back into Ticks/Sec
        target_BL = (v1 / 60.0f) * 175.0f;
        target_BR = (v2 / 60.0f) * 175.0f;
        last_msg_time = millis();
      }
      input_string = "";
    } else {
      input_string += c;
    }
  }

  // --- 1b. SAFETY STOP (Relaxed 2000ms for Keyboard Teleop) ---
  if (millis() - last_msg_time > 2000) {
    target_BL = 0.0f;
    target_BR = 0.0f;
  }

  // --- 2. PID LOOP (every 20ms) ---
  if (run_pid_flag) {
    run_pid_flag = false;

    noInterrupts();
    long cur_BL = ticks_BL;
    long cur_BR = ticks_BR;
    interrupts();

    float vel_BL = computeVelocity(cur_BL, prev_ticks_BL, vel_history_BL, vel_index_BL);
    float vel_BR = computeVelocity(cur_BR, prev_ticks_BR, vel_history_BR, vel_index_BR);

    // --- Motor 1 (Back Left) Deadband & Minimum Power ---
    float out_BL = 0.0f;
    if (abs(target_BL) < 2.0f) {
      out_BL = 0.0f; 
    } else {
      out_BL = pidBL.compute(target_BL, vel_BL);
      if (target_BL > 0.0f) out_BL += 25.0f; 
      if (target_BL < 0.0f) out_BL -= 25.0f; 
    }

    // --- Motor 2 (Back Right) Deadband & Minimum Power ---
    float out_BR = 0.0f;
    if (abs(target_BR) < 2.0f) {
      out_BR = 0.0f; 
    } else {
      out_BR = pidBR.compute(target_BR, vel_BR);
      if (target_BR > 0.0f) out_BR += 25.0f; 
      if (target_BR < 0.0f) out_BR -= 25.0f; 
    }

    out_BL = constrain(out_BL, -255.0f, 255.0f);
    out_BR = constrain(out_BR, -255.0f, 255.0f);

    // BL: forward = LOW
    digitalWrite(DIR_BL, out_BL >= 0 ? LOW : HIGH);
    ledcWrite(PWM_CH_BL, (int)abs(out_BL));

    // BR: inverted vs BL — forward = HIGH
    digitalWrite(DIR_BR, out_BR >= 0 ? HIGH : LOW);
    ledcWrite(PWM_CH_BR, (int)abs(out_BR));

    // --- 3. SEND CUMULATIVE TICKS TO HOST (every 50ms) ---
    // Sends M1 and M2 so ROS knows what it is looking at
    if (millis() - last_print_time >= 50) {
      last_print_time = millis();
      Serial.printf("ENC:M1:%ld M2:%ld\n", ticks_BL, ticks_BR);
    }
  }
}