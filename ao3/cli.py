import argparse
from .reader import search_ao3, read_fic
from .db import init_db, add_bookmark, list_bookmarks, remove_bookmark
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
    
    # unbookmark
    unbm_parser = subparsers.add_parser("unbookmark", help="Remove a bookmark")
    unbm_parser.add_argument("id", type=int, help="ID of bookmark to remove")


    # list bookmarks
    subparsers.add_parser("bookmarks", help="List all bookmarks")

    args = parser.parse_args()

    init_db()

    if args.command == "search":
        results = search_ao3(args.query, args.page, args.sort, args.complete, args.rating, return_list=True)
        if not results:
            console.print("[red]No results found[/red]")
        else:
            console.print(f"[green]Search results for '{args.query}':[/green]")
            for i, work in enumerate(results, 1):
                console.print(f"{i}. {work['title']} by {work['author']} - {work['link']}")

    elif args.command == "read":
        content = read_fic(args.url)
        if not content:
            console.print("[red]Failed to fetch the fic.[/red]")
        else:
             # Optional pagination for long fics
            CHUNK_SIZE = 3000
            for i in range(0, len(content), CHUNK_SIZE):
                console.print(content[i:i+CHUNK_SIZE])

    elif args.command == "bookmark":
        add_bookmark(args.url, args.title)
        console.print(f"[green]Bookmarked:[/green] {args.title}")

    elif args.command == "bookmarks":
        bookmarks = list_bookmarks(return_list=True)
        if not bookmarks:
            console.print("[yellow]No bookmarks found.[/yellow]")
        else:
            console.print("[green]Bookmarks:[/green]")
            for i, bm in enumerate(bookmarks, 1):
                console.print(f"{i}. {bm[1]} - {bm[2]}")

    elif args.command == "unbookmark":
        bookmarks = list_bookmarks(return_list=True)
        if 1 <= args.id <= len(bookmarks):
            bm_to_remove = bookmarks[args.id - 1]  # display number → DB ID
            remove_bookmark(bm_to_remove[0])
            console.print(f"[green]Removed bookmark:[/green] {bm_to_remove[1]}")
        else:
            console.print("[red]Invalid bookmark number[/red]")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
