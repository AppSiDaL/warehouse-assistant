#include <Arduino.h>

#include <AFMotor.h>

// Create motor objects for each motor
AF_DCMotor motor1(1, MOTOR12_64KHZ);
AF_DCMotor motor2(2, MOTOR12_64KHZ);
AF_DCMotor motor3(3, MOTOR34_1KHZ);
AF_DCMotor motor4(4, MOTOR34_1KHZ);

void setup()
{
  Serial.begin(9600);
  motor1.setSpeed(100);
  motor2.setSpeed(100);
  motor3.setSpeed(100);
  motor4.setSpeed(100);
}
void moveForward()
{
  Serial.println("Moving forward");

  motor1.run(FORWARD);
  motor2.run(FORWARD);
  motor3.run(FORWARD);
  motor4.run(FORWARD);
  delay(3000);
}

void moveBackward()
{
  Serial.println("Moving backward");
  motor1.run(BACKWARD);
  motor2.run(BACKWARD);
  motor3.run(BACKWARD);
  motor4.run(BACKWARD);
  delay(3000);
}

void moveLeft()
{
  Serial.println("Moving left");
  motor1.run(BACKWARD);
  motor2.run(FORWARD);
  motor3.run(FORWARD);
  motor4.run(BACKWARD);
  delay(3000);
}

void moveRight()
{
  Serial.println("Moving right");
  motor1.run(FORWARD);
  motor2.run(BACKWARD);
  motor3.run(BACKWARD);
  motor4.run(FORWARD);
  delay(3000);
}

void Rotate_Right()
{
  Serial.println("Rotating clockwise");
  motor1.run(FORWARD);
  motor2.run(BACKWARD);
  motor3.run(FORWARD);
  motor4.run(BACKWARD);
  delay(3000);
}

void Rotate_Left()
{
  Serial.println("Rotating counterclockwise");
  motor1.run(BACKWARD);
  motor2.run(FORWARD);
  motor3.run(BACKWARD);
  motor4.run(FORWARD);
  delay(3000);
}

void STOP()
{
  Serial.println("Stopping all motors");
  motor1.run(RELEASE);
  motor2.run(RELEASE);
  motor3.run(RELEASE);
  motor4.run(RELEASE);
  delay(3000);
}

void loop()
{
  // Check if data is available to read
  if (Serial.available() > 0)
  {
    // Read the incoming byte
    char command = Serial.read();

    // Execute the corresponding function based on the command
    switch (command)
    {
    case 'forward':
      Move_Forward(); // Full speed forward
      break;
    case 'backward':
      Move_Backward(); // Full speed backward
      break;
    case 'left':
      Rotate_Left(); // Full speed left
      break;
    case 'right':
      Rotate_Right(); // Full speed right
      break;
    case 'stop':
      STOP(); // Stop the car
      break;
    default:
      // Do nothing for unrecognized commands
      break;
    }
  }
}
