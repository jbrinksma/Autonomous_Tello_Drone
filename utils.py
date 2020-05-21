def print_status(msg):
    BLU = '\x1b[1;34m'
    RST = '\x1b[0;0m'
    print(f"(DRONE {BLU}INFO{RST}): {msg}")


def print_warning(msg):
    YLW = '\x1b[1;33m'
    RST = '\x1b[0;0m'
    print(f"(DRONE {YLW}WARNING{RST}): {msg}")


def print_error(msg):
    RED = '\x1b[1;31m'
    RST = '\x1b[0;0m'
    print(f"(DRONE {RED}ERROR{RST}): {msg}")
