from argparse import ArgumentParser
from configparser import ConfigParser
from loguru import logger

from .API import API

def main():

    logger.info("starting software")
    logger.debug("creating ArgumentParser")

    config = ConfigParser()
    config.read("test.ini")
    print(config.sections())

    parser = ArgumentParser("do-calculus", description="desc", epilog="epilog")
    args = parser.parse_args()
    ...

    # TODO Model Verification/Specification(YML/JSON)

    logger.debug("parsing arguments")
    
    api = API()

    # TODO
    # for model in args.validate:
        # api.validate(...)
    
    ...

    logger.info("shutting down")


if __name__ == "__main__":
    main()
