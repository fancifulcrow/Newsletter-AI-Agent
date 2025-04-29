from semantic_kernel.functions import kernel_function
import requests
from newspaper import Article
from dotenv import load_dotenv
from datetime import date, timedelta
from typing import Dict, List


load_dotenv()


class NewsCollectorPlugin:
    def __init__(self, topics:List[str], NEWS_API_KEY:str):
        self.topics = topics
        self.news_endpoint = "https://newsapi.org/v2/everything"
        self.news_api_key = NEWS_API_KEY

    @kernel_function
    async def search_news(self) -> List[Dict]:
        """Gets a list containing all of the top relevant news articles in the past day"""
        articles = []
        today = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d") # API has a 24 hour delay for free tiers.

        for topic in self.topics:
            params = {
                "apikey": self.news_api_key,
                "q": topic,
                "from": today,
                "pageSize": 10,
                "language": "en",
                "sortBy": "relevancy"
            }

            try:
                response = requests.get(url=self.news_endpoint, params=params)
                response.raise_for_status()
                data = response.json()

                for article in data.get("articles", []):
                    url = article.get("url")
                    article = {
                        "title": article["title"],
                        "source": article["source"]["name"],
                        "content": self.extract_text_from_url(url)
                    }
                    articles.append(article)
            except:
                pass
            
        return articles
    
    def extract_text_from_url(self, url:str) -> str:
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text
        except:
            return ""
