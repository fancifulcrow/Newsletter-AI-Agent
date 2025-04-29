from semantic_kernel.kernel import Kernel
from semantic_kernel.prompt_template import PromptTemplateConfig
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.ollama.ollama_prompt_execution_settings import OllamaChatPromptExecutionSettings
import asyncio

from plugins.news_collector import NewsCollectorPlugin
import smtplib
from email.message import EmailMessage
import markdown
import os
import re
from dotenv import load_dotenv
import yaml


load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


async def main():
    config_path = "config/default.yaml"
    with open(config_path, mode="r") as f:
        config = yaml.safe_load(f)

    kernel = Kernel()

    service_id = "ollama"
    kernel.add_service(
        OllamaChatCompletion(
            service_id=service_id,
            host=config["ollama"]["host"],
            ai_model_id=config["ollama"]["model"],
        )
    )

    execution_settings = OllamaChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    news_collector = kernel.add_plugin(
        NewsCollectorPlugin(config["topics"], NEWS_API_KEY), 
        plugin_name="NewsCollectorPlugin"
    )

    raw_articles = await kernel.invoke(news_collector["search_news"])

    prompt = """
        You are an AI assistant that creates a detailed and insightful daily newsletter based on the following news articles.

        Your job is to create your own article(s) by:
        1. Extracting the most important points from the articles.
        2. Identifying the sources and group similar news together along with their links.
        3. Detect and comment on any apparent bias or tone (e.g., sensationalism, political leaning).
        4. Highlight contradictions or differing perspectives across articles.
        5. Format the newsletter with clear section titles.

        It is important that you reply with only your articles.

        News Articles:
        {{$input}}

        Newsletter:
    """

    news_summarizer = kernel.add_function(
        function_name="NewsSummarizer",
        plugin_name="summarizePlugin",
        prompt_template_config=PromptTemplateConfig(
            template=prompt,
            name="summarize",
            template_format="semantic-kernel",
            execution_settings=execution_settings
        ),
    )

    newsletter = await kernel.invoke(news_summarizer, input=raw_articles)
    newsletter = str(newsletter)
    newsletter = re.sub(r"<think>.*?</think>", "", newsletter, flags=re.DOTALL).strip() # Remove the think tag

    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(user=EMAIL_ADDRESS, password=EMAIL_PASSWORD)

        msg = EmailMessage()
        msg["Subject"] = "Newsletter"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS

        html_content = markdown.markdown(newsletter)

        msg.set_content(newsletter)  # fallback for clients that don't support HTML
        msg.add_alternative(html_content, subtype="html")

        connection.send_message(msg)


if __name__ == "__main__":
    asyncio.run(main())
