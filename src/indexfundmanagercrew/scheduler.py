from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from crew import Indexfundmanagercrew
from memory_store import MemoryStore


def run_data_gathering_task():
    try:
        crew_instance = Indexfundmanagercrew()
        inputs = {'topic': 'AI LLMs', 'current_year': str(datetime.now().year)}
        print(f"[{datetime.now()}] Starting data gathering task")
        result = crew_instance.data_gathering_task().kickoff(inputs=inputs)
        print(f"[{datetime.now()}] Data gathering completed. Result: {result}")
        store = MemoryStore()
        store.update_memory('data_gathering_last_run', datetime.now().isoformat())
        store.update_memory('data_gathering_result', result)
    except Exception as e:
        print(f"[{datetime.now()}] Error in data gathering task: {e}")


def run_daily_analysis_task():
    try:
        crew_instance = Indexfundmanagercrew()
        inputs = {'topic': 'AI LLMs', 'current_year': str(datetime.now().year)}
        print(f"[{datetime.now()}] Starting daily analysis task")
        result = crew_instance.daily_analysis_task().kickoff(inputs=inputs)
        print(f"[{datetime.now()}] Daily analysis completed. Result: {result}")
        store = MemoryStore()
        store.update_memory('daily_analysis_last_run', datetime.now().isoformat())
        store.update_memory('daily_analysis_result', result)
    except Exception as e:
        print(f"[{datetime.now()}] Error in daily analysis task: {e}")


def run_publish_website_task():
    try:
        crew_instance = Indexfundmanagercrew()
        inputs = {'topic': 'AI LLMs', 'current_year': str(datetime.now().year)}
        print(f"[{datetime.now()}] Starting website publication task")
        result = crew_instance.publish_website_task().kickoff(inputs=inputs)
        print(f"[{datetime.now()}] Website publication completed. Result: {result}")
        store = MemoryStore()
        store.update_memory('publish_website_last_run', datetime.now().isoformat())
        store.update_memory('publish_website_result', result)
    except Exception as e:
        print(f"[{datetime.now()}] Error in website publication task: {e}")


def run_publish_twitter_task():
    try:
        crew_instance = Indexfundmanagercrew()
        inputs = {'topic': 'AI LLMs', 'current_year': str(datetime.now().year)}
        print(f"[{datetime.now()}] Starting Twitter publication task")
        result = crew_instance.publish_twitter_task().kickoff(inputs=inputs)
        print(f"[{datetime.now()}] Twitter publication completed. Result: {result}")
        store = MemoryStore()
        store.update_memory('publish_twitter_last_run', datetime.now().isoformat())
        store.update_memory('publish_twitter_result', result)
    except Exception as e:
        print(f"[{datetime.now()}] Error in Twitter publication task: {e}")


def run_weekly_decision_task():
    try:
        crew_instance = Indexfundmanagercrew()
        inputs = {'topic': 'AI LLMs', 'current_year': str(datetime.now().year)}
        print(f"[{datetime.now()}] Starting weekly decision task")
        result = crew_instance.weekly_decision_task().kickoff(inputs=inputs)
        print(f"[{datetime.now()}] Weekly decision completed. Result: {result}")
        store = MemoryStore()
        store.update_memory('weekly_decision_last_run', datetime.now().isoformat())
        store.update_memory('weekly_decision_result', result)
    except Exception as e:
        print(f"[{datetime.now()}] Error in weekly decision task: {e}")


if __name__ == '__main__':
    scheduler = BlockingScheduler()

    # Schedule data gathering twice a day (e.g., 9:00 AM and 3:00 PM)
    scheduler.add_job(run_data_gathering_task, 'cron', hour=9, minute=0, id='data_gathering_morning')
    scheduler.add_job(run_data_gathering_task, 'cron', hour=15, minute=0, id='data_gathering_afternoon')

    # Schedule daily analysis at 8:00 PM
    scheduler.add_job(run_daily_analysis_task, 'cron', hour=20, minute=0, id='daily_analysis')

    # Schedule publishing tasks shortly after daily analysis
    scheduler.add_job(run_publish_website_task, 'cron', hour=20, minute=15, id='publish_website')
    scheduler.add_job(run_publish_twitter_task, 'cron', hour=20, minute=17, id='publish_twitter')

    # Schedule weekly decision task (e.g., every Sunday at 8:00 PM)
    scheduler.add_job(run_weekly_decision_task, 'cron', day_of_week='sun', hour=20, minute=0, id='weekly_decision')

    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.") 