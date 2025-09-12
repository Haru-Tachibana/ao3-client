from ebooklib import epub
import requests
from bs4 import BeautifulSoup

def export_to_epub(title, author, chapters, filename):
    book = epub.EpubBook()
    book.set_identifier(title)
    book.set_title(title)
    book.set_language('en')
    book.add_author(author)

    epub_chapters = []
    for i, chapter in enumerate(chapters, 1):
        c = epub.EpubHtml(title=f"Chapter {i}", file_name=f'chap_{i}.xhtml', lang='en')
        c.content = f"<h1>Chapter {i}</h1><p>{chapter}</p>"
        book.add_item(c)
        epub_chapters.append(c)

    book.toc = tuple(epub_chapters)
    book.spine = ['nav'] + epub_chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    epub.write_epub(filename, book)
