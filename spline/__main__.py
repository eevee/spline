"""CLI entry point."""
from spline.cli.main import make_arg_parser


def main():
    parser = make_arg_parser()
    args = parser.parse_args()

    return args.func(parser, args)


if __name__ == '__main__':
    # This is for WSGI runners, in the case of `spline run`
    application = main()
