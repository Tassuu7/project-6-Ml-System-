import unittest
from datamorph.core.dataframe import DataFrame
from datamorph.transformers.text.cleaner import TextCleaner
from datamorph.transformers.text.tfidf import TFIDFVectorizer

class TestText(unittest.TestCase):
    def test_text_cleaner(self):
        df = DataFrame({"text": ["Hello WORLD! 123", "Data Preprocessing..."]})
        cleaner = TextCleaner(columns=["text"])
        res = cleaner.fit_transform(df)
        self.assertEqual(res["text"][0], "hello world 123")

    def test_tfidf(self):
        df = DataFrame({"review": ["great machine learning model", "deep learning machine neural network"]})
        tfidf = TFIDFVectorizer(columns=["review"])
        res = tfidf.fit_transform(df)
        self.assertTrue(any("tfidf" in col for col in res.columns))

if __name__ == "__main__":
    unittest.main()
