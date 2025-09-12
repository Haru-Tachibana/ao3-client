import requests
from bs4 import BeautifulSoup
from rich.console import Console

console = Console()

def search_ao3(query, page=1, sort="kudos", complete=False, rating=None):
    base = "https://archiveofourown.org/works/search"
    params = {
        "commit": "Search",
        "page": page,
        "work_search[query]": query,
        "work_search[sort_column]": sort
    }
    if complete:
        params["work_search[complete]"] = "T"
    if rating:
        params["work_search[rating_ids]"] = rating_map().get(rating.upper(), "")

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(base, headers=headers, params=params)
    if r.status_code != 200:
        console.print(f"[red]Error: {r.status_code}[/red]")
        return

    soup = BeautifulSoup(r.text, "html.parser")
    results = soup.find_all("li", class_="work blurb group")

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    for i, work in enumerate(results, 1):
        title_tag = work.find("h4", class_="heading")
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        link = "https://archiveofourown.org" + title_tag.a['href']
        author = work.find("a", rel="author").get_text(strip=True)
        summary = work.find("blockquote", class_="userstuff summary")
        summary_text = summary.get_text(strip=True) if summary else "No summary"
        console.print(f"[cyan]{i}. {title}[/cyan] by [magenta]{author}[/magenta]")
        console.print(f"   {link}")
        console.print(f"   [green]{summary_text}[/green]\n")

def read_fic(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url + "?view_adult=true&view_full_work=true", headers=headers)
    if r.status_code != 200:
        console.print(f"[red]Error: {r.status_code}[/red]")
        return

    soup = BeautifulSoup(r.text, "html.parser")
    chapters = soup.find_all("div", class_="userstuff")

    console.print(f"[bold underline green]Reading Fic: {url}[/bold underline green]\n")
    for chapter in chapters:
        text = chapter.get_text(separator="\n", strip=True)
        console.print(text + "\n---\n")

def rating_map():
    return {
        "G": "10",   # General
        "T": "11",   # Teen
        "M": "12",   # Mature
        "E": "13"    # Explicit
    }
