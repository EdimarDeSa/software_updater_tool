from argparse import ArgumentParser

from software_updater_tool.controller import Controller
from software_updater_tool.model import Model
from software_updater_tool.view import View


def main(software_name: str):
    view = View()
    model = Model()
    controller = Controller(view, model, software_name)

    controller.start()

    controller.start_update_process()

    controller.mainloop()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '--name',
        '-n',
        type=str,
        required=True,
        help='Name of the software to update',
    )

    main(parser.parse_args().name)
