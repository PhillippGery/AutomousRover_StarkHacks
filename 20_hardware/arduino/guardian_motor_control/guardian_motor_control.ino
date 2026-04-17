// MIT License
// GUARDIAN — StarkHacks 2026
//
// Purpose : Low-level motor control for GUARDIAN omnidirectional rover
// Author  : Vedant
// Date    : April 2026
// Hardware: Arduino Mega 2560
//           2× L298N H-bridge motor drivers
//           4× JGB37-3530 12V DC encoder motors
//
// Serial Protocol (115200 baud):
//   Receive  : "FL:150 FR:150 BL:-150 BR:-150\n"   (RPM targets from ROS2)
//   Transmit : "ENC:FL:148 FR:151 BL:-149 BR:-152\n" (measured RPMs)
//
// PID gains — tune at hackathon: Kp=1.5, Ki=0.0, Kd=0.1 as starting point

// ─── Pin Definitions ──────────────────────────────────────────────────────────
// L298N #1 controls Front-Left (FL) and Back-Left (BL)
// TODO: verify pin assignments against physical wiring before upload

// Front-Left (FL) — L298N #1 channel A
const int FL_IN1 = 2;
const int FL_IN2 = 3;
const int FL_ENA = 4;   // PWM-capable pin

// Back-Left (BL) — L298N #1 channel B
const int BL_IN1 = 5;
const int BL_IN2 = 6;
const int BL_ENB = 7;   // PWM-capable pin

// Front-Right (FR) — L298N #2 channel A
const int FR_IN1 = 8;
const int FR_IN2 = 9;
const int FR_ENA = 10;  // PWM-capable pin

// Back-Right (BR) — L298N #2 channel B
const int BR_IN1 = 11;
const int BR_IN2 = 12;
const int BR_ENB = 13;  // PWM-capable pin

// Encoder pins (use interrupt-capable pins: 2, 3, 18, 19, 20, 21)
// TODO: reassign if conflicting with L298N or I2C pins above
const int FL_ENC_A = 18;
const int FL_ENC_B = 19;
const int FR_ENC_A = 20;
const int FR_ENC_B = 21;
const int BL_ENC_A = 2;   // shared with FL_IN1 — TODO: resolve conflict
const int BL_ENC_B = 3;   // shared with FL_IN2 — TODO: resolve conflict
const int BR_ENC_A = -1;  // TODO: assign available interrupt pin
const int BR_ENC_B = -1;  // TODO: assign available interrupt pin

// ─── Target RPMs (set by serial commands) ─────────────────────────────────────
volatile int target_fl = 0;
volatile int target_fr = 0;
volatile int target_bl = 0;
volatile int target_br = 0;

// ─── Encoder counts ───────────────────────────────────────────────────────────
volatile long enc_fl = 0;
volatile long enc_fr = 0;
volatile long enc_bl = 0;
volatile long enc_br = 0;

// ─── Setup ────────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);

  // Motor driver pins
  pinMode(FL_IN1, OUTPUT); pinMode(FL_IN2, OUTPUT); pinMode(FL_ENA, OUTPUT);
  pinMode(BL_IN1, OUTPUT); pinMode(BL_IN2, OUTPUT); pinMode(BL_ENB, OUTPUT);
  pinMode(FR_IN1, OUTPUT); pinMode(FR_IN2, OUTPUT); pinMode(FR_ENA, OUTPUT);
  pinMode(BR_IN1, OUTPUT); pinMode(BR_IN2, OUTPUT); pinMode(BR_ENB, OUTPUT);

  // Start motors stopped
  setPWM(0, 0); setPWM(1, 0); setPWM(2, 0); setPWM(3, 0);

  // TODO: attach encoder interrupts
  // attachInterrupt(digitalPinToInterrupt(FL_ENC_A), isr_fl, RISING);
  // attachInterrupt(digitalPinToInterrupt(FR_ENC_A), isr_fr, RISING);
  // attachInterrupt(digitalPinToInterrupt(BL_ENC_A), isr_bl, RISING);
  // attachInterrupt(digitalPinToInterrupt(BR_ENC_A), isr_br, RISING);

  Serial.println("GUARDIAN motor controller ready.");
}

// ─── Main Loop ────────────────────────────────────────────────────────────────
void loop() {
  // TODO: read serial input, parse RPM targets, run PID, write PWM, publish encoders

  // Step 1: Read and parse serial command
  if (Serial.available()) {
    parseSerial();
  }

  // Step 2: Run PID for each wheel and set PWM
  // TODO: implement PID controller per wheel
  // int pwm_fl = pid(target_fl, measured_fl);
  // setPWM(0, pwm_fl);
  // ... repeat for FR, BL, BR

  // Step 3: Publish encoder feedback
  // TODO: call readEncoders() and transmit at fixed rate
  // readEncoders();
}

// ─── Parse Serial Command ─────────────────────────────────────────────────────
// Expected format: "FL:150 FR:150 BL:-150 BR:-150\n"
void parseSerial() {
  // TODO: implement serial parsing
  // Hint: use Serial.readStringUntil('\n'), then sscanf or String.toInt()
  // Example (sketch only — not validated):
  // String line = Serial.readStringUntil('\n');
  // sscanf(line.c_str(), "FL:%d FR:%d BL:%d BR:%d",
  //        &target_fl, &target_fr, &target_bl, &target_br);
}

// ─── Set Motor PWM ────────────────────────────────────────────────────────────
// motor: 0=FL, 1=FR, 2=BL, 3=BR
// value: -255 to +255 (negative = reverse)
void setPWM(int motor, int value) {
  // TODO: implement motor direction + PWM output
  // Hint: value > 0 → IN1=HIGH, IN2=LOW, analogWrite(ENA, abs(value))
  //       value < 0 → IN1=LOW, IN2=HIGH, analogWrite(ENA, abs(value))
  //       value == 0 → IN1=LOW, IN2=LOW, analogWrite(ENA, 0)
}

// ─── Read Encoders ────────────────────────────────────────────────────────────
// Reads encoder counts and transmits measured RPMs over Serial
void readEncoders() {
  // TODO: convert encoder counts to RPM, transmit, reset counts
  // Hint: RPM = (counts / CPR) * (60 / dt_seconds) where CPR = counts per revolution
  // Transmit format: "ENC:FL:148 FR:151 BL:-149 BR:-152\n"
  Serial.print("ENC:FL:"); Serial.print(0);
  Serial.print(" FR:"); Serial.print(0);
  Serial.print(" BL:"); Serial.print(0);
  Serial.print(" BR:"); Serial.println(0);
}

// ─── Encoder ISRs (attach in setup) ──────────────────────────────────────────
// void isr_fl() { enc_fl++; }
// void isr_fr() { enc_fr++; }
// void isr_bl() { enc_bl++; }
// void isr_br() { enc_br++; }
