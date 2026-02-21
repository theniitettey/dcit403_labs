"""
LAB 2: Perception and Environment Modelling

This module containes a simulated disaster environment, with various disaster scenarios and environmental conditions. The environment is designed to test the perception and environment modelling capabilities of autonomous agents in a disaster response context.
"""

import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional

class DisasterType(Enum):
    """
    Types of disasters that can occur in the environment
    """

    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    FIRE = "fire"
    DROUGHT = "drought"
    STORM = "storm"
    HURRICANE = "hurricane"


class Severity(Enum):
        """
        Severity levels for disasters
        """

        LOW = 1
        MODERATE = 2
        HIGH = 3
        CRITICAL = 4
        SEVERE = 5

@dataclass
class Location:
    """
    Represents a location in the environment
    """

    latitude: float
    longitude: float
    name: Optional[str] = None

    def __str__(self):
        return f"{self.name} ({self.latitude:.4f}, {self.longitude:.4f})" if self.name else f"({self.latitude:.4f}, {self.longitude:.4f})"
    
@dataclass
class DisasterEvent:
    """
    Represents a disaster event in the environment
    """
    event_id: str
    disaster_type: DisasterType
    location: Location
    severity: Severity
    timestamp: datetime
    affected_area: float
    casualties: int
    infrastructure_damage: float
    resources_needed: Dict[str, int]

    def __str__(self):
        return f"DisasterEvent(id={self.event_id}, type={self.disaster_type.value}, location={self.location}, severity={self.severity.name}, timestamp={self.timestamp.isoformat()}, affected_area={self.affected_area} sq km, casualties={self.casualties}, infrastructure_damage={self.infrastructure_damage}%, resources_needed={self.resources_needed})"


@dataclass
class EnvironmentPercept:
    """
    Represents the percept of the environment for an autonomous agent
    """

    timestamp: datetime
    location: Location
    temperature: float
    humidity: float
    wind_speed: float
    air_quality: float
    seismic_activity: float
    water_level: float
    smoke_detected: bool
    active_disasters: List[DisasterEvent]

    def __str__(self):
        return f"EnvironmentPercept(timestamp={self.timestamp.isoformat()}, location={self.location}, temperature={self.temperature}°C, humidity={self.humidity}%, wind_speed={self.wind_speed} km/h, air_quality={self.air_quality} AQI, seismic_activity={self.seismic_activity} Richter, water_level={self.water_level} m, smoke_detected={self.smoke_detected}, active_disasters=[{', '.join(str(d) for d in self.active_disasters)}])"
    
