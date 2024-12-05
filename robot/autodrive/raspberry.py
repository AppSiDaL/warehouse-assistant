from gpiozero import LED

front_led = LED(23)
right_led = LED(17)
left_led = LED(22)


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
