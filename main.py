import argparse

from services import StaticFilesTraversalService


def main():
    parser = argparse.ArgumentParser(
        description="Collecting static files from a web server and exploring github repo.",
    )
    parser.add_argument("--web-url", required=True, type=str, help="URL of a website")
    parser.add_argument(
        "--retry_delay",
        required=False,
        default=3.0,
        type=float,
        help="Retry delay when got HTTP_429_TOO_MANY_REQUESTS.",
    )
    parser.add_argument(
        "--max_retries",
        required=False,
        default=3,
        type=int,
        help="Max retry number when got HTTP_429_TOO_MANY_REQUESTS.",
    )
    parser.add_argument(
        "--depth",
        required=False,
        default=1,
        type=int,
        help="Depth for website tree traversal.",
    )
    args = parser.parse_args()

    web_url = args.web_url
    retry_delay = args.retry_delay
    max_retries = args.max_retries
    depth = args.depth

    s = StaticFilesTraversalService(
        base_url=web_url,
        max_retries=max_retries,
        retry_delay=retry_delay,
    )
    for x in s.traverse(max_depth=depth):
        print(x)


if __name__ == '__main__':
    main()
