import unittest
from Refibibex import generate_citekey

class TestGenerateCitekey(unittest.TestCase):

    def test_lastname_first(self):
        self.assertEqual(generate_citekey("Borges, Jorge Luis", "2023"), "borges2023")

    def test_firstname_last(self):
        self.assertEqual(generate_citekey("Jorge Luis Borges", "2023"), "borges2023")

    def test_compound_lastname(self):
        self.assertEqual(generate_citekey("DE SOUZA, Fulano", "2023"), "souza2023")

    def test_no_author(self):
        self.assertEqual(generate_citekey("", "2023"), "anon2023")
        self.assertEqual(generate_citekey(None, "2023"), "anon2023")

if __name__ == '__main__':
    unittest.main()