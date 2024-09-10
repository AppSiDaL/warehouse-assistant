#include <Arduino.h>

void setup() {
  // Initialize the digital pins as outputs
  pinMode(2, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);

  // Initialize serial communication at 9600 bits per second
  Serial.begin(9600);
}
void Move_Forward(int car_speed) {
  digitalWrite(2, HIGH);
  analogWrite(5, car_speed);
  digitalWrite(4, LOW);
  analogWrite(6, car_speed);
}

void Move_Backward(int car_speed) {
  digitalWrite(2, LOW);
  analogWrite(5, car_speed);
  digitalWrite(4, HIGH);
  analogWrite(6, car_speed);
}

void Rotate_Left(int car_speed) {
  digitalWrite(2, LOW);
  analogWrite(5, car_speed);
  digitalWrite(4, LOW);
  analogWrite(6, car_speed);
}

void Rotate_Right(int car_speed) {
  digitalWrite(2, HIGH);
  analogWrite(5, car_speed);
  digitalWrite(4, HIGH);
  analogWrite(6, car_speed);
}

void STOP() {
  digitalWrite(2, LOW);
  analogWrite(5, 0);
  digitalWrite(4, HIGH);
  analogWrite(6, 0);
}
void loop() {
  // Check if data is available to read
  if (Serial.available() > 0) {
    // Read the incoming byte
    char command = Serial.read();

    // Execute the corresponding function based on the command
    switch (command) {
      case 'f':
        Move_Forward(255);  // Full speed forward
        break;
      case 'b':
        Move_Backward(255);  // Full speed backward
        break;
      case 'l':
        Rotate_Left(255);  // Full speed left
        break;
      case 'r':
        Rotate_Right(255);  // Full speed right
        break;
      case 's':
        STOP();  // Stop the car
        break;
      default:
        // Do nothing for unrecognized commands
        break;
    }
  }
}

