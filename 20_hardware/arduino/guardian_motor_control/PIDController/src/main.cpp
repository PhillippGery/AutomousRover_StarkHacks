#include <Arduino.h>
#include "PIDController.h"

// =============================================================================
// PIN DEFINITIONS — Arduino Mega 2560
// =============================================================================
// Front Left
const int ENCODER_A_FL = 20;  // hardware interrupt (avoid I2C if used)
const int ENCODER_B_FL = 31;
const int PWM_PIN_FL   = 2;   // PWM Timer3
const int DIR_PIN_FL   = 30;

// Front Right
const int ENCODER_A_FR = 21;  // hardware interrupt (avoid I2C if used)
const int ENCODER_B_FR = 33;
const int PWM_PIN_FR   = 3;   // PWM Timer3
const int DIR_PIN_FR   = 32;

// Back Left
const int ENCODER_A_BL = 19;  // hardware interrupt (also UART1 TX — don't use Serial1)
const int ENCODER_B_BL = 35;
const int PWM_PIN_BL   = 4;   // PWM Timer0 ~980Hz
const int DIR_PIN_BL   = 34;

// Back Right
const int ENCODER_A_BR = 18;  // hardware interrupt (also UART1 RX — don't use Serial1)
const int ENCODER_B_BR = 37;
const int PWM_PIN_BR   = 5;   // PWM Timer3
const int DIR_PIN_BR   = 36;

// =============================================================================
// ENCODER CPR
// Trial and error: start with 4.0 (motor shaft) or 175.0 (gearbox output)
// Tell Phillipp whichever value you settle on — he needs it for odometry
// =============================================================================
float CPR = 4.0f;

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
// PID CONTROLLERS — same gains that worked in the single motor test
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
// PID TIMING — replaces ESP32 hw_timer_t; Mega uses millis() polling at 5ms
// =============================================================================
volatile bool run_pid_flag = false;
unsigned long last_pid_time = 0;

// =============================================================================
// LAST PWM OUTPUTS — file-scope so the serial print section can read them
// =============================================================================
float out_FL = 0.0f, out_FR = 0.0f, out_BL = 0.0f, out_BR = 0.0f;

// =============================================================================
// SERIAL PRINT TIMER
// =============================================================================
unsigned long last_print_time = 0;

