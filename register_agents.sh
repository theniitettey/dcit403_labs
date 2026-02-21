#!/bin/bash
#
# Register All DCIT 403 Lab Agents Script
# This script registers all required XMPP accounts for Labs 1-4
#
# Usage: 
#   For Docker: ./register_agents.sh docker
#   For Native: ./register_agents.sh native (requires sudo)
#

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

METHOD=${1:-docker}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}DCIT 403 - Agent Registration Script${NC}"
echo -e "${BLUE}========================================${NC}\n"

if [ "$METHOD" == "docker" ]; then
    echo -e "${YELLOW}Using Docker method...${NC}\n"
    
    # Check if Prosody container is running
    if ! docker ps | grep -q prosody; then
        echo -e "${YELLOW}Prosody container not running. Starting...${NC}"
        docker start prosody 2>/dev/null || {
            echo -e "${YELLOW}Creating new Prosody container...${NC}"
            docker run -d --name prosody \
              -p 5222:5222 \
              -p 5269:5269 \
              -e PROSODY_ADMINS=admin@localhost \
              prosody/prosody:latest
            sleep 3
        }
    fi
    
    CMD_PREFIX="docker exec prosody prosodyctl"
else
    echo -e "${YELLOW}Using native installation method (requires sudo)...${NC}\n"
    CMD_PREFIX="sudo prosodyctl"
fi

echo -e "${GREEN}Registering Lab 1 agents...${NC}"
$CMD_PREFIX register basic_agent localhost 1234 2>/dev/null && \
  echo "  ✓ basic_agent@localhost" || \
  echo "  ✗ basic_agent@localhost (may already exist)"

echo -e "\n${GREEN}Registering Lab 2 agents...${NC}"
$CMD_PREFIX register sensor localhost sensor123 2>/dev/null && \
  echo "  ✓ sensor@localhost" || \
  echo "  ✗ sensor@localhost (may already exist)"

echo -e "\n${GREEN}Registering Lab 3 agents...${NC}"
$CMD_PREFIX register response_agent localhost response123 2>/dev/null && \
  echo "  ✓ response_agent@localhost" || \
  echo "  ✗ response_agent@localhost (may already exist)"

echo -e "\n${GREEN}Registering Lab 4 agents...${NC}"
$CMD_PREFIX register sensor_comm localhost lab4pass 2>/dev/null && \
  echo "  ✓ sensor_comm@localhost" || \
  echo "  ✗ sensor_comm@localhost (may already exist)"

$CMD_PREFIX register response_comm localhost lab4pass 2>/dev/null && \
  echo "  ✓ response_comm@localhost" || \
  echo "  ✗ response_comm@localhost (may already exist)"

$CMD_PREFIX register coordinator_comm localhost lab4pass 2>/dev/null && \
  echo "  ✓ coordinator_comm@localhost" || \
  echo "  ✗ coordinator_comm@localhost (may already exist)"

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}Registration Complete!${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${YELLOW}Listing all registered users:${NC}"
if [ "$METHOD" == "docker" ]; then
    docker exec prosody prosodyctl list localhost
else
    sudo prosodyctl list localhost
fi

echo -e "\n${GREEN}Summary:${NC}"
echo "  Lab 1: basic_agent@localhost (password: 1234)"
echo "  Lab 2: sensor@localhost (password: sensor123)"
echo "  Lab 3: response_agent@localhost (password: response123)"
echo "  Lab 4: sensor_comm@localhost (password: lab4pass)"
echo "         response_comm@localhost (password: lab4pass)"
echo "         coordinator_comm@localhost (password: lab4pass)"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo "  1. Run labs with: python lab2_sensor_agent.py"
echo "  2. Check logs at: logs/"
echo "  3. For issues, verify Prosody is running"
echo ""
