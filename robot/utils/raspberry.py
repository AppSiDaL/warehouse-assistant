from gpiozero import LED

front_led = LED(17)

def front_on():
    front_led.on()

def front_off():
    front_led.off()