class DisasterEnvironment:
    """
    Simulated disaster environment for testing autonomous agents
    """

    def __init__(self):
        self.event_counter = 0
        self.active_disasters: List[DisasterEvent] = []
        self.locations: List[Location] = self.initialize_locations()
        self.current_conditions: Dict[str, float] = self.initialize_conditions()

    def initialize_locations(self) -> List[Location]:
        """
        Initialize locations to monitor
        """
        return [
            Location(34.0522, -118.2437, "Accra"),
            Location(40.7128, -74.0060, "Kumasi"),
            Location(41.8781, -87.6298, "Ada"),
            Location(29.7604, -95.3698, "Cape Coast"),
            Location(33.4484, -112.0740, "Tarkwa"),
        ]
    
    def initialize_conditions(self) -> Dict[str, float]:
        """
        Initialize the environmental conditions with random values
        """
        conditions = {}

        for location in self.locations:
            conditions[location.name] = {
                'temperature': random.uniform(25, 35),
                'humidity': random.uniform(60, 90),
                'wind_speed': random.uniform(0, 30),
                'air_quality': random.uniform(50, 150),
                'seismic_activity': 0.0,
                'water_level': 0.0,
                'smoke_detected': False,
            }

        return conditions
    
    def update_environment(self):
        """
        Update enviroment and maybe generate new disasters
        """

        for location_name in self.current_conditions:
            condition = self.current_conditions[location_name]
            condition["temperature"] += random.uniform(-2, 2)
            condition["humidity"] += random.uniform(-5, 5)
            condition['wind_speed'] = max(0, condition['wind_speed'] + random.uniform(-5, 5))
            condition['air_quality'] += random.uniform(-10, 10)

            # Adjust new values to realistic ranges
            condition["temperature"] = max(20, min(45, condition["temperature"]))
            condition["humidity"] = max(30, min(100, condition["humidity"]))
            condition["air_quality"] = max(0, min(500, condition["air_quality"]))

    
        # Randomly generate new disasters
        if random.random() < 0.80:
            self._generate_disaster()

        
        # Updte existing disasters
        self._update_disasters()

    
    def _generate_disaster(self):
        """
        Generate a new randown disaster
        """

        self.event_counter += 1

        disaster_type = random.choice(list(DisasterType))
        location = random.choice(self.locations)
        severity = random.choice(list(Severity))

        # Update conditons based on disaster type
        cond = self.current_conditions[location.name]

        if disaster_type == DisasterType.FLOOD:
            cond['water_level'] += random.uniform(1, 5)
            cond['humidity'] = min(100, cond["humidity"] + random.uniform(10, 20))
        elif disaster_type == DisasterType.EARTHQUAKE:
            cond['seismic_activity'] += random.uniform(4, 8)
        elif disaster_type == DisasterType.FIRE:
            cond['smoke_detected'] = True
            cond['air_quality'] += random.uniform(50, 100)
            cond['temperature'] += random.uniform(10, 30)
        elif disaster_type == DisasterType.STORM:
            cond['wind_speed'] += random.uniform(20, 50)
            cond['humidity'] = min(100, cond["humidity"] + random.uniform(10, 20))
        elif disaster_type == DisasterType.HURRICANE:
            cond['wind_speed'] += random.uniform(50, 100)
            cond['humidity'] = min(100, cond["humidity"] + random.uniform(20, 40))
            cond['water_level'] += random.uniform(2, 6)
        elif disaster_type == DisasterType.DROUGHT:
            cond['humidity'] = max(0, cond["humidity"] - random.uniform(20, 40))
            cond['temperature'] += random.uniform(5, 15)
        
        # Generate disaster event
        disaster_event = DisasterEvent(
            event_id=f"EVT{self.event_counter:04d}",
            disaster_type=disaster_type,
            location=location,
            severity=severity,
            timestamp=datetime.now(),
            affected_area=random.uniform(10, 1000),
            casualties=random.randint(0, 100),
            infrastructure_damage=random.uniform(0, 100),
            resources_needed={
                "medical_kits": random.randint(0, 50),
                "food_supplies": random.randint(0, 100),
                "water": random.randint(0, 200),
                "shelter_materials": random.randint(0, 50),
                "rescue_teams": random.randint(0, 20),
            }
        )

        self.active_disasters.append(disaster_event)
        return disaster_event
    
    def _update_disasters(self):
        """
        Update existing disasters, maybe resolve some
        """
        disasters_to_remove = []

        for disaster in self.active_disasters:
            # Randomly resolve some disasters
            if random.random() < 0.30:
                disasters_to_remove.append(disaster)
            
            # reset conditions if disaster is resolved
            cond = self.current_conditions[disaster.location.name]
            if disaster.disaster_type == DisasterType.FLOOD:
                cond['water_level'] = max(0, cond['water_level'] - random.uniform(1, 5))
                cond['humidity'] = max(30, cond["humidity"] - random.uniform(10, 20))
            elif disaster.disaster_type == DisasterType.EARTHQUAKE:
                cond['seismic_activity'] = max(0, cond['seismic_activity'] - random.uniform(4, 8))
            elif disaster.disaster_type == DisasterType.FIRE:
                cond['smoke_detected'] = False
                cond['air_quality'] = max(0, cond['air_quality'] - random.uniform(50, 100))
                cond['temperature'] = max(20, cond['temperature'] - random.uniform(10, 30))
            elif disaster.disaster_type == DisasterType.STORM:
                cond['wind_speed'] = max(0, cond['wind_speed'] - random.uniform(20, 50))
                cond['humidity'] = max(30, cond["humidity"] - random.uniform(10, 20))
            elif disaster.disaster_type == DisasterType.HURRICANE:
                cond['wind_speed'] = max(0, cond['wind_speed'] - random.uniform(50, 100))
                cond['humidity'] = max(30, cond["humidity"] - random.uniform(20, 40))
                cond['water_level'] = max(0, cond['water_level'] - random.uniform(2, 6))
            elif disaster.disaster_type == DisasterType.DROUGHT:
                cond['humidity'] = min(100, cond["humidity"] + random.uniform(20, 40))
                cond['temperature'] = max(20, cond['temperature'] - random.uniform(5, 15))
        
        for disaster in disasters_to_remove:
            self.active_disasters.remove(disaster)  
    
    def sense(self, location: Location) -> EnvironmentPercept:
        """
        Simulate sensing the environment at a given location
        """
        cond = self.current_conditions[location.name]
        local_disasters = [d for d in self.active_disasters if d.location == location]

        percept = EnvironmentPercept(
            timestamp=datetime.now(),
            location=location,
            temperature=cond['temperature'],
            humidity=cond['humidity'],
            wind_speed=cond['wind_speed'],
            air_quality=cond['air_quality'],
            seismic_activity=cond['seismic_activity'],
            water_level=cond['water_level'],
            smoke_detected=cond['smoke_detected'],
            active_disasters=local_disasters
        )

        return percept
    
    def get_all_percepts(self) -> List[EnvironmentPercept]:
        """
        Get percepts for all monitored locations
        """
        percepts = []
        for location in self.locations:
            percepts.append(self.sense(location))
        return percepts
    
    def get_summary(self) -> str:
        """Get a summary of the current environment state."""
        summary = "\n" + "="*70 + "\n"
        summary += "ENVIRONMENT STATUS SUMMARY\n"
        summary += "="*70 + "\n"
        summary += f"Active Disasters: {len(self.active_disasters)}\n"
        summary += f"Monitored Locations: {len(self.locations)}\n"
        summary += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += "="*70 + "\n\n"
        
        if self.active_disasters:
            summary += "ACTIVE DISASTERS:\n"
            summary += "-"*70 + "\n"
            for disaster in self.active_disasters:
                summary += f"{disaster}\n"
                summary += f"  Casualties: {disaster.casualties}, "
                summary += f"Damage: {disaster.infrastructure_damage:.1f}%, "
                summary += f"Area: {disaster.affected_area:.1f} km²\n"
            summary += "-"*70 + "\n"
        else:
            summary += "No active disasters - All locations clear\n"
            summary += "-"*70 + "\n"
        
        return summary


