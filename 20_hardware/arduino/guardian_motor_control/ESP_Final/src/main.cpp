#include <Arduino.h>
#include "PIDController.h"
// put function declarations here:
// Front Left
const int ENCODER_FL_A = 1; //fRONT LEFT MOTOR YELLOW
const int ENCODER_FL_B = 6; // FRONT LEFT MOTOR WHITE
const int PWM_FL       = 12; // FRONT LEFT PWM
const int DIR_FL       = 16; // FRONT LEFT DIR
const int PWM_CH_FL    = 0;

// Front Right
const int ENCODER_FR_A = 2; // FRONT RIGHT YELLOW
const int ENCODER_FR_B = 7; //FRONT RIGHT WHITE
const int PWM_FR       = 13; // FRONT RIGHT PWM'
const int DIR_FR       = 17; // FRONT RIGHT DIR
const int PWM_CH_FR    = 1;

// Rear Left
const int ENCODER_RL_A = 4; // REAR LEFT YELLOW
const int ENCODER_RL_B = 10; // REAR LEFT WHITE
const int PWM_RL       = 14; // REAR LEFT PWM
const int DIR_RL       = 18; // REAR LEFT DIR
const int PWM_CH_RL    = 2;

// Rear Right
const int ENCODER_RR_A = 5; //REAR RIGHT YELLOW
const int ENCODER_RR_B = 11;// REAR RIGHT WHITE
const int PWM_RR       = 35; // REAR RIGHT PWM
const int DIR_RR       = 21; // REAR RIGHT DIR
const int PWM_CH_RR    = 3;


volatile long ticks_FL = 0; long prev_ticks_FL = 0;
volatile long ticks_FR = 0; long prev_ticks_FR = 0;
volatile long ticks_RL = 0; long prev_ticks_RL = 0;
volatile long ticks_RR = 0; long prev_ticks_RR = 0;


float vel_history_FL[4] = {0, 0, 0, 0}; int vel_index_FL = 0;
float vel_history_FR[4] = {0, 0, 0, 0}; int vel_index_FR = 0; 
float vel_history_RL[4] = {0, 0, 0, 0}; int vel_index_RL = 0;
float vel_history_RR[4] = {0, 0, 0, 0}; int vel_index_RR = 0;

PIDController pidFL(0.3f, 0.005f, 0.0001f, 0.01f, 15000.0f);
PIDController pidFR(0.3f, 0.005f, 0.0001f, 0.01f, 15000.0f);
PIDController pidRL(0.3f, 0.005f, 0.0001f, 0.01f, 15000.0f);
PIDController pidRR(0.3f, 0.005f, 0.0001f, 0.01f, 15000.0f);

float target_FL = 0.0f;
float target_FR = 0.0f;
float target_RL = 0.0f;
float target_RR = 0.0f;

String input_string = "";
unsigned long last_msg_time = 0;

hw_timer_t * timer = NULL;
volatile bool run_pid_flag = false;
void IRAM_ATTR onTimer() { run_pid_flag = true; }

void IRAM_ATTR readEncoderFL() { if (digitalRead(ENCODER_FL_B)) ticks_FL++; else ticks_FL--; }
void IRAM_ATTR readEncoderFR() { if (digitalRead(ENCODER_FR_B)) ticks_FR++; else ticks_FR--; }
void IRAM_ATTR readEncoderRL() { if (digitalRead(ENCODER_RL_B)) ticks_RL--; else ticks_RL++; }
void IRAM_ATTR readEncoderRR() { if (digitalRead(ENCODER_RR_B)) ticks_RR++; else ticks_RR--; }

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




void setup() {
  // put your setup code here, to run once:
  Serial0.begin(115200);
  
  // Direct RR motor test — bypasses PID completely
  
  // Encoder pins
  pinMode(ENCODER_FL_A, INPUT_PULLUP); pinMode(ENCODER_FL_B, INPUT_PULLUP);
  pinMode(ENCODER_FR_A, INPUT_PULLUP); pinMode(ENCODER_FR_B, INPUT_PULLUP);
  pinMode(ENCODER_RL_A, INPUT_PULLUP); pinMode(ENCODER_RL_B, INPUT_PULLUP);
  pinMode(ENCODER_RR_A, INPUT_PULLUP); pinMode(ENCODER_RR_B, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(ENCODER_FL_A), readEncoderFL, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_FR_A), readEncoderFR, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_RL_A), readEncoderRL, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_RR_A), readEncoderRR, RISING);

  // Motor pins
  pinMode(DIR_FL, OUTPUT); pinMode(DIR_FR, OUTPUT);
  pinMode(DIR_RL, OUTPUT); pinMode(DIR_RR, OUTPUT);

  ledcSetup(PWM_CH_FL, 5000, 8); ledcAttachPin(PWM_FL, PWM_CH_FL); ledcWrite(PWM_CH_FL, 0);
  ledcSetup(PWM_CH_FR, 5000, 8); ledcAttachPin(PWM_FR, PWM_CH_FR); ledcWrite(PWM_CH_FR, 0);
  ledcSetup(PWM_CH_RL, 5000, 8); ledcAttachPin(PWM_RL, PWM_CH_RL); ledcWrite(PWM_CH_RL, 0);
  ledcSetup(PWM_CH_RR, 5000, 8); ledcAttachPin(PWM_RR, PWM_CH_RR); ledcWrite(PWM_CH_RR, 0);
  
  // 20ms hardware timer
  timer = timerBegin(0, 80, true);
  timerAttachInterrupt(timer, &onTimer, true);
  timerAlarmWrite(timer, 10000, true);
  timerAlarmEnable(timer);

  last_msg_time = millis();

  target_FL = 0.0f;
  target_FR = 0.0f;
  target_RL = 0.0f;
  target_RR = 0.0f;

  Serial0.println("ROBOT ready");
}

