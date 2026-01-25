"""
Heat packet model and heat sink representation.
"""

from typing import List, Tuple, Optional
import numpy as np

try:
    from .config import SimulationConfig
    from .grid import Grid
    from .rng import RandomNumberGenerator
except ImportError:
    # Fallback for direct execution
    from config import SimulationConfig
    from grid import Grid
    from rng import RandomNumberGenerator


class HeatPacket:
    """Represents a single heat packet in the simulation."""
    
    def __init__(self, x: int, y: int, packet_id: Optional[int] = None):
        self.x = x
        self.y = y
        self.active = True
        self.id = packet_id
        self.birth_time = 0
        self.steps_taken = 0
    
    def move_to(self, new_x: int, new_y: int):
        """Move packet to new position."""
        self.x = new_x
        self.y = new_y
        self.steps_taken += 1
    
    def deactivate(self):
        """Deactivate packet (e.g., when it hits boundary)."""
        self.active = False
    
    def get_position(self) -> Tuple[int, int]:
        """Get current position as tuple."""
        return (self.x, self.y)
    
    def __repr__(self) -> str:
        status = "active" if self.active else "inactive"
        return f"HeatPacket(id={self.id}, pos=({self.x},{self.y}), {status})"


class PacketManager:
    """Manages collection of heat packets."""
    
    def __init__(self):
        self.packets: List[HeatPacket] = []
        self._next_id = 0
    
    def add_packet(self, x: int, y: int) -> HeatPacket:
        """Add new heat packet at specified position."""
        packet = HeatPacket(x, y, self._next_id)
        self.packets.append(packet)
        self._next_id += 1
        return packet
    
    def remove_inactive_packets(self):
        """Remove all inactive packets from collection."""
        self.packets = [p for p in self.packets if p.active]
    
    def get_active_packets(self) -> List[HeatPacket]:
        """Get list of all active packets."""
        return [p for p in self.packets if p.active]
    
    def get_active_positions(self) -> List[Tuple[int, int]]:
        """Get positions of all active packets."""
        return [p.get_position() for p in self.packets if p.active]
    
    def count_active(self) -> int:
        """Count number of active packets."""
        return sum(1 for p in self.packets if p.active)
    
    def clear_all(self):
        """Remove all packets."""
        self.packets.clear()
        self._next_id = 0


class HeatSink:
    """Represents the heat sink with its physical properties and behavior."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.grid = Grid(config)
        self.packet_manager = PacketManager()
        
        # Statistics tracking
        self.total_packets_injected = 0
        self.total_packets_removed = 0
        self.total_packets_convected = 0  # Track convection removals separately
    
    def inject_heat_packets(self, rng: RandomNumberGenerator) -> int:
        """Inject new heat packets into hot-spot region."""
        packets_to_inject = self.config.Q  # Q is now integer
        injected_count = 0
        
        for _ in range(packets_to_inject):
            x, y = self.grid.get_random_hotspot_position(rng)
            self.packet_manager.add_packet(x, y)
            injected_count += 1
        
        self.total_packets_injected += injected_count
        return injected_count
    
    def move_packets(self, rng: RandomNumberGenerator) -> int:
        """Perform random walk update for all active packets with convection cooling."""
        packets_removed = 0
        packets_convected = 0
        
        for packet in self.packet_manager.get_active_packets():
            # --- NEW CODE START ---
            # Convection Check: Does the packet escape to the air?
            if rng.random() < self.config.convection_prob:
                # Packet is removed (heat lost to air).
                packet.deactivate()
                packets_convected += 1
                continue  # Break the 'while' loop to move to the next packet.
            # --- NEW CODE END ---
            
            # ... (Existing code for moving the packet) ...
            # Check if packet should move based on move probability
            if rng.random() < self.config.move_probability:
                # Choose random direction
                direction = rng.choice(self.grid.neighbor_directions)
                new_x = packet.x + direction[0]
                new_y = packet.y + direction[1]
                
                # Apply boundary conditions
                if self._apply_boundary_condition(packet, new_x, new_y):
                    packets_removed += 1
                else:
                    packet.move_to(new_x, new_y)
        
        # Clean up inactive packets
        self.packet_manager.remove_inactive_packets()
        self.total_packets_removed += packets_removed
        self.total_packets_convected += packets_convected
        
        return packets_removed + packets_convected
    
    def _apply_boundary_condition(self, packet: HeatPacket, new_x: int, new_y: int) -> bool:
        """Apply boundary condition. Returns True if packet was removed."""
        if not self.grid.is_valid_position(new_x, new_y):
            if self.config.boundary_type == "absorbing":
                # Remove packet (absorbing boundary)
                packet.deactivate()
                return True
            elif self.config.boundary_type == "reflecting":
                # Keep packet at current position (reflecting boundary)
                return False
        return False
    
    def update_temperature_field(self):
        """Update temperature field based on current packet positions."""
        positions = self.packet_manager.get_active_positions()
        self.grid.update_temperature_field(positions)
    
    def get_observables(self) -> dict:
        """Get current observable quantities."""
        self.update_temperature_field()
        
        return {
            'active_packets': self.packet_manager.count_active(),
            'hotspot_temperature': self.grid.get_hotspot_temperature(),
            'temperature_stats': self.grid.get_temperature_statistics(),
            'total_injected': self.total_packets_injected,
            'total_removed': self.total_packets_removed,
            'total_convected': self.total_packets_convected
        }
    
    def get_temperature_field(self) -> np.ndarray:
        """Get current temperature field."""
        return self.grid.temperature_field.copy()
    
    def reset(self):
        """Reset heat sink to initial state."""
        self.packet_manager.clear_all()
        self.grid.reset()
        self.total_packets_injected = 0
        self.total_packets_removed = 0
        self.total_packets_convected = 0
    
    def get_statistics_summary(self) -> dict:
        """Get summary of simulation statistics."""
        return {
            'config': self.config.to_dict(),
            'packets': {
                'active': self.packet_manager.count_active(),
                'total_injected': self.total_packets_injected,
                'total_removed': self.total_packets_removed,
                'total_convected': self.total_packets_convected,
                'net_packets': self.total_packets_injected - self.total_packets_removed - self.total_packets_convected
            },
            'grid': {
                'size': (self.config.Nx, self.config.Ny),
                'physical_size': (self.config.Lx, self.config.Ly),
                'hotspot_cells': np.sum(self.grid.hotspot_mask)
            }
        }