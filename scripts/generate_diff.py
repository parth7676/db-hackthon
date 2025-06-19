#!/usr/bin/env python3
"""
Code Diff Generator Script
Generates detailed diffs with customizable context lines and multiple output formats.
"""

import os
import sys
import json
import subprocess
import argparse
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DiffGenerator:
    def __init__(self, context_lines: int = 10, output_dir: str = "diff_output"):
        self.context_lines = context_lines
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def run_git_command(self, command: List[str]) -> Tuple[str, int]:
        """Run a git command and return output and return code."""
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip(), result.returncode
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {' '.join(command)}")
            print(f"Error: {e.stderr}")
            return e.stderr, e.returncode
    
    def check_commit_exists(self, commit_ref: str) -> bool:
        """Check if a commit reference exists."""
        _, return_code = self.run_git_command(["git", "rev-parse", "--verify", commit_ref])
        return return_code == 0
    
    def get_commit_info(self) -> Dict[str, str]:
        """Get information about current and previous commits."""
        # Get current commit
        current_commit, _ = self.run_git_command(["git", "rev-parse", "HEAD"])
        
        # Check if previous commit exists
        if self.check_commit_exists("HEAD~1"):
            # Get previous commit
            prev_commit, _ = self.run_git_command(["git", "rev-parse", "HEAD~1"])
            
            # Get commit messages
            current_msg, _ = self.run_git_command(["git", "log", "-1", "--pretty=format:%s"])
            prev_msg, _ = self.run_git_command(["git", "log", "-1", "--pretty=format:%s", "HEAD~1"])
        else:
            # Only one commit exists - use empty tree as previous
            prev_commit = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"  # Git empty tree
            current_msg, _ = self.run_git_command(["git", "log", "-1", "--pretty=format:%s"])
            prev_msg = "Initial commit (empty tree)"
        
        # Get author info
        author, _ = self.run_git_command(["git", "log", "-1", "--pretty=format:%an"])
        
        return {
            "current_commit": current_commit,
            "previous_commit": prev_commit,
            "current_message": current_msg,
            "previous_message": prev_msg,
            "author": author,
            "timestamp": datetime.now().isoformat(),
            "is_initial_commit": not self.check_commit_exists("HEAD~1")
        }
    
    def generate_diff(self, prev_commit: str, current_commit: str) -> str:
        """Generate diff with specified context lines."""
        diff_cmd = [
            "git", "diff", 
            f"-U{self.context_lines}", 
            prev_commit, 
            current_commit
        ]
        
        diff_output, return_code = self.run_git_command(diff_cmd)
        
        if return_code != 0:
            print(f"Warning: Git diff returned code {return_code}")
            if "fatal: ambiguous argument" in diff_output:
                print("This might be the first commit in the repository.")
        
        return diff_output
    
    def get_changed_files_stats(self, prev_commit: str, current_commit: str) -> str:
        """Get statistics about changed files."""
        stat_cmd = ["git", "diff", "--stat", prev_commit, current_commit]
        stats, return_code = self.run_git_command(stat_cmd)
        
        if return_code != 0:
            return "No statistics available (possibly initial commit)"
        
        return stats
    
    def call_databricks_api(self, diff_content: str) -> Optional[Dict]:
        """
        Call Databricks model serving endpoint for code review.
        
        Args:
            diff_content: The git diff content to analyze
            
        Returns:
            API response as dictionary or None if failed
        """
        url = "https://dbc-477bce68-f9e4.cloud.databricks.com/serving-endpoints/agents_workspace-default-secureguard/invocations"
        token = os.environ.get('DATABRICKS_TOKEN')
        
        if not token:
            print("❌ DATABRICKS_TOKEN not found in environment variables")
            print("Please set the DATABRICKS_TOKEN environment variable or GitHub secret")
            return None
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Create the correct dataframe_split format with proper message structure
        try:
            # Create a data structure with proper message objects
            data = {
                'messages': [
                    {
                        'role': 'user',
                        'content': diff_content
                    }
                ],
                'context': {
                    'conversation_id': 'code_review_session',
                    'user_id': 'github_actions'
                }
            }
            
            # Convert to dataframe_split format
            ds_dict = {
                'dataframe_split': {
                    'data': [data]
                }
            }
            
            # Serialize with allow_nan=True as in the working example
            data_json = json.dumps(ds_dict, allow_nan=True, ensure_ascii=False)
            
            print(f"📤 Sending payload to Databricks API:")
            print(f"   URL: {url}")
            print(f"   Payload format: dataframe_split")
            print(f"   Messages count: {len(data['messages'])}")
            print(f"   Payload size: {len(data_json)} characters")
            
            response = requests.post(url, headers=headers, data=data_json, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Successfully received AI code review")
                print(f"   Response size: {len(response.text)} characters")
                return result
            else:
                print(f"❌ Error calling Databricks endpoint: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON serialization error: {e}")
            return None
        except Exception as e:
            print(f"❌ Exception calling Databricks endpoint: {e}")
            return None
    
    def create_pr_comment(self, ai_review: Dict, diff_content: str, commit_info: Dict[str, str]) -> str:
        """
        Create a PR comment with the AI review results.
        
        Args:
            ai_review: The response from Databricks API
            diff_content: The original diff content
            commit_info: Commit information dictionary
            
        Returns:
            Formatted comment text
        """
        # Extract AI review content from the response
        ai_content = ""
        if isinstance(ai_review, dict):
            # Try to extract the review content from the response
            if 'messages' in ai_review and len(ai_review['messages']) > 0:
                # Get the first message content
                first_message = ai_review['messages'][0]
                if 'content' in first_message:
                    ai_content = first_message['content']
            elif 'predictions' in ai_review:
                ai_content = str(ai_review['predictions'])
            elif 'response' in ai_review:
                ai_content = str(ai_review['response'])
            else:
                ai_content = str(ai_review)
        else:
            ai_content = str(ai_review)
        
        # Parse and format the AI content for better readability
        formatted_review = self._format_ai_review(ai_content)
        
        # Create the comment
        comment = f"""## 🤖 AI Security Code Review - Databricks SecureGuard

### Review Summary
**Previous Commit:** `{commit_info['previous_commit'][:8]}`
**Current Commit:** `{commit_info['current_commit'][:8]}`
**Context Lines:** ±{self.context_lines}
**Review Source:** Databricks Model Serving Endpoint

{formatted_review}

---
*AI analysis provided by Databricks SecureGuard AI*"""
        
        return comment
    
    def _format_ai_review(self, ai_content: str) -> str:
        """
        Format the AI review content to be simple, readable and developer-friendly.
        
        Args:
            ai_content: Raw AI review content
            
        Returns:
            Formatted review content
        """
        if not ai_content:
            return "❌ No AI review content available"
        
        # Simple, clean formatting
        formatted_parts = []
        
        # Extract basic vulnerability info
        if "Path Traversal Vulnerability" in ai_content:
            formatted_parts.append("## 🚨 Security Issue: Path Traversal")
            formatted_parts.append("")
        
        # Extract location
        location = ""
        for line in ai_content.split('\n'):
            if "File:" in line:
                location = line.replace("File:", "").strip()
                break
        
        if location:
            formatted_parts.append(f"**File:** {location}")
        
        # Extract severity
        severity = "High"
        for line in ai_content.split('\n'):
            if "Severity:" in line:
                severity = line.replace("Severity:", "").strip()
                break
        
        formatted_parts.append(f"**Severity:** {severity}")
        formatted_parts.append("")
        
        # Extract CWE
        cwe = ""
        for line in ai_content.split('\n'):
            if "CWE-ID:" in line:
                cwe = line.replace("CWE-ID:", "").strip()
                break
        
        if cwe:
            formatted_parts.append(f"**CWE:** {cwe}")
            formatted_parts.append("")
        
        # Extract description (first meaningful paragraph)
        description = ""
        lines = ai_content.split('\n')
        for i, line in enumerate(lines):
            if "Vulnerability Description:" in line:
                # Get the next meaningful line
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].strip().startswith('###'):
                        description = lines[j].strip()
                        break
                break
        
        if description:
            formatted_parts.append("**Issue:** " + description)
            formatted_parts.append("")
        
        # Extract vulnerable code
        vulnerable_code = ""
        start_idx = ai_content.find("```python")
        if start_idx != -1:
            end_idx = ai_content.find("```", start_idx + 9)
            if end_idx != -1:
                vulnerable_code = ai_content[start_idx:end_idx + 3]
        
        if vulnerable_code:
            formatted_parts.append("**Vulnerable Code:**")
            formatted_parts.append(vulnerable_code)
            formatted_parts.append("")
        
        # Extract secure code
        secure_code = ""
        secure_start = ai_content.find("Secure Code:")
        if secure_start != -1:
            start_idx = ai_content.find("```python", secure_start)
            if start_idx != -1:
                end_idx = ai_content.find("```", start_idx + 9)
                if end_idx != -1:
                    secure_code = ai_content[start_idx:end_idx + 3]
        
        if secure_code:
            formatted_parts.append("**Secure Code:**")
            formatted_parts.append(secure_code)
            formatted_parts.append("")
        
        # Extract key recommendations
        recommendations = []
        in_recs = False
        for line in ai_content.split('\n'):
            if "Recommendations:" in line:
                in_recs = True
                continue
            elif in_recs and line.strip().startswith('###'):
                break
            elif in_recs and line.strip().startswith('1.') or line.strip().startswith('-'):
                rec = line.strip()
                if rec.startswith('1.'):
                    rec = rec[2:].strip()
                elif rec.startswith('-'):
                    rec = rec[1:].strip()
                if rec and len(rec) > 10:
                    recommendations.append(rec)
        
        if recommendations:
            formatted_parts.append("**Key Fixes:**")
            for i, rec in enumerate(recommendations[:3], 1):  # Limit to 3
                formatted_parts.append(f"{i}. {rec}")
            formatted_parts.append("")
        
        # If no structured content found, provide a simple summary
        if len(formatted_parts) <= 3:
            formatted_parts = []
            formatted_parts.append("## 🔍 AI Security Review")
            formatted_parts.append("")
            formatted_parts.append("The AI has analyzed your code changes and identified potential security considerations.")
            formatted_parts.append("")
            formatted_parts.append("**Recommendation:** Review the changes for security best practices and ensure proper input validation.")
        
        return '\n'.join(formatted_parts)
    
    def create_markdown_summary(self, commit_info: Dict[str, str], diff_content: str, stats: str) -> str:
        """Create a formatted markdown summary."""
        initial_commit_note = ""
        if commit_info.get("is_initial_commit", False):
            initial_commit_note = "\n> **Note:** This appears to be the initial commit in the repository."
        
        summary = f"""# Code Diff Summary

## Commit Information
- **Previous Commit:** `{commit_info['previous_commit'][:8]}`
- **Current Commit:** `{commit_info['current_commit'][:8]}`
- **Author:** {commit_info['author']}
- **Context Lines:** ±{self.context_lines}
- **Timestamp:** {commit_info['timestamp']}{initial_commit_note}

## Commit Messages
- **Previous:** {commit_info['previous_message']}
- **Current:** {commit_info['current_message']}

## Changed Files Statistics
```
{stats}
```

## Detailed Diff
```diff
{diff_content}
```

---
*Generated by Python Diff Generator Script*
"""
        return summary
    
    def create_json_report(self, commit_info: Dict[str, str], diff_content: str, stats: str) -> Dict:
        """Create a JSON report with metadata."""
        # Count lines in diff
        diff_lines = len(diff_content.split('\n'))
        
        # Parse stats to get file count
        stat_lines = stats.strip().split('\n')
        changed_files = len([line for line in stat_lines if '|' in line])
        
        return {
            "metadata": {
                "generator": "Python Diff Generator",
                "version": "1.0.0",
                "timestamp": commit_info['timestamp'],
                "context_lines": self.context_lines,
                "is_initial_commit": commit_info.get("is_initial_commit", False)
            },
            "commits": {
                "previous": {
                    "hash": commit_info['previous_commit'],
                    "short_hash": commit_info['previous_commit'][:8],
                    "message": commit_info['previous_message']
                },
                "current": {
                    "hash": commit_info['current_commit'],
                    "short_hash": commit_info['current_commit'][:8],
                    "message": commit_info['current_message']
                }
            },
            "author": commit_info['author'],
            "statistics": {
                "total_diff_lines": diff_lines,
                "changed_files": changed_files,
                "context_lines": self.context_lines
            },
            "files_stats": stats,
            "diff_content": diff_content
        }
    
    def save_files(self, diff_content: str, markdown_summary: str, json_report: Dict):
        """Save all output files."""
        # Save raw diff
        diff_file = self.output_dir / "code_diff.txt"
        with open(diff_file, 'w', encoding='utf-8') as f:
            f.write(diff_content)
        
        # Save markdown summary
        summary_file = self.output_dir / "diff_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(markdown_summary)
        
        # Save JSON report
        json_file = self.output_dir / "diff_report.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Files saved to: {self.output_dir}")
        print(f"  - {diff_file}")
        print(f"  - {summary_file}")
        print(f"  - {json_file}")
    
    def generate(self) -> Dict:
        """Main method to generate the complete diff analysis."""
        print(f"🔍 Generating diff with ±{self.context_lines} context lines...")
        
        # Get commit information
        commit_info = self.get_commit_info()
        print(f"📝 Previous commit: {commit_info['previous_commit'][:8]}")
        print(f"📝 Current commit: {commit_info['current_commit'][:8]}")
        
        if commit_info.get("is_initial_commit", False):
            print("ℹ️  This appears to be the initial commit - comparing against empty tree")
        
        # Generate diff
        diff_content = self.generate_diff(
            commit_info['previous_commit'], 
            commit_info['current_commit']
        )
        
        # Get file statistics
        stats = self.get_changed_files_stats(
            commit_info['previous_commit'], 
            commit_info['current_commit']
        )
        
        # Create summaries
        markdown_summary = self.create_markdown_summary(commit_info, diff_content, stats)
        json_report = self.create_json_report(commit_info, diff_content, stats)
        
        # Save files
        self.save_files(diff_content, markdown_summary, json_report)
        
        # Call Databricks API for AI review
        ai_review = self.call_databricks_api(diff_content)
        if ai_review:
            # Create PR comment
            pr_comment = self.create_pr_comment(ai_review, diff_content, commit_info)
            
            # Save AI review and comment
            ai_review_file = self.output_dir / "ai_review.json"
            with open(ai_review_file, 'w', encoding='utf-8') as f:
                json.dump(ai_review, f, indent=2, ensure_ascii=False)
            
            pr_comment_file = self.output_dir / "pr_comment.md"
            with open(pr_comment_file, 'w', encoding='utf-8') as f:
                f.write(pr_comment)
            
            print(f"  - {ai_review_file}")
            print(f"  - {pr_comment_file}")
            
            # Add AI review to JSON report
            json_report["ai_review"] = ai_review
            json_report["pr_comment"] = pr_comment
            
            # Update JSON file with AI review
            with open(self.output_dir / "diff_report.json", 'w', encoding='utf-8') as f:
                json.dump(json_report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        diff_lines = len(diff_content.split('\n'))
        print(f"📊 Diff analysis complete!")
        print(f"   Total diff lines: {diff_lines}")
        print(f"   Context lines: ±{self.context_lines}")
        if ai_review:
            print(f"   AI review: ✅ Generated")
        
        return json_report


def main():
    parser = argparse.ArgumentParser(description="Generate code diffs with customizable context")
    parser.add_argument(
        "--context-lines", "-c", 
        type=int, 
        default=10,
        help="Number of context lines (default: 10)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="diff_output",
        help="Output directory (default: diff_output)"
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output only JSON report to stdout"
    )
    
    args = parser.parse_args()
    
    # Validate context lines
    if args.context_lines < 0:
        print("❌ Context lines must be non-negative")
        sys.exit(1)
    
    # Check if we're in a git repository
    if not os.path.exists(".git"):
        print("❌ Not in a git repository")
        sys.exit(1)
    
    # Generate diff
    generator = DiffGenerator(args.context_lines, args.output_dir)
    
    try:
        result = generator.generate()
        
        if args.json_only:
            # Output only JSON to stdout
            print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Error generating diff: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 