#include <Arduino.h>
#include <AFMotor.h>
#include <Servo.h>

// Create motor objects for each motor
AF_DCMotor motor1(1, MOTOR12_64KHZ);
AF_DCMotor motor2(2, MOTOR12_64KHZ);
AF_DCMotor motor3(3, MOTOR34_1KHZ);
AF_DCMotor motor4(4, MOTOR34_1KHZ);
Servo servo1, servo2;

int speed = 250;

void setup()
{
  Serial.begin(2000000);
  motor1.setSpeed(speed);
  motor2.setSpeed(speed);
  motor3.setSpeed(speed);
  motor4.setSpeed(speed);
  servo1.attach(9);       // El servo 1 se controla con el pin 9
  servo2.attach(10);      // El servo 2 se controla con el pin 10
}

void moveForward()
{
  Serial.println("Moving forward");
  motor1.run(FORWARD);
  motor2.run(FORWARD);
  motor3.run(FORWARD);
  motor4.run(FORWARD);
}

void moveBackward()
{
  Serial.println("Moving backward");
  motor1.run(BACKWARD);
  motor2.run(BACKWARD);
  motor3.run(BACKWARD);
  motor4.run(BACKWARD);
}

void Rotate_Right()
{
  Serial.println("Rotating clockwise");
  motor1.run(FORWARD);
  motor2.run(BACKWARD);
  motor3.run(BACKWARD);
  motor4.run(FORWARD);
}

void Rotate_Left()
{
  Serial.println("Rotating counterclockwise");
  motor1.run(BACKWARD);
  motor2.run(FORWARD);
  motor3.run(FORWARD);
  motor4.run(BACKWARD);
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

void controlServo(int servoNumber, int angle)
{
  if (servoNumber == 1)
  {
    Serial.print("Moving servo1 to ");
    Serial.print(angle);
    Serial.println(" degrees");
    servo1.write(angle);
  }
  else if (servoNumber == 2)
  {
    Serial.print("Moving servo2 to ");
    Serial.print(angle);
    Serial.println(" degrees");
    servo2.write(angle);
  }
  else
  {
    Serial.println("Invalid servo number");
  }
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
    else if (command.length() > 5 && command.substring(0, 5) == "servo")
    {
      int dashIndex = command.indexOf('-');
      if (dashIndex > 5)
      {
        int servoNumber = command.substring(5, dashIndex).toInt();
        int angle = command.substring(dashIndex + 1).toInt();
        controlServo(servoNumber, angle);
      }
    }
    else
    {
      // Do nothing for unrecognized commands
    }
  }
}
