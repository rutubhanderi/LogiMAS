# LogiMAS: Logistics Multi-Agent System

LogiMAS is an intelligent logistics management system powered by specialized AI agents. It automates and optimizes key logistics operations such as route planning, inventory management, and cost optimization using advanced language models and real-time data.

## Project Overview

LogiMAS leverages a multi-agent architecture to streamline logistics workflows:

- **Mobility Agent:** Optimizes delivery routes using live traffic and weather data.
- **Inventory & Supply Agent:** Monitors stock levels, predicts demand, and schedules restocking.
- **Cost Optimization Agent:** Minimizes transportation and handling costs by suggesting efficient delivery strategies.
- **Central Coordinator Agent:** Reads user queries and routes them to the appropriate specialized agent for efficient handling.

## Developed By

- [Rutu Bhanderi](https://github.com/rutubhanderi)
- [Dhairya A Mehra](https://github.com/Dhairya-A-Mehra)
- [Atharv Raje](https://github.com/AtharvRaje33)
- [Devvrat Saini](https://github.com/devvratsaini)

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```sh
   git clone <repository-url>
   cd LogiMAS/agents-logic
   ```
2. **Create a virtual environment:**
   ```sh
   python -m venv venv
   # Activate on Windows (PowerShell):
   .\venv\Scripts\Activate
   # Activate on Git Bash:
   source venv/Scripts/activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Set up environment variables:**
   - Create a `.env` file in the `agents-logic` directory with the following content:
     ```env
     GROQ_API_KEY=your_groq_api_key
     MODEL=your_llm_model
     TEMPERATURE=your_model_temperature
     ```

### Running the Project

1. Navigate to the `agents` directory:
   ```sh
   cd agents
   ```
2. Run the central coordinator agent:
   ```sh
   python central_coordinator_agent.py
   ```

The script will process a set of sample queries and display which specialized agent is selected for each.

---

For any questions or contributions, please contact the developers via their GitHub profiles above.
