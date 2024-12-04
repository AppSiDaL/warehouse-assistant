#include <Arduino.h>
#include <AFMotor.h>
#include <Servo.h>
#include <Bridge.h>
#include <HttpClient.h>

// Replace with your network credentials
const char* ssid = "VAMSI INTERNET 7121647128";
const char* password = "RC74KL58AS";

// API endpoint
const char* api_url = "http://raspberrypi.local:8000/current_command";

// Create motor objects for each motor
AF_DCMotor motor1(1, MOTOR12_64KHZ);
AF_DCMotor motor2(2, MOTOR12_64KHZ);
AF_DCMotor motor3(3, MOTOR34_1KHZ);
AF_DCMotor motor4(4, MOTOR34_1KHZ);
Servo servo1, servo2;

int speed = 250;

void setup()
{
  Serial.begin(115200);
  motor1.setSpeed(speed);
  motor2.setSpeed(speed);
  motor3.setSpeed(speed);
  motor4.setSpeed(speed);
  servo1.attach(9);       // El servo 1 se controla con el pin 9
  servo2.attach(10);      // El servo 2 se controla con el pin 10

  // Initialize Bridge
  Bridge.begin();

  Serial.println("Bridge initialized");
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
  // Initialize the client library
  HttpClient client;

  // Make a HTTP request:
  client.get(api_url);

  // if there are incoming bytes available
  // from the server, read them and process them:
  String payload = "";
  while (client.available()) {
    char c = client.read();
    payload += c;
  }

  if (payload.length() > 0) {
    Serial.println(payload);

    if (payload == "forward")
    {
      moveForward();
    }
    else if (payload == "backward")
    {
      moveBackward();
    }
    else if (payload == "left")
    {
      Rotate_Left();
    }
    else if (payload == "right")
    {
      Rotate_Right();
    }
    else if (payload == "stop")
    {
      STOP();
    }
    else if (payload.length() > 5 && payload.substring(0, 5) == "servo")
    {
      int dashIndex = payload.indexOf('-');
      if (dashIndex > 5)
      {
        int servoNumber = payload.substring(5, dashIndex).toInt();
        int angle = payload.substring(dashIndex + 1).toInt();
        controlServo(servoNumber, angle);
      }
    }
  } else {
    Serial.println("Error on HTTP request");
  }

  delay(500); // Wait for 500 milliseconds before the next request
}