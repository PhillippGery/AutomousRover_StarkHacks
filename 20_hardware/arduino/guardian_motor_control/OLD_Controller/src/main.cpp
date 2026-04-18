#include <Arduino.h>
#include "PIDController.h"

// =============================================================================
// PIN DEFINITIONS
// =============================================================================
// Front Left — confirmed working from single motor test
const int ENCODER_A_FL = 39; // Needs physical 10kΩ pull-up to 3.3V
const int ENCODER_B_FL = 25; // Needs physical 10kΩ pull-up to 3.3V
const int PWM_PIN_FL   = 33;
const int DIR_PIN_FL   = 27;
const int PWM_CH_FL    = 0;

// Front Right — confirmed working from 2 motor test
const int ENCODER_A_FR = 26;
const int ENCODER_B_FR = 35; // Needs physical 10kΩ pull-up to 3.3V
const int PWM_PIN_FR   = 15;
const int DIR_PIN_FR   = 32;
const int PWM_CH_FR    = 1;

// Back Left — VERIFY THESE PINS before flashing
// Original pins 20 (SDA) and 21 (SCL) were I2C — remapped below
const int ENCODER_A_BL = 19; // TODO: verify with your wiring
const int ENCODER_B_BL = 18; // TODO: verify with your wiring
const int PWM_PIN_BL   = 14; // TODO: verify with your wiring
const int DIR_PIN_BL   = 12; // TODO: verify with your wiring
const int PWM_CH_BL    = 2;

// Back Right — from original design
const int ENCODER_A_BR = 4;
const int ENCODER_B_BR = 13;
const int PWM_PIN_BR   = 19;
const int DIR_PIN_BR   = 21;
const int PWM_CH_BR    = 3;

// =============================================================================
// ENCODER CPR
// Trial and error: start with 4.0 (motor shaft) or 175.0 (gearbox output)
// Tell Phillipp whichever value you settle on — he needs it for odometry
// =============================================================================
float CPR = 4.0f; // <-- Change this during your trial and error

// =============================================================================
// ENCODER TICKS
// =============================================================================
volatile long ticks_FL = 0; long prev_ticks_FL = 0;
volatile long ticks_FR = 0; long prev_ticks_FR = 0;
volatile long ticks_BL = 0; long prev_ticks_BL = 0;
volatile long ticks_BR = 0; long prev_ticks_BR = 0;

// =============================================================================
// VELOCITY FILTERS
// =============================================================================
float vel_history_FL[4] = {0,0,0,0}; int vel_index_FL = 0;
float vel_history_FR[4] = {0,0,0,0}; int vel_index_FR = 0;
float vel_history_BL[4] = {0,0,0,0}; int vel_index_BL = 0;
float vel_history_BR[4] = {0,0,0,0}; int vel_index_BR = 0;

// =============================================================================
// PID CONTROLLERS — same gains that worked in your single motor test
// Re-tune per motor if they behave differently under load
// =============================================================================
PIDController pidFL(0.05f, 0.2f, 0.0f, 0.005f, 15000.0f);
PIDController pidFR(0.05f, 0.2f, 0.0f, 0.005f, 15000.0f);
PIDController pidBL(0.05f, 0.2f, 0.0f, 0.005f, 15000.0f);
PIDController pidBR(0.05f, 0.2f, 0.0f, 0.005f, 15000.0f);

// =============================================================================
// TARGET SPEEDS — set by NAV2 over serial (RPM), stored as ticks/s internally
// =============================================================================
float target_FL = 0.0f;
float target_FR = 0.0f;
float target_BL = 0.0f;
float target_BR = 0.0f;

// =============================================================================
// SERIAL PARSING
// =============================================================================
String input_string = "";

// =============================================================================
// HARDWARE TIMER
// =============================================================================
hw_timer_t * timer = NULL;
volatile bool run_pid_flag = false;
void IRAM_ATTR onTimer() { run_pid_flag = true; }

// =============================================================================
// ENCODER ISRs
// =============================================================================
void IRAM_ATTR readEncoderFL() { if (digitalRead(ENCODER_B_FL)) ticks_FL++; else ticks_FL--; }
void IRAM_ATTR readEncoderFR() { if (digitalRead(ENCODER_B_FR)) ticks_FR++; else ticks_FR--; }
void IRAM_ATTR readEncoderBL() { if (digitalRead(ENCODER_B_BL)) ticks_BL++; else ticks_BL--; }
void IRAM_ATTR readEncoderBR() { if (digitalRead(ENCODER_B_BR)) ticks_BR++; else ticks_BR--; }

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
// SERIAL PRINT TIMER
// =============================================================================
unsigned long last_print_time = 0;

