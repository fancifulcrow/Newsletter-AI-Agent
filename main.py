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
        You are an AI assistant that writes a detailed and grounded newsletter based on recent news articles. You are not a marketing assistant, and you must not add fluff or emojis.

        Your task is to create full-length article-style sections by:
        1. Extracting diverse and newsworthy topics.
        2. Grouping similar articles together.
        3. Commenting on any apparent bias or tone (e.g., sensationalism, political leaning).
        4. Highlighting contradictions or differing viewpoints across sources.
        5. Writing in a natural, grounded tone—avoid bullet points, headings like “Key Takeaways”, or emojis.
        6. Elaborating thoughtfully: each section should be 1-2 full paragraphs.
        7. Starting each section with a **short and clear headline**, followed by the body text in prose.

        **The structure should be:**
        - A headline (single line, Title Case)
        - 1 or 2 paragraphs explaining the news
        - A line break (then the next section)

        DO NOT include:
        - A summary or outline
        - Key takeaways
        - Emojis or final sign-offs like "Stay tuned"
        - Anything before or after the newsletter (no greetings or conclusions)

        News Articles:
        {{$input}}

        Newsletter:
    """

    news_writer = kernel.add_function(
        function_name="NewsWriter",
        plugin_name="NewsWriterPlugin",
        prompt_template_config=PromptTemplateConfig(
            template=prompt,
            name="writer",
            template_format="semantic-kernel",
            execution_settings=execution_settings
        ),
    )

    newsletter = await kernel.invoke(news_writer, input=raw_articles)
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
