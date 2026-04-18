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
PIDController pidFL(2.0f, 0.1f, 0.0f, 0.02f, 15000.0f);
PIDController pidFR(2.0f, 0.1f, 0.0f, 0.02f, 15000.0f);

// =============================================================================
// TARGET SPEEDS (ticks/sec) — set via serial
// =============================================================================
float target_FL = 0.0f;
float target_FR = 0.0f;

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
  pinMode(ENCODER_FL_A, INPUT_PULLUP); pinMode(ENCODER_FL_B, INPUT_PULLUP);
  pinMode(ENCODER_FR_A, INPUT_PULLUP); pinMode(ENCODER_FR_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_FL_A), readEncoderFL, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_FR_A), readEncoderFR, RISING);

  // Motor pins
  pinMode(DIR_FL, OUTPUT); pinMode(DIR_FR, OUTPUT);
  ledcSetup(PWM_CH_FL, 5000, 8); ledcAttachPin(PWM_FL, PWM_CH_FL);
  ledcSetup(PWM_CH_FR, 5000, 8); ledcAttachPin(PWM_FR, PWM_CH_FR);
  ledcWrite(PWM_CH_FL, 0);
  ledcWrite(PWM_CH_FR, 0);

  // 20ms hardware timer
  timer = timerBegin(0, 80, true);
  timerAttachInterrupt(timer, &onTimer, true);
  timerAlarmWrite(timer, 20000, true);
  timerAlarmEnable(timer);

  last_msg_time = millis();
  Serial.println("FRONT ready");
}

// =============================================================================
// LOOP
// =============================================================================
void loop() {

  // --- 1. RECEIVE COMMANDS: "M1:xxx M2:xxx\n" (ticks/sec) ---
  // --- 1. RECEIVE COMMANDS ---
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      float v1, v2; // <-- Change to floats!
      // Look for floats (%f) instead of ints (%d)
      if (sscanf(input_string.c_str(), "M1:%f M2:%f", &v1, &v2) == 2) {
        // Convert the incoming RPM back into Ticks/Sec
        target_FL = (v1 / 60.0f) * 700.0f;
        target_FR = (v2 / 60.0f) * 700.0f;
        last_msg_time = millis();
      }
      input_string = "";
    } else {
      input_string += c;
    }
  }

  // --- 1b. SAFETY STOP — no message for 500ms ---
  if (millis() - last_msg_time > 500) {
    target_FL = 0.0f;
    target_FR = 0.0f;
  }

  // --- 2. PID LOOP (every 20ms) ---
  if (run_pid_flag) {
    run_pid_flag = false;

    noInterrupts();
    long cur_FL = ticks_FL;
    long cur_FR = ticks_FR;
    interrupts();

    float vel_FL = computeVelocity(cur_FL, prev_ticks_FL, vel_history_FL, vel_index_FL);
    float vel_FR = computeVelocity(cur_FR, prev_ticks_FR, vel_history_FR, vel_index_FR);

    float out_FL = (target_FL == 0.0f) ? 0.0f : pidFL.compute(target_FL, vel_FL);
    float out_FR = (target_FR == 0.0f) ? 0.0f : pidFR.compute(target_FR, vel_FR);

    out_FL = constrain(out_FL, -255.0f, 255.0f);
    out_FR = constrain(out_FR, -255.0f, 255.0f);

    // FL: forward = LOW
    digitalWrite(DIR_FL, out_FL >= 0 ? LOW : HIGH);
    ledcWrite(PWM_CH_FL, (int)abs(out_FL));

    // FR: inverted vs FL — forward = HIGH
    digitalWrite(DIR_FR, out_FR >= 0 ? HIGH : LOW);
    ledcWrite(PWM_CH_FR, (int)abs(out_FR));

    // --- 3. SEND CUMULATIVE TICKS TO HOST (every 50ms) ---
    if (millis() - last_print_time >= 50) {
      last_print_time = millis();
      Serial.printf("ENC:M1:%ld M2:%ld\n", ticks_FL, ticks_FR);
    }
  }
}
