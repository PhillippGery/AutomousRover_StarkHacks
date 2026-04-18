#include <Arduino.h>
#include "PIDController.h"

// =============================================================================
// PIN DEFINITIONS — ESP32 Feather V2, REAR board
// =============================================================================
// Motor 1 BL
#define M1_DIR_PIN  12
#define M1_PWM_PIN  13
#define M1_ENC_A    34
#define M1_ENC_B    39

// Motor 2 BR — uncomment when wired
// #define M2_DIR_PIN  27
// #define M2_PWM_PIN  33
// #define M2_ENC_A    35
// #define M2_ENC_B    32

// =============================================================================
// PWM CHANNELS
// =============================================================================
const int PWM_CH_M1 = 0;
const int PWM_CH_M2 = 1;

// =============================================================================
// ENCODER TICKS
// =============================================================================
volatile long ticks_M1 = 0; long prev_ticks_M1 = 0;
volatile long ticks_M2 = 0; long prev_ticks_M2 = 0;

// =============================================================================
// VELOCITY FILTERS
// =============================================================================
float vel_history_M1[4] = {0,0,0,0}; int vel_index_M1 = 0;
float vel_history_M2[4] = {0,0,0,0}; int vel_index_M2 = 0;

// =============================================================================
// PID CONTROLLERS — 5ms loop
// =============================================================================
PIDController pidM1(0.05f, 0.2f, 0.0f, 0.005f, 15000.0f);
PIDController pidM2(0.05f, 0.2f, 0.0f, 0.005f, 15000.0f);

// =============================================================================
// TARGET SPEEDS (ticks/sec) — set via serial
// =============================================================================
float target_M1 = 0.0f;
float target_M2 = 0.0f;

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
void IRAM_ATTR readEncoderM1() { if (digitalRead(M1_ENC_B)) ticks_M1++; else ticks_M1--; }
#ifdef M2_ENC_A
void IRAM_ATTR readEncoderM2() { if (digitalRead(M2_ENC_B)) ticks_M2++; else ticks_M2--; }
#endif

// =============================================================================
// TIMERS
// =============================================================================
unsigned long last_print_time = 0;

// =============================================================================
// VELOCITY HELPER
// =============================================================================
float computeVelocity(long cur, long &prev, float* history, int &index) {
  float raw = (cur - prev) / 0.005f;  // 5ms timer
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

  // M1 (BL)
  pinMode(M1_ENC_A, INPUT_PULLUP);
  pinMode(M1_ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(M1_ENC_A), readEncoderM1, RISING);
  pinMode(M1_DIR_PIN, OUTPUT);
  ledcSetup(PWM_CH_M1, 5000, 8); ledcAttachPin(M1_PWM_PIN, PWM_CH_M1);
  ledcWrite(PWM_CH_M1, 0);

#ifdef M2_ENC_A
  // M2 (BR)
  pinMode(M2_ENC_A, INPUT_PULLUP);
  pinMode(M2_ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(M2_ENC_A), readEncoderM2, RISING);
  pinMode(M2_DIR_PIN, OUTPUT);
  ledcSetup(PWM_CH_M2, 5000, 8); ledcAttachPin(M2_PWM_PIN, PWM_CH_M2);
  ledcWrite(PWM_CH_M2, 0);
#endif

  // 5ms hardware timer
  timer = timerBegin(0, 80, true);
  timerAttachInterrupt(timer, &onTimer, true);
  timerAlarmWrite(timer, 5000, true);
  timerAlarmEnable(timer);

  last_msg_time = millis();
  Serial.println("REAR ready");
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

  // --- 1b. SAFETY STOP — no message for 500ms ---
  if (millis() - last_msg_time > 500) {
    target_M1 = 0.0f;
    target_M2 = 0.0f;
  }

  // --- 2. PID LOOP (every 5ms) ---
  if (run_pid_flag) {
    run_pid_flag = false;

    noInterrupts();
    long cur_M1 = ticks_M1;
    long cur_M2 = ticks_M2;
    interrupts();

    float vel_M1 = computeVelocity(cur_M1, prev_ticks_M1, vel_history_M1, vel_index_M1);
    float vel_M2 = computeVelocity(cur_M2, prev_ticks_M2, vel_history_M2, vel_index_M2);

    float out_M1 = (target_M1 == 0.0f) ? 0.0f : pidM1.compute(target_M1, vel_M1);
    float out_M2 = (target_M2 == 0.0f) ? 0.0f : pidM2.compute(target_M2, vel_M2);

    out_M1 = constrain(out_M1, -255.0f, 255.0f);
    out_M2 = constrain(out_M2, -255.0f, 255.0f);

    // M1 (BL): forward = LOW
    digitalWrite(M1_DIR_PIN, out_M1 >= 0 ? LOW : HIGH);
    ledcWrite(PWM_CH_M1, (int)abs(out_M1));

#ifdef M2_ENC_A
    // M2 (BR): forward = HIGH
    digitalWrite(M2_DIR_PIN, out_M2 >= 0 ? HIGH : LOW);
    ledcWrite(PWM_CH_M2, (int)abs(out_M2));
#endif

    // --- 3. SEND CUMULATIVE TICKS TO HOST (every 50ms) ---
    if (millis() - last_print_time >= 50) {
      last_print_time = millis();
      Serial.printf("ENC:M1:%ld M2:%ld\n", ticks_M1, ticks_M2);
    }
  }
}
