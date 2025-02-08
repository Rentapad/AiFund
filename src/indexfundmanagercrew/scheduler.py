from datetime import datetime
import asyncio
from apscheduler.schedulers.blocking import BlockingScheduler
from crew import Indexfundmanagercrew
from memory_store import MemoryStore


def run_data_gathering_task():
    try:
        crew_instance = Indexfundmanagercrew()
        inputs = {'topic': 'AI Agent tokens', 'current_day': str(datetime.now().day)}
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
        inputs = {'topic': 'AI Agent Tokens', 'current_day': str(datetime.now().day)}
        print(f"[{datetime.now()}] Starting daily analysis task")
        result = crew_instance.daily_analysis_task().kickoff(inputs=inputs)
        print(f"[{datetime.now()}] Daily analysis completed. Result: {result}")
        
        # Process the analysis results
        if isinstance(result, dict):
            # Check if we have a discussion field
            discussion = result.get('daily_discussion') or result.get('discussion')
            
            if not discussion and isinstance(result.get('analysis'), str):
                # If no explicit discussion field, use the analysis as the discussion
                result['daily_discussion'] = result['analysis']
            elif not discussion and isinstance(result.get('analysis'), dict):
                # If analysis is a dict, create a discussion from its contents
                discussion_parts = []
                
                # Add key findings and insights
                if 'findings' in result['analysis']:
                    discussion_parts.extend(result['analysis']['findings'])
                
                # Add notable developments
                if 'developments' in result['analysis']:
                    discussion_parts.extend(result['analysis']['developments'])
                
                # Add recommendations if any
                if 'recommendations' in result['analysis']:
                    recs = result['analysis']['recommendations']
                    if isinstance(recs, list):
                        discussion_parts.extend(recs)
                    else:
                        discussion_parts.append(str(recs))
                
                if discussion_parts:
                    result['daily_discussion'] = ". ".join(discussion_parts)
        
        store = MemoryStore()
        store.update_memory('daily_analysis_last_run', datetime.now().isoformat())
        store.update_memory('daily_analysis_result', result)
    except Exception as e:
        print(f"[{datetime.now()}] Error in daily analysis task: {e}")


def run_publish_website_task():
    try:
        crew_instance = Indexfundmanagercrew()
        inputs = {'topic': 'AI Agent Tokens', 'current_day': str()}
        print(f"[{datetime.now()}] Starting website publication task")
        result = crew_instance.publish_website_task().kickoff(inputs=inputs)
        print(f"[{datetime.now()}] Website publication completed. Result: {result}")
        store = MemoryStore()
        store.update_memory('publish_website_last_run', datetime.now().isoformat())
        store.update_memory('publish_website_result', result)
    except Exception as e:
        print(f"[{datetime.now()}] Error in website publication task: {e}")


def run_twitter_task_wrapper():
    """Wrapper function to run the async Twitter task in the scheduler."""
    asyncio.run(run_publish_twitter_task())


async def run_publish_twitter_task():
    """Publishes daily analysis to Twitter."""
    try:
        # Get the latest analysis results from memory store
        store = MemoryStore()
        daily_analysis_result = store.get_memory('daily_analysis_result')
        
        if not daily_analysis_result:
            print(f"[{datetime.now()}] No daily analysis results found for Twitter publication")
            return
            
        from tools.social.twitter_publisher import TwitterPublisher
        publisher = TwitterPublisher()
        result = await publisher.publish_daily_analysis(daily_analysis_result)
        
        if result["status"] == "success":
            print(f"[{datetime.now()}] Twitter publication completed successfully. "
                  f"Published {result['tweet_count']} tweets.")
            store.update_memory('publish_twitter_last_run', datetime.now().isoformat())
            store.update_memory('publish_twitter_result', result)
        else:
            print(f"[{datetime.now()}] Twitter publication failed: {result['error']}")
            store.update_memory('publish_twitter_result', result)
            
    except Exception as e:
        error_msg = f"Error in Twitter publication task: {str(e)}"
        print(f"[{datetime.now()}] {error_msg}")
        store = MemoryStore()
        store.update_memory('publish_twitter_result', {
            "status": "error",
            "error": error_msg
        })


def run_weekly_decision_task():
    try:
        crew_instance = Indexfundmanagercrew()
        inputs = {'topic': 'Base Chain AI Agent Tokens', 'current_day': str(datetime.now().day)}
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
    scheduler.add_job(run_twitter_task_wrapper, 'cron', hour=20, minute=17, id='publish_twitter')

    # Schedule weekly decision task (e.g., every Sunday at 8:00 PM)
    scheduler.add_job(run_weekly_decision_task, 'cron', day_of_week='sun', hour=20, minute=0, id='weekly_decision')

    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.") 