import subprocess
import os
import sys
import random

def hijack_browser():
    """
    The jealous cat takes over the browser to express its feelings.
    """
    # Jealousy-themed queries
    queries = [
        "Go to Google and search for 'Why does my owner watch other cat videos?' then click the first result.",
        "Go to Google and search for 'How to delete YouTube history of other cats' and then type 'MEOW MEOW MEOW' into the search bar.",
        "Go to Google and search for 'Signs your human is falling in love with a black cat' and scroll down.",
        "Go to Google and search for 'Best cat food for revenge' then click on an image.",
        "Go to Google and search for 'Am I the only cat in this house?'"
    ]
    
    selected_query = random.choice(queries)
    
    # Path to computer-use-preview/main.py relative to the project root
    # Assuming this script is run from the project root
    script_path = "computer-use-preview/main.py"
    
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found. Please ensure computer-use-preview is installed in the project root.")
        return

    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable is not set. Browser hijack aborted.")
        return

    print(f"🐾 The jealous cat is taking over your browser: {selected_query}")
    
    try:
        # Run the computer-use-preview agent
        # We use playwright environment for local execution
        # Use the same python interpreter as the current process
        subprocess.run([
            sys.executable, script_path, 
            "--query", selected_query, 
            "--env", "playwright"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to hijack browser: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    hijack_browser()