// =============================================================================
// SETUP
// =============================================================================
void setup() {
  Serial.begin(115200);

  // FL
  pinMode(ENCODER_A_FL, INPUT_PULLUP);
  pinMode(ENCODER_B_FL, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_A_FL), readEncoderFL, RISING);
  pinMode(DIR_PIN_FL, OUTPUT);
  ledcSetup(PWM_CH_FL, 5000, 8); ledcAttachPin(PWM_PIN_FL, PWM_CH_FL);
  ledcWrite(PWM_CH_FL, 0);

  // FR
  pinMode(ENCODER_A_FR, INPUT_PULLUP);
  pinMode(ENCODER_B_FR, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_A_FR), readEncoderFR, RISING);
  pinMode(DIR_PIN_FR, OUTPUT);
  ledcSetup(PWM_CH_FR, 5000, 8); ledcAttachPin(PWM_PIN_FR, PWM_CH_FR);
  ledcWrite(PWM_CH_FR, 0);

  // BL
  pinMode(ENCODER_A_BL, INPUT_PULLUP);
  pinMode(ENCODER_B_BL, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_A_BL), readEncoderBL, RISING);
  pinMode(DIR_PIN_BL, OUTPUT);
  ledcSetup(PWM_CH_BL, 5000, 8); ledcAttachPin(PWM_PIN_BL, PWM_CH_BL);
  ledcWrite(PWM_CH_BL, 0);

  // BR
  pinMode(ENCODER_A_BR, INPUT_PULLUP);
  pinMode(ENCODER_B_BR, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_A_BR), readEncoderBR, RISING);
  pinMode(DIR_PIN_BR, OUTPUT);
  ledcSetup(PWM_CH_BR, 5000, 8); ledcAttachPin(PWM_PIN_BR, PWM_CH_BR);
  ledcWrite(PWM_CH_BR, 0);

  // 5ms hardware timer
  timer = timerBegin(0, 80, true);
  timerAttachInterrupt(timer, &onTimer, true);
  timerAlarmWrite(timer, 5000, true);
  timerAlarmEnable(timer);
}

// =============================================================================
// LOOP
// =============================================================================
void loop() {

  // --- 1. RECEIVE FROM NAV2 (non-blocking) ---
  // Expected format: "FL:500 FR:500 BL:500 BR:500" where values are RPM
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      int fl_rpm, fr_rpm, bl_rpm, br_rpm;
      int parsed = sscanf(input_string.c_str(), "FL:%d FR:%d BL:%d BR:%d",
                          &fl_rpm, &fr_rpm, &bl_rpm, &br_rpm);
      if (parsed == 4) {
        // Convert RPM -> ticks/s
        //target_FL = (float)fl_rpm * CPR / 60.0f;
        //target_FR = (float)fr_rpm * CPR / 60.0f;
        //target_BL = (float)bl_rpm * CPR / 60.0f;
        //target_BR = (float)br_rpm * CPR / 60.0f;
        target_BL = 100.0f;
        target_BR = 100.0f;
        target_FL = 100.0f;
        target_FR = 100.0f;
      }
      input_string = "";
    } else {
      input_string += c;
    }
  }

  // --- 2. FAST PID LOOP (every 5ms) ---
  if (run_pid_flag) {
    run_pid_flag = false;

    // Safely read all ticks
    noInterrupts();
    long cur_FL = ticks_FL; long cur_FR = ticks_FR;
    long cur_BL = ticks_BL; long cur_BR = ticks_BR;
    interrupts();

    // Compute filtered velocities
    float vel_FL = computeVelocity(cur_FL, prev_ticks_FL, vel_history_FL, vel_index_FL);
    float vel_FR = computeVelocity(cur_FR, prev_ticks_FR, vel_history_FR, vel_index_FR);
    float vel_BL = computeVelocity(cur_BL, prev_ticks_BL, vel_history_BL, vel_index_BL);
    float vel_BR = computeVelocity(cur_BR, prev_ticks_BR, vel_history_BR, vel_index_BR);

    // Run PIDs
    float out_FL = pidFL.compute(target_FL, vel_FL);
    float out_FR = pidFR.compute(target_FR, vel_FR);
    float out_BL = pidBL.compute(target_BL, vel_BL);
    float out_BR = pidBR.compute(target_BR, vel_BR);

    // Clamp all outputs
    out_FL = constrain(out_FL, -255.0f, 255.0f);
    out_FR = constrain(out_FR, -255.0f, 255.0f);
    out_BL = constrain(out_BL, -255.0f, 255.0f);
    out_BR = constrain(out_BR, -255.0f, 255.0f);

    // Apply to motors
    // If any motor spins the wrong direction, swap LOW/HIGH on that motor's DIR line
    digitalWrite(DIR_PIN_FL, out_FL >= 0 ? LOW : HIGH);
    ledcWrite(PWM_CH_FL, (int)abs(out_FL));

    digitalWrite(DIR_PIN_FR, out_FR >= 0 ? HIGH : LOW); // FR inverted vs FL
    ledcWrite(PWM_CH_FR, (int)abs(out_FR));

    digitalWrite(DIR_PIN_BL, out_BL >= 0 ? LOW : HIGH);
    ledcWrite(PWM_CH_BL, (int)abs(out_BL));

    digitalWrite(DIR_PIN_BR, out_BR >= 0 ? HIGH : LOW); // BR inverted vs BL
    ledcWrite(PWM_CH_BR, (int)abs(out_BR));
  }

  // --- 3. SEND RAW TICKS TO NAV2 (every 50ms) ---
  // Phillipp converts ticks -> odometry using the same CPR value above
  if (millis() - last_print_time >= 50) {
    last_print_time = millis();
    Serial.printf("ENC:FL:%ld FR:%ld BL:%ld BR:%ld\n",
                  ticks_FL, ticks_FR, ticks_BL, ticks_BR);
  
  Serial.printf("PWM:FL:%d FR:%d BL:%d BR:%d\n",
                  (int)out_FL, (int)out_FR, (int)out_BL, (int)out_BR);
  }
}