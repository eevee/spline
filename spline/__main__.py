"""Entry point for running spline as a web app."""
# NOTE: this code CANNOT EVER go in spline/app.py; running that directly will
# change its name to __main__ which will make pyramid confused and unhappy.

import waitress

import spline.app

from spline.lib.parsing import (
    make_parser
)

def main():
    parser = make_parser()
    args = parser.parse_args()

    app = spline.app.main({}, **vars(args))
    if args.bind:
        waitress.serve(app, **args.bind)
    else:
        return app


if __name__ == '__main__':
    application = main()
