#include <Arduino.h>
#include "PIDController.h"

#define BOARD_ID "FRONT"

// =============================================================================
// PIN DEFINITIONS — ESP32 Feather V2, FRONT board
// =============================================================================
// Front Left (M1)
const int ENCODER_FL_A = 34;
const int ENCODER_FL_B = 39;
const int PWM_FL       = 25;
const int DIR_FL       = 26;
const int PWM_CH_FL    = 0;

// Front Right (M2)
const int ENCODER_FR_A = 15;
const int ENCODER_FR_B = 32;
const int PWM_FR       = 33;
const int DIR_FR       = 27;
const int PWM_CH_FR    = 1;

// =============================================================================
// ENCODER CPR (counts per wheel rev — tune to match REAR)
// =============================================================================
const float CPR = 4.0f;

// =============================================================================
// ENCODER TICKS (cumulative, sent to host)
// =============================================================================
volatile long ticks_M1 = 0;  long prev_ticks_M1 = 0;
volatile long ticks_M2 = 0;  long prev_ticks_M2 = 0;

// =============================================================================
// VELOCITY FILTERS
// =============================================================================
float vel_history_M1[4] = {0,0,0,0};  int vel_index_M1 = 0;
float vel_history_M2[4] = {0,0,0,0};  int vel_index_M2 = 0;

// =============================================================================
// PID CONTROLLERS — same gains as REAR
// =============================================================================
PIDController pidM1(0.05f, 0.2f, 0.0f, 0.005f, 15000.0f);
PIDController pidM2(0.05f, 0.2f, 0.0f, 0.005f, 15000.0f);

// =============================================================================
// TARGETS (ticks/sec) — set via serial
// =============================================================================
float target_M1 = 0.0f;
float target_M2 = 0.0f;

float out_M1 = 0.0f;
float out_M2 = 0.0f;

// =============================================================================
// SERIAL PARSING
// =============================================================================
String input_string = "";
unsigned long last_msg_time = 0;

// =============================================================================
// HARDWARE TIMER — 5ms, matches REAR
// =============================================================================
hw_timer_t * timer = NULL;
volatile bool run_pid_flag = false;
void IRAM_ATTR onTimer() { run_pid_flag = true; }

// =============================================================================
// ENCODER ISRs
// =============================================================================
void IRAM_ATTR readEncoderM1() { if (digitalRead(ENCODER_FL_B)) ticks_M1--; else ticks_M1++; }
void IRAM_ATTR readEncoderM2() { if (digitalRead(ENCODER_FR_B)) ticks_M2++; else ticks_M2--; }

// =============================================================================
// VELOCITY HELPER
// =============================================================================
float computeVelocity(long cur, long &prev, float* history, int &index) {
  float raw = (cur - prev) / 0.005f;
  prev = cur;
  if (raw >  5000.0f) raw =  5000.0f;
  if (raw < -5000.0f) raw = -5000.0f;
  history[index] = raw;
  index = (index + 1) % 4;
  return (history[0] + history[1] + history[2] + history[3]) / 4.0f;
}

// =============================================================================
// TIMERS
// =============================================================================
unsigned long last_print_time = 0;
unsigned long last_heartbeat  = 0;

// =============================================================================
// SETUP
// =============================================================================
void setup() {
  Serial.begin(115200);

  // Encoders
  pinMode(ENCODER_FL_A, INPUT_PULLUP); pinMode(ENCODER_FL_B, INPUT_PULLUP);
  pinMode(ENCODER_FR_A, INPUT_PULLUP); pinMode(ENCODER_FR_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_FL_A), readEncoderM1, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_FR_A), readEncoderM2, RISING);

  // Motors
  pinMode(DIR_FL, OUTPUT); pinMode(DIR_FR, OUTPUT);
  ledcSetup(PWM_CH_FL, 5000, 8); ledcAttachPin(PWM_FL, PWM_CH_FL);
  ledcSetup(PWM_CH_FR, 5000, 8); ledcAttachPin(PWM_FR, PWM_CH_FR);
  ledcWrite(PWM_CH_FL, 0);
  ledcWrite(PWM_CH_FR, 0);

  // 5ms hardware timer
  timer = timerBegin(0, 80, true);
  timerAttachInterrupt(timer, &onTimer, true);
  timerAlarmWrite(timer, 5000, true);
  timerAlarmEnable(timer);

  last_msg_time = millis();
  Serial.println(BOARD_ID " ready");
}

// =============================================================================
// LOOP
// =============================================================================
void loop() {

  // --- 1. RECEIVE COMMANDS: "M1:xxx M2:xxx\n" (ticks/sec) ---
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      int v1, v2;
      if (sscanf(input_string.c_str(), "M1:%d M2:%d", &v1, &v2) == 2) {
        target_M1 = (float)v1;
        target_M2 = (float)v2;
        last_msg_time = millis();
      }
      input_string = "";
    } else {
      input_string += c;
    }
  }

  // --- 1b. SAFETY STOP ---
  if (millis() - last_msg_time > 500) {
    target_M1 = 0.0f;
    target_M2 = 0.0f;
  }

  // --- 2. FAST PID LOOP (every 5ms) ---
  if (run_pid_flag) {
    run_pid_flag = false;

    noInterrupts();
    long cur_M1 = ticks_M1;
    long cur_M2 = ticks_M2;
    interrupts();

    float vel_M1 = computeVelocity(cur_M1, prev_ticks_M1, vel_history_M1, vel_index_M1);
    float vel_M2 = computeVelocity(cur_M2, prev_ticks_M2, vel_history_M2, vel_index_M2);

    out_M1 = (target_M1 == 0.0f) ? 0.0f : pidM1.compute(target_M1, vel_M1);
    out_M2 = (target_M2 == 0.0f) ? 0.0f : pidM2.compute(target_M2, vel_M2);

    out_M1 = constrain(out_M1, -255.0f, 255.0f);
    out_M2 = constrain(out_M2, -255.0f, 255.0f);

    // M1 (FL): forward = LOW
    digitalWrite(DIR_FL, out_M1 >= 0 ? LOW : HIGH);
    ledcWrite(PWM_CH_FL, (int)abs(out_M1));

    // M2 (FR): inverted — forward = HIGH
    digitalWrite(DIR_FR, out_M2 >= 0 ? HIGH : LOW);
    ledcWrite(PWM_CH_FR, (int)abs(out_M2));
  }

  // --- 3. SEND CUMULATIVE TICKS TO HOST (every 50ms) ---
  if (millis() - last_print_time >= 50) {
    last_print_time = millis();
    Serial.printf("ENC:M1:%ld M2:%ld\n", ticks_M1, ticks_M2);
  }

  // --- 4. HEARTBEAT (every 2s) ---
  if (millis() - last_heartbeat >= 2000) {
    last_heartbeat = millis();
    Serial.println(BOARD_ID " alive");
  }
}
