"""
Performance-optimized heat packet model using numpy arrays instead of individual objects.
"""

from typing import List, Tuple, Optional
import numpy as np
from .config import SimulationConfig
from .grid import Grid
from .rng import RandomNumberGenerator


class OptimizedPacketManager:
    """High-performance packet manager using numpy arrays."""
    
    def __init__(self, max_packets: int = 100000):
        """Initialize with pre-allocated arrays for performance."""
        self.max_packets = max_packets
        
        # Pre-allocate arrays
        self.positions_x = np.full(max_packets, -1, dtype=np.int32)
        self.positions_y = np.full(max_packets, -1, dtype=np.int32)
        self.active_mask = np.zeros(max_packets, dtype=bool)
        
        self.n_active = 0
        self.next_slot = 0
    
    def add_packets(self, positions: List[Tuple[int, int]]) -> int:
        """Add multiple packets at once for better performance."""
        n_to_add = len(positions)
        
        if self.n_active + n_to_add > self.max_packets:
            # Compact arrays if needed
            self._compact_arrays()
            
            if self.n_active + n_to_add > self.max_packets:
                # Still too many - add what we can
                n_to_add = self.max_packets - self.n_active
                positions = positions[:n_to_add]
        
        # Find available slots
        available_slots = np.where(~self.active_mask)[0][:n_to_add]
        
        # Add packets
        for i, (x, y) in enumerate(positions):
            slot = available_slots[i]
            self.positions_x[slot] = x
            self.positions_y[slot] = y
            self.active_mask[slot] = True
        
        self.n_active += n_to_add
        return n_to_add
    
    def add_packet(self, x: int, y: int) -> bool:
        """Add single packet (less efficient than batch add)."""
        return self.add_packets([(x, y)]) == 1
    
    def move_packets(self, move_mask: np.ndarray, new_x: np.ndarray, new_y: np.ndarray):
        """Move packets based on boolean mask and new positions."""
        active_indices = np.where(self.active_mask)[0]
        move_indices = active_indices[move_mask]
        
        self.positions_x[move_indices] = new_x[move_mask]
        self.positions_y[move_indices] = new_y[move_mask]
    
    def remove_packets(self, remove_mask: np.ndarray):
        """Remove packets based on boolean mask."""
        active_indices = np.where(self.active_mask)[0]
        remove_indices = active_indices[remove_mask]
        
        self.active_mask[remove_indices] = False
        self.n_active -= len(remove_indices)
        
        return len(remove_indices)
    
    def get_active_positions(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get positions of all active packets as numpy arrays."""
        active_indices = np.where(self.active_mask)[0]
        return self.positions_x[active_indices], self.positions_y[active_indices]
    
    def get_active_positions_list(self) -> List[Tuple[int, int]]:
        """Get active positions as list of tuples (for compatibility)."""
        x_pos, y_pos = self.get_active_positions()
        return list(zip(x_pos, y_pos))
    
    def count_active(self) -> int:
        """Count number of active packets."""
        return self.n_active
    
    def clear_all(self):
        """Remove all packets."""
        self.active_mask.fill(False)
        self.n_active = 0
        self.next_slot = 0
    
    def _compact_arrays(self):
        """Compact arrays by moving active packets to beginning."""
        active_indices = np.where(self.active_mask)[0]
        
        if len(active_indices) == 0:
            self.clear_all()
            return
        
        # Move active packets to beginning of arrays
        self.positions_x[:len(active_indices)] = self.positions_x[active_indices]
        self.positions_y[:len(active_indices)] = self.positions_y[active_indices]
        
        # Update active mask
        self.active_mask.fill(False)
        self.active_mask[:len(active_indices)] = True
        
        self.n_active = len(active_indices)
        self.next_slot = len(active_indices)


class OptimizedHeatSink:
    """Performance-optimized heat sink using numpy arrays."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.grid = Grid(config)
        
        # Use optimized packet manager
        max_packets = max(50000, config.N_packets * 10)  # Allow for growth
        self.packet_manager = OptimizedPacketManager(max_packets)
        
        # Pre-allocate arrays for random walk
        self._temp_arrays_allocated = False
        
        # Statistics tracking
        self.total_packets_injected = 0
        self.total_packets_removed = 0
    
    def _allocate_temp_arrays(self, size: int):
        """Allocate temporary arrays for vectorized operations."""
        self._move_decisions = np.zeros(size, dtype=bool)
        self._direction_choices = np.zeros(size, dtype=np.int32)
        self._new_x = np.zeros(size, dtype=np.int32)
        self._new_y = np.zeros(size, dtype=np.int32)
        self._boundary_hits = np.zeros(size, dtype=bool)
        self._temp_arrays_allocated = True
    
    def inject_heat_packets(self, rng: RandomNumberGenerator) -> int:
        """Inject new heat packets into hot-spot region."""
        packets_to_inject = self.config.Q
        
        # Generate all positions at once
        positions = []
        for _ in range(packets_to_inject):
            x, y = self.grid.get_random_hotspot_position(rng)
            positions.append((x, y))
        
        # Add packets in batch
        injected_count = self.packet_manager.add_packets(positions)
        self.total_packets_injected += injected_count
        
        return injected_count
    
    def move_packets(self, rng: RandomNumberGenerator) -> int:
        """Vectorized random walk update for all active packets."""
        n_active = self.packet_manager.count_active()
        
        if n_active == 0:
            return 0
        
        # Allocate temporary arrays if needed
        if not self._temp_arrays_allocated or len(self._move_decisions) < n_active:
            self._allocate_temp_arrays(max(n_active, 10000))
        
        # Get current positions
        current_x, current_y = self.packet_manager.get_active_positions()
        
        # Vectorized move decisions
        move_probs = np.array([rng.random() for _ in range(n_active)])
        move_mask = move_probs < self.config.move_probability
        n_moving = np.sum(move_mask)
        
        if n_moving == 0:
            return 0
        
        # Vectorized direction choices for moving packets
        direction_indices = np.array([rng.randint(0, 4) for _ in range(n_moving)])
        
        # Calculate new positions
        directions = np.array([(0, 1), (0, -1), (1, 0), (-1, 0)])
        dx = directions[direction_indices, 0]
        dy = directions[direction_indices, 1]
        
        new_x_moving = current_x[move_mask] + dx
        new_y_moving = current_y[move_mask] + dy
        
        # Check boundary conditions
        boundary_hits = ((new_x_moving < 0) | (new_x_moving >= self.grid.Nx) |
                        (new_y_moving < 0) | (new_y_moving >= self.grid.Ny))
        
        packets_removed = 0
        
        if self.config.boundary_type == "absorbing":
            # Remove packets that hit boundaries
            packets_removed = np.sum(boundary_hits)
            
            # Create removal mask for all active packets
            remove_mask_all = np.zeros(n_active, dtype=bool)
            remove_mask_all[move_mask] = boundary_hits
            
            # Remove boundary-hitting packets
            if packets_removed > 0:
                self.packet_manager.remove_packets(remove_mask_all)
            
            # Move remaining packets
            valid_moves = move_mask.copy()
            valid_moves[move_mask] &= ~boundary_hits
            
            if np.any(valid_moves):
                # Update positions for valid moves
                new_x_all = current_x.copy()
                new_y_all = current_y.copy()
                
                valid_moving_mask = ~boundary_hits
                new_x_all[move_mask] = np.where(valid_moving_mask, new_x_moving, current_x[move_mask])
                new_y_all[move_mask] = np.where(valid_moving_mask, new_y_moving, current_y[move_mask])
                
                self.packet_manager.move_packets(valid_moves, new_x_all, new_y_all)
        
        elif self.config.boundary_type == "reflecting":
            # Keep packets at current position if they would hit boundary
            new_x_all = current_x.copy()
            new_y_all = current_y.copy()
            
            # Only update positions for valid moves
            valid_moves = ~boundary_hits
            new_x_all[move_mask] = np.where(valid_moves, new_x_moving, current_x[move_mask])
            new_y_all[move_mask] = np.where(valid_moves, new_y_moving, current_y[move_mask])
            
            self.packet_manager.move_packets(move_mask, new_x_all, new_y_all)
        
        self.total_packets_removed += packets_removed
        return packets_removed
    
    def update_temperature_field(self):
        """Update temperature field based on current packet positions."""
        positions = self.packet_manager.get_active_positions_list()
        self.grid.update_temperature_field(positions)
    
    def get_observables(self) -> dict:
        """Get current observable quantities."""
        self.update_temperature_field()
        
        return {
            'active_packets': self.packet_manager.count_active(),
            'hotspot_temperature': self.grid.get_hotspot_temperature(),
            'temperature_stats': self.grid.get_temperature_statistics(),
            'total_injected': self.total_packets_injected,
            'total_removed': self.total_packets_removed
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
    
    def get_statistics_summary(self) -> dict:
        """Get summary of simulation statistics."""
        return {
            'config': self.config.to_dict(),
            'packets': {
                'active': self.packet_manager.count_active(),
                'total_injected': self.total_packets_injected,
                'total_removed': self.total_packets_removed,
                'net_packets': self.total_packets_injected - self.total_packets_removed,
                'max_capacity': self.packet_manager.max_packets
            },
            'grid': {
                'size': (self.config.Nx, self.config.Ny),
                'physical_size': (self.config.Lx, self.config.Ly),
                'hotspot_cells': np.sum(self.grid.hotspot_mask)
            }
        }