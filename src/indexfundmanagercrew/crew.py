from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from indexfundmanagercrew.tools.research_tools.cookie_tool import CookieFilterTool, AgentDetailTool, TweetSearchTool
from indexfundmanagercrew.tools.research_tools.defillama_tool import PriceFetcherAgent, ProtocolInfoTool, TVLMetricsTool
from indexfundmanagercrew.tools.api.Cookie import CookieAPI, create_production_instance, CookieAPIError
import os
import logging
import asyncio

logger = logging.getLogger(__name__)

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Indexfundmanagercrew():
	"""Indexfundmanagercrew crew"""

	@before_kickoff
	def check_api_status(self, inputs):
		"""Check the status of required APIs before starting the crew."""
		logger.info("Checking API status before starting the crew...")

		# Check Cookie API status with a test agent lookup
		try:
			cookie_api = create_production_instance()
			# Test with get_agents_paged which should always work
			test_response = cookie_api.get_agents_paged(interval="_3Days", page=1, page_size=1)
			if test_response and 'data' in test_response:
				logger.info("Cookie API Status: OK (Agents listing working)")
				logger.info(f"Total agents available: {test_response.get('totalCount', 'unknown')}")
			else:
				logger.warning("Cookie API Status: Response format unexpected")
			logger.info("Note: Twitter search functionality might be limited")
		except CookieAPIError as e:
			logger.warning(f"Cookie API Status: Error - {str(e)}")
		except Exception as e:
			logger.warning(f"Cookie API Status: Unexpected Error - {str(e)}")

		# Check DefiLlama API status with a simple price check
		try:
			price_fetcher = PriceFetcherAgent()
			# Test with ETH price check
			test_price = price_fetcher._run("ethereum", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
			if "Error" not in test_price:
				logger.info(f"DefiLlama API Status: OK - {test_price}")
			else:
				logger.warning(f"DefiLlama API Status: {test_price}")
		except Exception as e:
			logger.warning(f"DefiLlama API Status: Error - {str(e)}")

		return inputs

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def researcher(self) -> Agent:
		cookie_filter = CookieFilterTool()
		agent_detail = AgentDetailTool()
		tweet_search = TweetSearchTool()
		price_fetcher = PriceFetcherAgent()
		protocol_info = ProtocolInfoTool()
		tvl_metrics = TVLMetricsTool()
		return Agent(
			config=self.agents_config['researcher'],
			verbose=True,
			tools=[cookie_filter, agent_detail, tweet_search, price_fetcher, protocol_info, tvl_metrics],
			llm_config={
				"provider": "google",
				"model": "gemini-1.5-pro",
				"api_key": os.getenv("GEMINI_API_KEY"),
				"config": {
					"temperature": 0.7,
					"top_p": 0.9
				}
			}
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			verbose=True,
			llm_config={
				"provider": "google",
				"model": "gemini-1.5-pro",
				"api_key": os.getenv("GEMINI_API_KEY"),
				"config": {
					"temperature": 0.7,
					"top_p": 0.9
				}
			}
		)

	@agent
	def manager(self) -> Agent:
		return Agent(
			config=self.agents_config['manager'],
			verbose=True,
			llm_config={
				"provider": "google",
				"model": "gemini-1.5-pro",
				"api_key": os.getenv("GEMINI_API_KEY"),
				"config": {
					"temperature": 0.7,
					"top_p": 0.9
				}
			}
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			output_file='report.md'
		)

	@task
	def data_gathering_task(self) -> Task:
		return Task(
			config=self.tasks_config['data_gathering_task']
		)

	@task
	def daily_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['daily_analysis_task']
		)

	@task
	def publish_website_task(self) -> Task:
		return Task(
			config=self.tasks_config['publish_website_task']
		)

	@task
	def publish_twitter_task(self) -> Task:
		return Task(
			config=self.tasks_config['publish_twitter_task']
		)

	@task
	def weekly_decision_task(self) -> Task:
		return Task(
			config=self.tasks_config['weekly_decision_task']
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Indexfundmanagercrew crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		# Create a list of agents excluding the manager
		crew_agents = [self.researcher(), self.reporting_analyst()]

		return Crew(
			agents=crew_agents, # Only include non-manager agents
			tasks=self.tasks, # Automatically created by the @task decorator
			manager_agent=self.manager(),
			process=Process.hierarchical,
			verbose=True,
			memory=True,
			llm_config={
				"provider": "google",
				"model": "gemini-1.5-pro",
				"api_key": os.getenv("GEMINI_API_KEY"),
				"config": {
					"temperature": 0.7,
					"top_p": 0.9
				}
			}
		)
