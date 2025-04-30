# Newsletter AI Agent

## Overview

This Python-based application automatically generates and emails a well-structured, insightful daily newsletter using real-time news articles and an LLM (via Ollama). The system gets the latest news on configurable topics, summarizes and analyzes them, and sends an email digest.

## Requirements

- Python 3.8 and above
- An [Ollama](https://ollama.com/) LLM instance running locally or accessible via network
- [News API](https://newsapi.org/) key (e.g., from NewsAPI)
- Gmail account (or any SMTP server)

## Setup
1. **Clone the repository**

2. **Install dependencies**  
    You can use a virtual environment if preferred.
    ```bash
    pip install -r requirements.txt
    ```

3. **Create a `.env` file.**  
    Create a .env file in the root directory with the following variables:
    ```ini
    NEWS_API_KEY=your_newsapi_key
    EMAIL_ADDRESS=your_email@gmail.com
    EMAIL_PASSWORD=your_app_password
    ```

4. **Configure topics and model**  
    Edit `config/default.yaml` to set your news topics and the Ollama model configuration:
    ```yaml
    ollama:
        host: "http://localhost:11434"
        model: "llama3"
    
    topics:
        - technology
        - politics
    ```

## Running the Project

To run the script and send your daily newsletter:
```bash
python main.py
```
> Make sure your Ollama model is running before executing the script.

You may choose to run this script periodically using a scheduler like:
- cron (Linux/macOS)
- Task Scheduler (Windows)
- watchdog, APScheduler, or other Python-based solutions

This allows you to automate daily delivery of your newsletter without manual intervention.

## Example Output

```markdown
# Newsletter: Key Election and Policy Developments

1. **Wales Votes on Climate Emergency**
The Welsh government has passed a landmark law declaring a climate emergency, backed by the Welsh Assembly. Environment Minister Bethan Jenkins emphasized the need for public support to meet emissions targets and transition to renewable energy. A consultation on the 2050 net-zero goal will follow, with plans to phase out fossil fuels and boost green infrastructure.

2. **UK Election Results: Conservatives Win, Labour Faces Challenges**
The Conservative Party secured a narrow victory in the UK general election, though their majority is smaller than expected. Labour leader Kier Starmer is addressing the party’s struggles to gain public trust. Meanwhile, Green Party co-leader Elizabeth May retained her Saanich-Gulf Islands seat in Canada, while the party’s overall vote share dropped to 1.2%—a significant decline.

3. **UK’s New Energy Strategy: 40 GW of Onshore Wind by 2030**
The UK government unveiled a plan to invest £3.3 billion in renewable energy, targeting 40 GW of onshore wind capacity by 2030. The strategy includes expanding offshore wind, hydrogen projects, and grid upgrades. National Grid will play a key role in managing the transition, with public consultations to shape the rollout.

4. **Green Party’s Elizabeth May: Defending Environmental Leadership**
In Canada, Green Party co-leader Elizabeth May won her fifth term in Saanich-Gulf Islands, citing her grassroots campaign and focus on environmental issues. She criticized mainstream media for promoting a two-party race and defended the Greens’ role in economic sovereignty. However, the party’s overall vote share fell, with co-leader Jonathan Pedneault finishing fifth in Quebec.

5. **Climate and Energy: A Global Focus**
From Wales’ climate emergency to the UK’s renewable energy push, the focus on decarbonization remains central. Leaders are balancing immediate policy goals with long-term sustainability, while parties like the Greens face challenges in expanding their influence beyond environmental issues.

Stay tuned for updates on how these developments shape global climate and energy policies.
```