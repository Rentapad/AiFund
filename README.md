# Indexfundmanagercrew Crew

Welcome to the Indexfundmanagercrew Crew project, powered by [crewAI](https://crewai.com) and [cookie.fun dataswarm API](https://cookie.fun). This project was developed for the Cookie Hackathon with the goal of creating an AI-managed index fund that leverages both on-chain metrics and social signals from influential crypto voices to make informed investment decisions.

## Hackathon & Evaluation Process

Our AI agents operate on a structured weekly schedule:
- Every day at 8 PM, the agents analyze market data, social metrics, and on-chain indicators
- Daily insights and analysis are published on our [website](https://aifolio-two.vercel.app/) and Twitter
- After a week of thorough analysis, agents decide whether to create a new index fund
- If approved, the index fund composition is determined based on accumulated data and insights

You can follow our daily updates and join the conversation at [aifolio-two](https://aifolio-two.vercel.app/).

## Installation

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```

### Customizing

**Add your `OPENAI_API_KEY` and `COOKIE_API_KEY` into the `.env` file**

- Modify `src/indexfundmanagercrew/config/agents.yaml` to define your agents
- Modify `src/indexfundmanagercrew/config/tasks.yaml` to define your tasks
- Modify `src/indexfundmanagercrew/crew.py` to add your own logic, tools and specific args
- Modify `src/indexfundmanagercrew/main.py` to add custom inputs for your agents and tasks

## Blockchain Integration

Our project includes integrated Web3 tools that enable your AI agents to interact with the blockchain, specifically focusing on index fund token management on the Base chain (chain_id: 8453). The tools allow for:

- **Index Fund Management:** Creating and managing index fund tokens using the module in `src/indexfundmanagercrew/tools/web3/index_fund.py`.
- **Token Metrics Analysis:** Gathering on-chain data such as liquidity, TVL, trading volume, price history, and token correlations via `src/indexfundmanagercrew/tools/web3/token_metrics.py`.
- **Social Metrics Analysis:** Evaluating the sentiment, engagement, and influence of smart followers (influential crypto Twitter users) using `src/indexfundmanagercrew/tools/web3/social_metrics.py`.

These tools form the backbone of our data-driven approach, helping the AI agents to make informed decisions about index fund token composition based on both on-chain and social data from cookie.fun dataswarm API.

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the IndexFundManagerCrew Crew, assembling the agents and assigning them tasks as defined in your configuration.

The agents will begin their daily analysis at 8 PM, collecting data and insights that will be published to our website and Twitter. After a week of analysis, they will make a decision about creating a new index fund based on the accumulated data.

## Understanding Your Crew

The IndexFundManagerCrew Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

Furthermore, the integrated Web3 tools empower the crew to interact with the blockchain by performing analytics and management of index fund tokens on the Base chain. These functionalities are designed to support a week-long evaluation period before any index fund is created, ensuring decisions are well-informed by both market data and social metrics from cookie.fun dataswarm API.

## Support

For support, questions, or feedback regarding the Indexfundmanagercrew Crew or crewAI:
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)
- Visit our website: [aifolio-two.vercel.app](https://aifolio-two.vercel.app/)

Let's create wonders together with the power of crewAI and cookie.fun dataswarm API.
