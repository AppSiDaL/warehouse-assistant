from gpiozero import LED

front_led = LED(18)
right_led = LED(14)
left_led = LED(15)


def front_on():
    front_led.on()


def front_off():
    front_led.off()


def right_on():
    right_led.on()


def right_off():
    right_led.off()


def left_on():
    left_led.on()


def left_off():
    left_led.off()
