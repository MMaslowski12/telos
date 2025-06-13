# Telos

A Python-based project for LLM-based automation of CFD optimization of plane-like drones. (drop airfoils, get optimized aircraft for the specific requirements). I am building this for my aeroengineering friends, hoping to speed up their design cycles so that we can all have more cool hardware stuff (personally, I find it reprehensible that my hardware friends are blocked by the low-level BS in old software instead of having JARVIS-style support. They should be the cool kids building stuff from garages, just like I can write software with a laptop)

I am building on top of https://github.com/nikhil-sethi/xflrpy, a python-friendly version of XFLR5

# Current Stage

The project is currently in early stages of development. So far, it is possible to connect to XFLR5 and 
converse with an AI bot that can call basic tools in XFLR5 ("Change the chord of the midsection of this airplane to 2 meters"). See an example below:

# TODO

SHORT TERM: (~mid June 2025)
- Add the ability to calculate lift and drag at constant velocities
- Create the LLM that can execute single commands: "Make the lift-drag positive in this aircraft at 8ms-2"

LONG TERM: (~end of June/July 2025)
- Specialize the LLM in aerodynamics using notes from meetings with my aeroengineering friends
- Step up the autonomous model: "Using these airfoils for wings, elevators, and fins, construct an airplane that could carry a 2kg payload with maximum range / an airplane that can carry the highest payload" 

BACKLOG:
- Add visualization tools (make the LLM "see" the aircraft as it designs it)
- Add the capability of the model to choose its own airfoils (instead of scraping it from the NASA database as my friends already do it)

## Overview

This project provides tools for aerodynamic analysis and optimization of aircraft designs using XFLR5/XFLRpy. It includes functionality for:
- Setting up and managing airplane configurations
- Running aerodynamic analyses
- Interactive chat-based optimization
- Various aerodynamic tools and utilities

## Prerequisites

- Python 3.x
- XFLR5/XFLRpy 0.48
- OpenAI API access

## Installation

1. Clone the repository:
```bash
git clone https://github.com/MMaslowski12/telos.git
cd Telos
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Install XFLR5/XFLRpy:

### macOS
For macOS users, XFLRpy is already built, run it with:
xflrpy/xflrpy.app/Contents/MacOS/xflrpy

You should run xflrpy (the modified xflr5) in one terminal, and main.py in the other

### Linux and Windows
For Linux and Windows users, you'll need to build XFLRpy from source. For further details, look at the original xflrpy repo

4. Add your Deepseek API key to .env (or any other model, but make sure to change the URL in the openAI client)

## Project Structure

- `main.py` - Main entry point and project configuration
- `delphi.py` - Chat loop implementation for interactive optimization
- `tools.py` - Core aerodynamic tools and analysis functions
- `utils.py` - Utility functions
- `smietnik.py` - Additional utilities and helper functions. feel free to ignore

## Usage

Run the main script:
```bash
python main.py
```

The program will:
1. Set up a new airplane configuration
2. Initialize the analysis environment
3. Start an interactive chat loop for optimization

## License

This project is licensed under the GNU General Public License v3.0 - see the [License.txt](License.txt) file for details.

This project is built on top of [XFLRpy](https://github.com/nikhil-sethi/xflrpy), which is also licensed under the GNU General Public License v3.0.

## Contributing

Feel free to submit issues and enhancement requests! 