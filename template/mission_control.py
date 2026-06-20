from pybricks.hubs import MoveHub
from pybricks.pupdevices import Motor, ColorDistanceSensor
from pybricks.parameters import Port, Color, Direction
from pybricks.robotics import DriveBase

# --- HOST_PARAMS_START ---
# AI/Host will replace the variables below before upload
speed_green = 150
speed_yellow = 100
speed_blue = 100
speed_red = 0
turn_rate_green = 0
turn_rate_yellow = 90
turn_rate_blue = -90
turn_rate_red = 0
motor_d_speed = 25
# --- HOST_PARAMS_END ---


class ColorStrategy:
    def execute(self, robot):
        raise NotImplementedError()


class DriveStrategy(ColorStrategy):
    def __init__(self, speed, turn_rate):
        self.speed = speed
        self.turn_rate = turn_rate

    def execute(self, robot):
        robot.drive(self.speed, self.turn_rate)


def main():
    hub = MoveHub()
    left_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
    right_motor = Motor(Port.B, Direction.CLOCKWISE)
    robot = DriveBase(left_motor, right_motor, wheel_diameter=30, axle_track=65)

    motor = Motor(Port.D)
    sensor = ColorDistanceSensor(Port.C)

    motor.run(speed=motor_d_speed)

    strategies = {
        Color.GREEN: DriveStrategy(speed=speed_green, turn_rate=turn_rate_green),
        Color.YELLOW: DriveStrategy(speed=speed_yellow, turn_rate=turn_rate_yellow),
        Color.BLUE: DriveStrategy(speed=speed_blue, turn_rate=turn_rate_blue),
        Color.RED: DriveStrategy(speed=speed_red, turn_rate=turn_rate_red),
    }

    print_result()

    last_color = None
    while True:
        detected_color = sensor.color()

        if detected_color is None:
            hub.light.off()
            last_color = None
            continue

        hub.light.on(detected_color)

        strategy = strategies.get(detected_color)
        if strategy:
            strategy.execute(robot)
            if detected_color != last_color:
                print_result()
                last_color = detected_color


def print_result():
    print(
        "RESULT speed_green={sg} speed_yellow={sy} speed_blue={sb} speed_red={sr}"
        " turn_rate_green={tg} turn_rate_yellow={ty} turn_rate_blue={tb}"
        " turn_rate_red={tr} motor_d_speed={md}".format(
            sg=speed_green,
            sy=speed_yellow,
            sb=speed_blue,
            sr=speed_red,
            tg=turn_rate_green,
            ty=turn_rate_yellow,
            tb=turn_rate_blue,
            tr=turn_rate_red,
            md=motor_d_speed,
        )
    )


if __name__ == "__main__":
    main()
