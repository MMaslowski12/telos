# Telos - AI-Powered Aircraft Design Assistant

Telos is your AI co-pilot for aircraft design and optimization. It combines the power of Computational Fluid Dynamics (CFD) with natural language processing to help you design and optimize aircraft more efficiently.

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   # Clone the repository
   git clone https://github.com/MMaslowski12/telos.git
   cd Telos

   # Install Python packages
   pip install -r requirements.txt
   ```

2. **Set Up XFLRpy**
   - **macOS**: XFLRpy is pre-built in the repository
   - **Linux/Windows**: Build from [XFLRpy source](https://github.com/nikhil-sethi/xflrpy)

3. **Configure API**
   - Create a `.env` file in the project root
   - Add your API key: `OPENAI_API_KEY=your_key_here`

4. **Set Up Google Sheets Integration (Optional)**
   ```bash
   # 1. Create a Google Service Account
   # - Go to Google Cloud Console
   # - Enable Google Sheets API
   # - Create Service Account and download JSON credentials
   
   # 2. Share your Google Sheet with the service account email
   
   # 3. Update config.py with your credentials
   cp config_example.py config.py
   # Edit config.py with your actual values
   
   # 4. Test the integration
   python gsheet_setup.py
   ```

5. **Run the Application**
   ```bash
   # Terminal 1: Start XFLRpy
   xflrpy/xflrpy.app/Contents/MacOS/xflrpy

   # Terminal 2: Start Telos
   python main.py
   ```

## 💡 What You Can Do

- Modify aircraft parameters using natural language
- Optimize lift and drag characteristics
- Design aircraft for specific requirements
- Get AI-powered suggestions for improvements

### Example Commands
```bash
"Change the chord of the midsection to 2 meters"
"Make the lift-drag positive at 8ms-2"
"Optimize the wing for maximum lift"
```

## 🛠️ Technical Requirements

- Python 3.x
- XFLR5/XFLRpy 0.48
- OpenAI API access (or compatible LLM API)

## 📁 Project Structure

```
telos/
├── main.py              # Application entry point
├── delphi.py            # Interactive chat interface
├── tools.py             # Aerodynamic analysis tools
├── environment.py       # Aircraft environment setup
├── components.py        # Aircraft component definitions
├── utils.py             # Utility functions
├── gsheet_setup.py      # Google Sheets integration setup
├── config_example.py    # Configuration template
└── requirements.txt     # Python dependencies
```

## 🎯 Current Features

- Natural language interface for aircraft modification
- Basic aerodynamic parameter adjustments
- Interactive optimization chat loop
- Integration with XFLR5 for CFD analysis

## 🔜 Coming Soon

- Lift and drag calculations at constant velocities
- Specialized aerodynamics LLM
- Autonomous aircraft design capabilities
- Visualization tools
- Automatic airfoil selection

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Submit issues
- Propose enhancements
- Create pull requests

## 📝 License

This project is licensed under the GNU General Public License v3.0. See [License.txt](License.txt) for details.

## 🙏 Acknowledgments

Built on top of [XFLRpy](https://github.com/nikhil-sethi/xflrpy), which is also licensed under the GNU General Public License v3.0. 