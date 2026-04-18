#!/usr/bin/env python3
"""
Usage:
    python main.py tx    <txhash>
    python main.py block <blockhash>
"""

import asyncio
from payjoin_detector.cli.commands import cmd_block, cmd_tx
from payjoin_detector.cli.parser import build_parser, get_provider
from payjoin_detector.detector import Detector
from payjoin_detector.cli.debug import setup_debug_logger


async def async_main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    detector = Detector(provider=get_provider(args))

    setup_debug_logger(getattr(args, "debug_output", None))

    if args.command == "tx":
        await cmd_tx(args, detector)
    elif args.command == "block":
        await cmd_block(args, detector)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