void loop() {
  // put your main code here, to run repeatedly:
  while (Serial0.available() > 0) {
    char c = Serial0.read();
    if (c == '\n') {
      float v1, v2, v3, v4;
      if (sscanf(input_string.c_str(), "M1:%f M2:%f M3:%f M4:%f", &v1, &v2, &v3, &v4) == 4) {
        target_FL = (v1 / 60.0f) * 175.0f;
        target_FR = (v2 / 60.0f) * 175.0f;
        target_RL = (v3 / 60.0f) * 175.0f;
        target_RR = (v4 / 60.0f) * 175.0f;
        last_msg_time = millis();
      }
      input_string = "";
    } else {
      input_string += c;
    }
  }

if (run_pid_flag) {
    run_pid_flag = false;

    noInterrupts();
    long cur_FL = ticks_FL; long cur_FR = ticks_FR;
    long cur_RL = ticks_RL; long cur_RR = ticks_RR;
    interrupts();

    float vel_FL = computeVelocity(cur_FL, prev_ticks_FL, vel_history_FL, vel_index_FL);
    float vel_FR = computeVelocity(cur_FR, prev_ticks_FR, vel_history_FR, vel_index_FR);
    float vel_RL = computeVelocity(cur_RL, prev_ticks_RL, vel_history_RL, vel_index_RL);
    float vel_RR = computeVelocity(cur_RR, prev_ticks_RR, vel_history_RR, vel_index_RR);

    float out_FL = (target_FL == 0.0f) ? 0.0f : pidFL.compute(target_FL, vel_FL);
    float out_FR = (target_FR == 0.0f) ? 0.0f : pidFR.compute(target_FR, vel_FR);
    float out_RL = (target_RL == 0.0f) ? 0.0f : pidRL.compute(target_RL, vel_RL);
    float out_RR = (target_RR == 0.0f) ? 0.0f : pidRR.compute(target_RR, vel_RR);

    // Feedforward
    if (target_FL > 0.0f) out_FL += 25.0f; else if (target_FL < 0.0f) out_FL -= 50.0f;
    if (target_FR > 0.0f) out_FR += 25.0f; else if (target_FR < 0.0f) out_FR -= 50.0f;
    if (target_RL > 0.0f) out_RL += 25.0f; else if (target_RL < 0.0f) out_RL -= 50.0f;
    if (target_RR > 0.0f) out_RR += 25.0f; else if (target_RR < 0.0f) out_RR -= 50.0f;

    out_FL = constrain(out_FL, -255.0f, 255.0f);
    out_FR = constrain(out_FR, -255.0f, 255.0f);
    out_RL = constrain(out_RL, -255.0f, 255.0f);
    out_RR = constrain(out_RR, -255.0f, 255.0f);

    digitalWrite(DIR_FL, out_FL >= 0 ? LOW : HIGH); ledcWrite(PWM_CH_FL, (int)abs(out_FL));
    digitalWrite(DIR_FR, out_FR >= 0 ? LOW : HIGH); ledcWrite(PWM_CH_FR, (int)abs(out_FR));
    digitalWrite(DIR_RL, out_RL >= 0 ? LOW: HIGH); ledcWrite(PWM_CH_RL, (int)abs(out_RL));
    digitalWrite(DIR_RR, out_RR >= 0 ? HIGH : LOW); ledcWrite(PWM_CH_RR, (int)abs(out_RR));

    // --- SEND TICKS every 50ms ---
    if (millis() - last_print_time >= 50) {
      last_print_time = millis();
      Serial0.printf("ENC:M1:%.1f M2:%.1f M3:%.1f M4:%.1f\n", vel_FL, vel_FR, vel_RL, vel_RR);
    }
  }
}