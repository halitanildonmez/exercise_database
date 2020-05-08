from bs4 import BeautifulSoup

# uses Beautiful Soup to parse the
class WorkoutPageParser:
    def __init__(self, html_content, workout_table):
        self.html = html_content
        self.table_vals = workout_table

    # takes the html table and appends the new values to the end
    def insert_into_html(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        table_soup = BeautifulSoup(self.table_vals, 'html.parser')
        table = soup.find("table", {"id": "workout_links_table"})
        table.append(table_soup)
        return soup.prettify()
