import os
from datetime import datetime
from typing import Dict, Any
import git
from pathlib import Path

class WebsitePublisher:
    def __init__(self):
        self.content_dir = os.getenv("WEBSITE_CONTENT_DIR", "website/content/daily")
        self.repo_path = os.getenv("WEBSITE_REPO_PATH", ".")
        
    def format_daily_discussion(self, analysis_data: Dict[str, Any]) -> str:
        """Format the daily discussion into a markdown post."""
        date = datetime.now().strftime("%Y-%m-%d")
        
        # Start with the frontmatter
        content = [
            "---",
            f"title: 'Daily AI Agent Token Discussion - {date}'",
            f"date: '{datetime.now().isoformat()}'",
            "type: 'daily-discussion'",
            "---",
            "",
            f"# Daily Discussion Notes - {date}",
            "",
            "## Today's Key Points",
            ""
        ]
        
        # Add the discussion content
        discussion = analysis_data.get('daily_discussion')
        if discussion:
            content.extend(discussion.split('\n'))
            
        # Add any specific debates
        if 'debates' in analysis_data:
            content.extend([
                "",
                "## Key Debates",
                ""
            ])
            for debate in analysis_data['debates']:
                content.extend([
                    f"### {debate['topic']}",
                    "",
                    "**Bull Case:**",
                    debate.get('bull_case', 'No bull case presented'),
                    "",
                    "**Bear Case:**",
                    debate.get('bear_case', 'No bear case presented'),
                    "",
                    "**Team's Current Take:**",
                    debate.get('conclusion', 'Discussion ongoing'),
                    ""
                ])
        
        # Add sentiment and next steps
        if 'sentiment' in analysis_data:
            content.extend([
                "",
                "## Current Sentiment",
                "",
                analysis_data['sentiment']
            ])
            
        if 'next_steps' in analysis_data:
            content.extend([
                "",
                "## Next Steps",
                "",
                analysis_data['next_steps']
            ])
            
        return "\n".join(content)
        
    def save_discussion(self, content: str) -> str:
        """Save the discussion as a markdown file."""
        # Create the content directory if it doesn't exist
        os.makedirs(self.content_dir, exist_ok=True)
        
        # Create filename based on date
        date = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date}-daily-discussion.md"
        filepath = os.path.join(self.content_dir, filename)
        
        # Save the content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return filepath
        
    def publish_to_git(self, filepath: str):
        """Commit and push the new content to git."""
        try:
            repo = git.Repo(self.repo_path)
            
            # Stage the new file
            repo.index.add([filepath])
            
            # Create commit
            date = datetime.now().strftime("%Y-%m-%d")
            commit_message = f"Add daily discussion for {date}"
            repo.index.commit(commit_message)
            
            # Push to origin
            origin = repo.remote('origin')
            origin.push()
            
        except Exception as e:
            raise Exception(f"Failed to publish to git: {str(e)}")
            
    def publish(self, analysis_data: Dict[str, Any]):
        """Main method to publish the daily discussion."""
        try:
            # Format the content
            content = self.format_daily_discussion(analysis_data)
            
            # Save to file
            filepath = self.save_discussion(content)
            
            # Publish to git
            self.publish_to_git(filepath)
            
            return {
                "status": "success",
                "filepath": filepath
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            } 