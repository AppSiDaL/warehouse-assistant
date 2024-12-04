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
  Serial.begin(9600);
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
}

void executeSequence()
{
  // Secuencia de comandos predefinidos
  moveBackward();
  delay(3000); // Ajusta el tiempo según la distancia a recorrer
  STOP();

  Rotate_Left();
  delay(2000); // Ajusta el tiempo según el ángulo de giro
  STOP();

  moveForward();
  delay(5000); // Ajusta el tiempo según la distancia a recorrer
  STOP();

  Rotate_Left();
  delay(2000); // Ajusta el tiempo según el ángulo de giro
  STOP();

  moveForward();
  delay(5000); // Ajusta el tiempo según la distancia a recorrer
  STOP();

  Rotate_Left();
  delay(2000); // Ajusta el tiempo según el ángulo de giro
  STOP();

  moveForward();
  delay(7000); // Ajusta el tiempo según la distancia a recorrer
  STOP();
}

void loop()
{
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove any leading or trailing whitespace
    if (command == "start") {
      executeSequence();
    }
  }
}
