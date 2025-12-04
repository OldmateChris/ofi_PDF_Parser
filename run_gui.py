import sys
from pathlib import Path

# Add the current directory to Python's path so it finds 'ParsingTool'
sys.path.append(str(Path(__file__).parent))

# Import using the full package name
from ParsingTool.parsing.gui import run_gui

if __name__ == "__main__":
    run_gui()