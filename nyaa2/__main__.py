
import sys

if __package__ is None and not hasattr(sys, "frozen"):
    # direct call of __main__.py
    import os.path
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.realpath(path))


if __name__ == "__main__":
    import nyaa2

    nyaa2.create_important_paths()

    # loop = asyncio.get_event_loop()

    # loop.run_until_complete(nyaa2.main())
    # sys.exit()

    sys.exit(nyaa2.main())
