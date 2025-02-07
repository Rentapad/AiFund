import schedule
import time
import datetime
import os
from src.crews.data_gathering_crew import create_data_gathering_crew_instance
from src.crews.data_analysis_crew import create_data_analysis_crew_instance
from src.utils.publishing import publish_to_website, generate_twitter_summary


def run_daily_tasks(data_gathering_crew, data_analysis_crew, data_gathering_tasks, data_analysis_tasks, day_of_week):
    (
        daily_data_gathering_task_morning,
        daily_data_gathering_task_evening,
    ) = data_gathering_tasks

    (
        daily_data_analysis_task,
        weekly_decision_making_task,
        manager_final_action_task
    ) = data_analysis_tasks

    daily_analysis_output = None # Capture output
    weekly_decision_output = None # Capture weekly decision output


    print("Running Morning Data Gathering Task...")
    data_gathering_crew.kickoff(tasks=[daily_data_gathering_task_morning], inputs={'day': datetime.datetime.now().strftime("%Y-%m-%d")})
    print("Morning Data Gathering Task Completed.")

    print("Running Evening Data Gathering Task...")
    data_gathering_crew.kickoff(tasks=[daily_data_gathering_task_evening], inputs={'day': datetime.datetime.now().strftime("%Y-%m-%d")})
    print("Evening Data Gathering Task Completed.")

    print("Running Daily Data Analysis Task...")
    daily_analysis_result = data_analysis_crew.kickoff(tasks=[daily_data_analysis_task], inputs={'day': datetime.datetime.now().strftime("%Y-%m-%d")})
    print("Daily Data Analysis Task Completed.")
    daily_analysis_output = daily_analysis_result.output.raw if daily_analysis_result and daily_analysis_result.output else "No daily analysis output." # Capture output


    if day_of_week == 'Sunday': # Assuming Sunday is end of week for decision
        print("Running Weekly Decision Making Task...")
        weekly_decision_result = data_analysis_crew.kickoff(tasks=[weekly_decision_making_task], inputs={'week_ending': datetime.datetime.now().strftime("%Y-%m-%d")})
        print("Weekly Decision Making Task Completed.")
        weekly_decision_output = weekly_decision_result.output.raw if weekly_decision_result and weekly_decision_result.output else "No weekly decision output." # Capture output


        print("Running Manager Final Action Task...")
        manager_final_action_result = data_analysis_crew.kickoff(tasks=[manager_final_action_task], inputs={'week_ending': datetime.datetime.now().strftime("%Y-%m-%d")})
        print("Manager Final Action Task Completed.")

        # Publish to website and Twitter on Sundays after weekly decision
        if daily_analysis_output and weekly_decision_output: # Check if outputs were captured
            publish_to_website(daily_analysis_output, weekly_decision_output, day_of_week)
            twitter_summary = generate_twitter_summary(weekly_decision_output)
            print(f"\nTwitter Summary:\n{twitter_summary}")
        else:
            print("Could not generate website or twitter content due to missing outputs.")


def main():
    topic = 'Market Trends in AI Agents' # Define your topic here

    # Create Crews and Tasks Instances
    data_gathering_crew, data_gathering_tasks = create_data_gathering_crew_instance(topic)
    data_analysis_crew, data_analysis_tasks = create_data_analysis_crew_instance(topic)


    # Daily schedule
    schedule.every().day.at("08:00").do(lambda: run_daily_tasks(data_gathering_crew, data_analysis_crew, data_gathering_tasks, data_analysis_tasks, datetime.datetime.now().strftime("%A"))) # Morning gathering
    schedule.every().day.at("20:00").do(lambda: run_daily_tasks(data_gathering_crew, data_analysis_crew, data_gathering_tasks, data_analysis_tasks, datetime.datetime.now().strftime("%A"))) # Evening gathering & analysis + weekly on Sunday

    print("Crew system scheduled. Running initial daily tasks...")
    run_daily_tasks(data_gathering_crew, data_analysis_crew, data_gathering_tasks, data_analysis_tasks, datetime.datetime.now().strftime("%A")) # Run initial daily tasks right away


    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()