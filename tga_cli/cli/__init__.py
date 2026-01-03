# cli/
#       __init__.py
#       args.py                   # argparse only
#       controller.py             # calls service, handles exit codes/logging

from tga_cli.app_factory import create_service

#__all__ = ["create_service"]
# __all__ = []