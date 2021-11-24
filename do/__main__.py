from argparse import ArgumentParser
from loguru import logger

from .API import API

def main():

    logger.info("starting software")
    logger.debug("creating ArgumentParser")

    parser = ArgumentParser("do-calculus", description="desc", epilog="epilog")
    parser.parse_args()
    ...

    logger.debug("parsing arguments")
    logger.critical("AHHH")
    
    ...



if __name__ == "__main__":
    main()
