from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListView, ListItem, Button, Input
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
import webbrowser
import asyncio

from ao3.reader import search_ao3, read_fic
from ao3.db import list_bookmarks, add_bookmark, remove_bookmark
from ao3.ebook import export_to_epub


class AO3App(App):
    CSS_PATH = "app.css"
    
    selected_work = reactive(None)
    current_page = reactive(0)
    article_pages = reactive([])
    search_results = reactive([])
    show_search_results = reactive(False)

    def compose(self) -> ComposeResult:
        yield Header()

        # Top row: Search + Sort + Toggle Bookmarks
        with Horizontal(id="top-row"):
            with Horizontal(id="search-left"):
                yield Input(placeholder="Tag, character, author, or URL...", id="search-box")
                yield Button("Search", id="search-btn")
            with Horizontal(id="search-right"):
                yield Button("Sort by Kudos", id="sort-kudos")
                yield Button("Sort by Date", id="sort-date")
                yield Button("Filter Complete", id="sort-complete")
                yield Button("Toggle Bookmarks", id="toggle-bm")

        # Middle: Main article + Results + Sidebar
        with Horizontal(id="middle"):
            # Main content area
            with Vertical(id="main-area"):
                yield VerticalScroll(Static("", id="fic-text", markup=True), id="scroll-content")
                yield ListView(id="results-list")
                with Horizontal(id="page-buttons"):
                    yield Button("Prev Page", id="prev-page")
                    yield Button("Next Page", id="next-page")

            # Sidebar: bookmarks
            with Vertical(id="sidebar"):
                yield ListView(id="bookmarks-list")

        # Bottom row: action buttons
        with Horizontal(id="bottom-row"):
            yield Button("Bookmark/Unbookmark", id="bookmark-btn")
            yield Button("Export EPUB", id="export-btn")
            yield Button("View on AO3", id="view-btn")

        yield Footer()

    async def on_mount(self):
        await self.refresh_bookmarks()
        # Initially hide search results
        self.query_one("#results-list", ListView).visible = False

    def watch_show_search_results(self, show: bool):
        """React to changes in show_search_results"""
        results_list = self.query_one("#results-list", ListView)
        results_list.visible = show

    # ----------------------
    # Bookmarks
    # ----------------------
    def get_bookmark_items(self):
        items = []
        try:
            for i, bm in enumerate(list_bookmarks(return_list=True), 1):
                items.append(
                    ListItem(Button(f"{i}. {bm[1]}", id=f"bookmark-{bm[0]}")))
        except Exception as e:
            # Handle potential database errors
            pass
        return items

    async def refresh_bookmarks(self):
        bookmarks_list = self.query_one("#bookmarks-list", ListView)
        bookmarks_list.clear()
        for item in self.get_bookmark_items():
            bookmarks_list.append(item)

    # ----------------------
    # Button actions
    # ----------------------
    async def on_button_pressed(self, event):
        btn_id = event.button.id

        # Search / sort
        if btn_id == "search-btn":
            query = self.query_one("#search-box", Input).value.strip()
            if query:
                await self.run_search(query)
        elif btn_id in ("sort-kudos", "sort-date", "sort-complete"):
            query = self.query_one("#search-box", Input).value.strip()
            if query:
                sort = btn_id.replace("sort-", "")
                await self.run_search(query, sort=sort)

        # Toggle sidebar
        elif btn_id == "toggle-bm":
            sidebar = self.query_one("#sidebar", Vertical)
            sidebar.visible = not sidebar.visible

        # Bookmark / unbookmark
        elif btn_id == "bookmark-btn" and self.selected_work:
            try:
                bookmarks = list_bookmarks(return_list=True)
                if any(b[2] == self.selected_work["link"] for b in bookmarks):
                    for b in bookmarks:
                        if b[2] == self.selected_work["link"]:
                            remove_bookmark(b[0])
                            break
                else:
                    add_bookmark(
                        self.selected_work["link"], self.selected_work["title"])
                await self.refresh_bookmarks()
            except Exception as e:
                self.update_status(f"[red]Bookmark error: {str(e)}[/red]")

        # Export EPUB
        elif btn_id == "export-btn" and self.selected_work:
            try:
                text = read_fic(self.selected_work["link"])
                export_to_epub(
                    self.selected_work["title"],
                    self.selected_work["author"],
                    [text],
                    f"{self.selected_work['title']}.epub",
                )
                self.update_status(f"[green]Exported {self.selected_work['title']} to EPUB[/green]")
            except Exception as e:
                self.update_status(f"[red]Export error: {str(e)}[/red]")

        # Open in browser
        elif btn_id == "view-btn" and self.selected_work:
            try:
                webbrowser.open(self.selected_work["link"])
            except Exception as e:
                self.update_status(f"[red]Browser error: {str(e)}[/red]")

        # Bookmark clicked
        elif btn_id.startswith("bookmark-"):
            try:
                bookmark_id = int(btn_id.split("-")[1])
                bookmarks = list_bookmarks(return_list=True)
                for b in bookmarks:
                    if b[0] == bookmark_id:
                        await self.load_work({"title": b[1], "link": b[2], "author": "Unknown"})
                        break
            except Exception as e:
                self.update_status(f"[red]Error loading bookmark: {str(e)}[/red]")

        # Search result clicked
        elif btn_id.startswith("work-"):
            try:
                idx = int(btn_id.split("-")[1]) - 1
                if 0 <= idx < len(self.search_results):
                    await self.load_work(self.search_results[idx])
            except Exception as e:
                self.update_status(f"[red]Error loading work: {str(e)}[/red]")

        # Pagination
        elif btn_id == "prev-page":
            if self.current_page > 0:
                self.current_page -= 1
                self.update_page_display()

        elif btn_id == "next-page":
            if self.article_pages and self.current_page < len(self.article_pages) - 1:
                self.current_page += 1
                self.update_page_display()

    # ----------------------
    # Helper methods
    # ----------------------
    def update_status(self, message: str):
        """Update the text display with a status message"""
        textlog = self.query_one("#fic-text", Static)
        textlog.update(message)

    async def load_work(self, work_info: dict):
        """Load a work and display it"""
        try:
            self.selected_work = work_info
            self.update_status("[yellow]Loading work...[/yellow]")
            
            # Load content in thread to avoid blocking
            content = await asyncio.to_thread(read_fic, self.selected_work["link"])
            self.article_pages = self.paginate_text(content)
            self.current_page = 0
            
            # Hide search results and show content
            self.show_search_results = False
            self.update_page_display()
            
        except Exception as e:
            self.update_status(f"[red]Error loading work: {str(e)}[/red]")

    def update_page_display(self):
        """Update the page display"""
        if self.article_pages and 0 <= self.current_page < len(self.article_pages):
            textlog = self.query_one("#fic-text", Static)
            page_info = f"[dim]Page {self.current_page + 1}/{len(self.article_pages)}[/dim]\n\n"
            textlog.update(page_info + self.article_pages[self.current_page])
            
            # Reset scroll to top
            scroll_container = self.query_one("#scroll-content", VerticalScroll)
            scroll_container.scroll_home()

    # ----------------------
    # Search logic
    # ----------------------
    async def run_search(self, query, sort=None):
        results_list = self.query_one("#results-list", ListView)
        results_list.clear()
        self.update_status("[yellow]Searching...[/yellow]")

        try:
            # Run search in thread to avoid blocking
            results = await asyncio.to_thread(search_ao3, query, True)
            
            if not results:
                self.update_status("[red]No results found[/red]")
                self.show_search_results = False
                return

            self.search_results = results

            # Apply sorting/filtering
            if sort == "kudos":
                results.sort(key=lambda x: x.get("kudos", 0), reverse=True)
            elif sort == "date":
                results.sort(key=lambda x: x.get("date", ""), reverse=True)
            elif sort == "complete":
                results = [r for r in results if r.get("complete", False)]
                self.search_results = results

            if not results:
                self.update_status("[red]No results found after filtering[/red]")
                self.show_search_results = False
                return

            # Add search result buttons
            for i, work in enumerate(results, 1):
                title = work.get('title', 'Unknown Title')
                author = work.get('author', 'Unknown Author')
                results_list.append(
                    ListItem(Button(f"{i}. {title} by {author}", id=f"work-{i}")))

            self.update_status("[green]Select a work from the list below[/green]")
            self.show_search_results = True

        except Exception as e:
            self.update_status(f"[red]Search error: {str(e)}[/red]")
            self.show_search_results = False

    # ----------------------
    # Pagination
    # ----------------------
    def paginate_text(self, text: str, chunk_size: int = 3000):
        if not text:
            return ["[red]No content available[/red]"]
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


if __name__ == "__main__":
    AO3App().run()