// =============================================================================
// ENCODER ISRs — IRAM_ATTR removed (AVR does not use it)
// =============================================================================
void readEncoderFL() { if (digitalRead(ENCODER_B_FL)) ticks_FL++; else ticks_FL--; }
void readEncoderFR() { if (digitalRead(ENCODER_B_FR)) ticks_FR++; else ticks_FR--; }
void readEncoderBL() { if (digitalRead(ENCODER_B_BL)) ticks_BL++; else ticks_BL--; }
void readEncoderBR() { if (digitalRead(ENCODER_B_BR)) ticks_BR++; else ticks_BR--; }

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
// MOTOR TEST — send "TEST\n" over serial to verify wiring before connecting ROS2
// Runs each motor forward at 50% for 1 second then stops
// =============================================================================
void runMotorTest() {
  Serial.println("TEST: starting motor test");
  int dir_pins[4]  = { DIR_PIN_FL, DIR_PIN_FR, DIR_PIN_BL, DIR_PIN_BR };
  int pwm_pins[4]  = { PWM_PIN_FL, PWM_PIN_FR, PWM_PIN_BL, PWM_PIN_BR };
  const char* names[4] = { "FL", "FR", "BL", "BR" };
  for (int i = 0; i < 4; i++) {
    Serial.print("TEST: motor "); Serial.println(names[i]);
    digitalWrite(dir_pins[i], LOW);
    analogWrite(pwm_pins[i], 127); // 50%
    delay(1000);
    analogWrite(pwm_pins[i], 0);
    delay(200);
  }
  Serial.println("TEST: done");
}

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
  pinMode(PWM_PIN_FL, OUTPUT);
  analogWrite(PWM_PIN_FL, 0);

  // FR
  pinMode(ENCODER_A_FR, INPUT_PULLUP);
  pinMode(ENCODER_B_FR, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_A_FR), readEncoderFR, RISING);
  pinMode(DIR_PIN_FR, OUTPUT);
  pinMode(PWM_PIN_FR, OUTPUT);
  analogWrite(PWM_PIN_FR, 0);

  // BL
  pinMode(ENCODER_A_BL, INPUT_PULLUP);
  pinMode(ENCODER_B_BL, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_A_BL), readEncoderBL, RISING);
  pinMode(DIR_PIN_BL, OUTPUT);
  pinMode(PWM_PIN_BL, OUTPUT);
  analogWrite(PWM_PIN_BL, 0);

  // BR
  pinMode(ENCODER_A_BR, INPUT_PULLUP);
  pinMode(ENCODER_B_BR, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_A_BR), readEncoderBR, RISING);
  pinMode(DIR_PIN_BR, OUTPUT);
  pinMode(PWM_PIN_BR, OUTPUT);
  analogWrite(PWM_PIN_BR, 0);
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
      if (input_string == "TEST") {
        runMotorTest();
      } else {
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
      }
      input_string = "";
    } else {
      input_string += c;
    }
  }

  // --- 2. FAST PID LOOP (every 5ms via millis — replaces ESP32 hardware timer) ---
  if (millis() - last_pid_time >= 5) {
    last_pid_time = millis();
    run_pid_flag = true;
  }

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
    out_FL = pidFL.compute(target_FL, vel_FL);
    out_FR = pidFR.compute(target_FR, vel_FR);
    out_BL = pidBL.compute(target_BL, vel_BL);
    out_BR = pidBR.compute(target_BR, vel_BR);

    // Clamp all outputs
    out_FL = constrain(out_FL, -255.0f, 255.0f);
    out_FR = constrain(out_FR, -255.0f, 255.0f);
    out_BL = constrain(out_BL, -255.0f, 255.0f);
    out_BR = constrain(out_BR, -255.0f, 255.0f);

    // Apply to motors
    // If any motor spins the wrong direction, swap LOW/HIGH on that motor's DIR line
    digitalWrite(DIR_PIN_FL, out_FL >= 0 ? LOW : HIGH);
    analogWrite(PWM_PIN_FL, (int)abs(out_FL));

    digitalWrite(DIR_PIN_FR, out_FR >= 0 ? HIGH : LOW); // FR inverted vs FL
    analogWrite(PWM_PIN_FR, (int)abs(out_FR));

    digitalWrite(DIR_PIN_BL, out_BL >= 0 ? LOW : HIGH);
    analogWrite(PWM_PIN_BL, (int)abs(out_BL));

    digitalWrite(DIR_PIN_BR, out_BR >= 0 ? HIGH : LOW); // BR inverted vs BL
    analogWrite(PWM_PIN_BR, (int)abs(out_BR));
  }

  // --- 3. SEND RAW TICKS TO NAV2 (every 50ms) ---
  // Phillipp converts ticks -> odometry using the same CPR value above
  // Serial.printf not available on AVR — replaced with Serial.print chains
  if (millis() - last_print_time >= 50) {
    last_print_time = millis();
    Serial.print("ENC:FL:"); Serial.print(ticks_FL);
    Serial.print(" FR:"); Serial.print(ticks_FR);
    Serial.print(" BL:"); Serial.print(ticks_BL);
    Serial.print(" BR:"); Serial.println(ticks_BR);

    Serial.print("PWM:FL:"); Serial.print((int)out_FL);
    Serial.print(" FR:"); Serial.print((int)out_FR);
    Serial.print(" BL:"); Serial.print((int)out_BL);
    Serial.print(" BR:"); Serial.println((int)out_BR);
  }
}
