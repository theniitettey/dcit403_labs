# DCIT 403 - Designing Intelligent Agent

## Disaster Response & Relief Coordination System

A multi-agent system for coordinating disaster response operations using the SPADE (Smart Python Agent Development Environment) framework.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Laboratory Sessions](#laboratory-sessions)
- [Usage](#usage)
- [Agent Types](#agent-types)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This project implements a decentralized intelligent multi-agent system for disaster response coordination. The system demonstrates:

- **Agent-oriented design principles**
- **Belief-Desire-Intention (BDI) reasoning**
- **Prometheus methodology**
- **FIPA-ACL communication**
- **Distributed decision-making under uncertainty**

### Core Capabilities

- ✅ Disaster event detection
- ✅ Damage severity assessment
- ✅ Rescue task allocation
- ✅ Resource management
- ✅ Multi-agent coordination

---

## 📁 Project Structure

```
dcit403-labs/
├── README.md
├── .gitignore
├── requirements.txt
├── agent_env/                    # Virtual environment (not tracked)
├── lab1_basic_agent.py           # Lab 1: Basic SPADE agent
├── lab2_sensor_agent.py          # Lab 2: SensorAgent with perception
├── lab3_communication.py         # Lab 3: Inter-agent communication
├── lab4_coordination.py          # Lab 4: Multi-agent coordination
├── disaster_events.log           # Generated event logs
├── screenshots/                  # Lab screenshots
│   ├── lab1_screenshot.png
│   └── lab2_screenshot.png
└── reports/                      # Lab reports
    └── DCIT403_Lab1_Lab2_Report.docx
```

---

## 🔧 Prerequisites

### Required Software

- **Python**: 3.9 or higher
- **pip**: Latest version
- **Git**: For version control
- **XMPP Server**: Prosody or access to public XMPP server

### Recommended Tools

- **VS Code** or **PyCharm**: IDE
- **GitHub Codespaces**: Online development environment
- **Draw.io**: For AUML diagrams

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd dcit403-labs
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv agent_env

# Activate virtual environment
source agent_env/bin/activate  # Linux/Mac
# OR
agent_env\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install SPADE and dependencies
pip install spade
```

### 4. Set Up XMPP Account

**Option A: Public Server (Recommended for Testing)**
- Register at: https://xmpp.jp/
- Use credentials in your agent code

**Option B: Local Prosody Server**
```bash
sudo apt-get update
sudo apt-get install prosody

# Create agent account
sudo prosodyctl adduser disaster_agent@localhost
```

---

## 🧪 Laboratory Sessions

### Lab 1: Environment and Agent Platform Setup

**Objective**: Configure Python environment and deploy basic SPADE agent

**Tasks**:
1. Verify Python and SPADE installation
2. Start XMPP server
3. Create and run basic agent
4. Demonstrate agent lifecycle

**Run**:
```bash
python lab1_basic_agent.py
```

**Expected Output**:
- Agent initialization
- Connection to XMPP server
- 5 behavior cycles
- Graceful shutdown

---

### Lab 2: Perception and Environment Modeling

**Objective**: Implement agent perception and disaster event detection

**Tasks**:
1. Create disaster environment simulator
2. Implement SensorAgent
3. Monitor environmental conditions
4. Detect and log disaster events

**Run**:
```bash
python lab2_sensor_agent.py
```

**Expected Output**:
- Environmental monitoring across 4 zones
- Temperature, humidity, visibility readings
- Disaster event detection
- Event logging to `disaster_events.log`

---

### Lab 3: Inter-Agent Communication (Coming Soon)

**Objective**: Implement FIPA-ACL messaging between agents

**Features**:
- Message sending/receiving
- Protocol implementation
- Request-response patterns

---

### Lab 4: Multi-Agent Coordination (Coming Soon)

**Objective**: Coordinate multiple agents for disaster response

**Features**:
- Task allocation
- Resource sharing
- Collaborative decision-making

---

## 💻 Usage

### Basic Agent Example

```python
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

class MyAgent(Agent):
    class MyBehaviour(CyclicBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: Running...")
            await asyncio.sleep(1)
    
    async def setup(self):
        b = self.MyBehaviour()
        self.add_behaviour(b)

# Create and start agent
agent = MyAgent("user@xmpp.jp", "password")
agent.start()
```

### SensorAgent Example

```python
from lab2_sensor_agent import SensorAgent

# Create sensor agent
sensor = SensorAgent("sensor@xmpp.jp", "password")

# Start monitoring
sensor.start()

# Agent will detect disasters and log events
```

---

## 🤖 Agent Types

### 1. SensorAgent
**Responsibility**: Detect disaster events and report environmental conditions

**Capabilities**:
- Multi-zone monitoring
- Temperature/humidity sensing
- Disaster type classification
- Severity assessment (LOW, MEDIUM, HIGH, CRITICAL)

### 2. RescueAgent (Future)
**Responsibility**: Perform rescue operations

**Capabilities**:
- Task execution
- Resource utilization
- Status reporting

### 3. LogisticsAgent (Future)
**Responsibility**: Manage supplies and relief items

**Capabilities**:
- Inventory management
- Resource allocation
- Supply chain coordination

### 4. CoordinatorAgent (Future)
**Responsibility**: Assign tasks and coordinate agents

**Capabilities**:
- Task prioritization
- Agent assignment
- Conflict resolution

---

## 📊 Event Logging

Disaster events are logged to `disaster_events.log` with the following format:

```
TIMESTAMP | ZONE | DISASTER_TYPE | SEVERITY | AFFECTED_POPULATION
2026-01-28 10:30:45 | Zone A | Fire | CRITICAL | 423
2026-01-28 10:35:12 | Zone C | Earthquake | HIGH | 346
```

---

## 🔍 Testing

### Run All Tests
```bash
# Activate virtual environment first
source agent_env/bin/activate

# Run Lab 1
python lab1_basic_agent.py

# Run Lab 2
python lab2_sensor_agent.py

# Check logs
cat disaster_events.log
```

### Verify Installation
```bash
python -c "import spade; print('SPADE version:', spade.__version__)"
```

---

## 🛠️ Troubleshooting

### SPADE Installation Issues
```bash
# Try upgrading pip first
pip install --upgrade pip

# Install with verbose output
pip install -v spade
```

### XMPP Connection Failed
- Check your internet connection
- Verify XMPP credentials
- Try alternative server (xmpp.jp, jabber.org)
- Check firewall settings

### Virtual Environment Issues
```bash
# Delete and recreate
rm -rf agent_env
python3 -m venv agent_env
source agent_env/bin/activate
pip install spade
```

---

## 📚 Resources

### Documentation
- [SPADE Documentation](https://spade-mas.readthedocs.io/)
- [FIPA Standards](http://www.fipa.org/repository/standardspecs.html)
- [Prometheus Methodology](http://www.cs.rmit.edu.au/agents/prometheus/)

### Tutorials
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [XMPP Protocol](https://xmpp.org/about/technology-overview/)
- [Multi-Agent Systems](https://en.wikipedia.org/wiki/Multi-agent_system)

---

## 🤝 Contributing

This is an educational project for DCIT 403. Contributions are welcome!

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/lab3`)
3. Commit changes (`git commit -m 'Add Lab 3 implementation'`)
4. Push to branch (`git push origin feature/lab3`)
5. Open Pull Request

---

## 📝 License

This project is part of the DCIT 403 course curriculum.

---

## 👥 Authors

- **Course**: DCIT 403 - Designing Intelligent Agent
- **Institution**: University of Ghana
- **Instructor**: Dr. PBS

---

## 📧 Contact

For questions or support:
- **Email**: [mptettey@st.ug.edu.gh]

---

## 🎓 Acknowledgments

- Anthropic's Claude for development assistance
- SPADE development team
- Course instructors and teaching assistants
- Fellow students and collaborators

---

## 📅 Version History

- **v0.2.0** (2026-01-28): Lab 2 - SensorAgent implementation
- **v0.1.0** (2026-01-28): Lab 1 - Basic agent setup
- **v0.0.1** (2026-01-27): Initial project structure

---

**Last Updated**: January 28, 2026