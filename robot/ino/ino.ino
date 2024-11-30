#include <Arduino.h>
#include <AFMotor.h>

// Create motor objects for each motor
AF_DCMotor motor1(1, MOTOR12_64KHZ);
AF_DCMotor motor2(2, MOTOR12_64KHZ);
AF_DCMotor motor3(3, MOTOR34_1KHZ);
AF_DCMotor motor4(4, MOTOR34_1KHZ);

int speed = 200;

void setup()
{
  Serial.begin(9600);
  motor1.setSpeed(speed);
  motor2.setSpeed(speed);
  motor3.setSpeed(speed);
  motor4.setSpeed(speed);
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
    // Read the incoming string
    String command = Serial.readStringUntil('\n');

    // Execute the corresponding function based on the command
    if (command == "forward")
    {
      moveForward(); // Full speed forward
    }
    else if (command == "backward")
    {
      moveBackward(); // Full speed backward
    }
    else if (command == "left")
    {
      Rotate_Left(); // Full speed left
    }
    else if (command == "right")
    {
      Rotate_Right(); // Full speed right
    }
    else if (command == "stop")
    {
      STOP(); // Stop the car
    }
    else
    {
      // Do nothing for unrecognized commands
    }
  }
}
