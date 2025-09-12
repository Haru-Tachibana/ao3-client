import requests
from bs4 import BeautifulSoup

def search_ao3(query, return_list=False):
    """Return simplified search results as list of dicts for TUI"""
    url = "https://archiveofourown.org/works/search"
    params = {"commit": "Search", "work_search[query]": query}
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    results = soup.find_all("li", class_="work blurb group")
    output = []
    for work in results[:10]:  # limit for UI
        title_tag = work.find("h4", class_="heading")
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        link = "https://archiveofourown.org" + title_tag.a['href']
        author = work.find("a", rel="author").get_text(strip=True)
        summary = work.find("blockquote", class_="userstuff summary")
        summary_text = summary.get_text(strip=True) if summary else ""
        output.append({"title": title, "author": author, "link": link, "summary": summary_text})
    if return_list:
        return output
    return output

def read_fic(url):
    """
    Fetch the full text of a work from AO3.
    Currently returns plain text of first chapter as placeholder.
    """
    import requests
    from bs4 import BeautifulSoup

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    
    chapter = soup.find("div", class_="userstuff")
    text = chapter.get_text("\n", strip=True) if chapter else "[No text found]"
    
    return text
