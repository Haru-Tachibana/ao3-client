import argparse
from .reader import search_ao3, read_fic
from .db import init_db, add_bookmark, list_bookmarks
from rich.console import Console

console = Console()

def main():
    parser = argparse.ArgumentParser(description="AO3 Terminal Client")
    subparsers = parser.add_subparsers(dest="command")

    # search command
    search_parser = subparsers.add_parser("search", help="Search AO3 works")
    search_parser.add_argument("query", help="Search query (tags, ships, etc.)")
    search_parser.add_argument("--page", type=int, default=1, help="Page number")
    search_parser.add_argument("--sort", default="kudos", help="Sort by (kudos, hits, date)")
    search_parser.add_argument("--complete", action="store_true", help="Only completed works")
    search_parser.add_argument("--rating", default=None, help="Filter by rating (G, T, M, E)")

    # read command
    read_parser = subparsers.add_parser("read", help="Read a fic by URL")
    read_parser.add_argument("url", help="AO3 work URL")

    # bookmark add
    bm_add_parser = subparsers.add_parser("bookmark", help="Bookmark a fic")
    bm_add_parser.add_argument("url", help="AO3 work URL")
    bm_add_parser.add_argument("title", help="Title of the fic")

    # list bookmarks
    subparsers.add_parser("bookmarks", help="List all bookmarks")

    args = parser.parse_args()

    init_db()

    if args.command == "search":
        search_ao3(args.query, args.page, args.sort, args.complete, args.rating)
    elif args.command == "read":
        read_fic(args.url)
    elif args.command == "bookmark":
        add_bookmark(args.url, args.title)
    elif args.command == "bookmarks":
        list_bookmarks()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
