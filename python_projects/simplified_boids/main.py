
from Field import Field


def main() -> None:
    # make Field object with flocks of sizes 15, 10, and 12
    field = Field([15, 10, 12])
    # run the Field's display in a loop
    while True:
        field.view()


if __name__ == '__main__':
    main()
        




