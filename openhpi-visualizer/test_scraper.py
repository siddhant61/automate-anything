import unittest
from scraper import scrape_courses_data

class TestScraper(unittest.TestCase):
    def test_scrape_courses_data(self):
        """
        Tests that the scrape_courses_data function returns a list of courses.
        """
        courses_data = scrape_courses_data('https://open.hpi.de/courses')
        self.assertIsInstance(courses_data, list)
        self.assertGreater(len(courses_data), 0)

if __name__ == '__main__':
    unittest.main()
