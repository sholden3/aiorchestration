"""
@fileoverview Port Discovery System
@author Dr. Sarah Chen - Backend/Systems Architect
@description Automatic port discovery and management for backend services
"""

import socket
import psutil
import logging
from typing import Optional, List, Tuple
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class PortDiscovery:
    """
    Intelligent port discovery system that finds available ports
    and manages port allocation for services
    """
    
    def __init__(self, 
                 preferred_port: int = 8000,
                 port_range: Tuple[int, int] = (8000, 9000),
                 state_file: Optional[Path] = None):
        """
        Initialize port discovery system
        
        Args:
            preferred_port: Preferred port to use if available
            port_range: Range of ports to scan for availability
            state_file: File to persist port allocation state
        """
        self.preferred_port = preferred_port
        self.port_range = port_range
        self.state_file = state_file or Path.home() / '.ai_assistant' / 'port_state.json'
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.allocated_ports = self.load_state()
        
    def find_available_port(self, service_name: str = 'backend') -> int:
        """
        Find an available port for a service
        
        Args:
            service_name: Name of the service requesting a port
            
        Returns:
            Available port number
        """
        # Check if service already has a port allocated
        if service_name in self.allocated_ports:
            port = self.allocated_ports[service_name]
            if self.is_port_available(port):
                logger.info(f"Reusing previously allocated port {port} for {service_name}")
                return port
            else:
                logger.info(f"Previously allocated port {port} for {service_name} is in use")
        
        # Try preferred port first
        if self.is_port_available(self.preferred_port):
            self.allocate_port(service_name, self.preferred_port)
            return self.preferred_port
        
        # Scan for available port in range
        for port in range(self.port_range[0], self.port_range[1]):
            if self.is_port_available(port):
                self.allocate_port(service_name, port)
                logger.info(f"Found available port {port} for {service_name}")
                return port
        
        # If no port in range is available, use system-assigned port
        port = self.get_system_port()
        self.allocate_port(service_name, port)
        logger.warning(f"No port in range {self.port_range} available, using system port {port}")
        return port
    
    def is_port_available(self, port: int) -> bool:
        """
        Check if a port is available for binding
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is available, False otherwise
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return True
        except (OSError, socket.error):
            return False
    
    def get_system_port(self) -> int:
        """
        Get a system-assigned available port
        
        Returns:
            Available port number assigned by the system
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            port = s.getsockname()[1]
            return port
    
    def allocate_port(self, service_name: str, port: int) -> None:
        """
        Allocate a port to a service and persist state
        
        Args:
            service_name: Name of the service
            port: Port number to allocate
        """
        self.allocated_ports[service_name] = port
        self.save_state()
        logger.info(f"Allocated port {port} to {service_name}")
    
    def release_port(self, service_name: str) -> None:
        """
        Release a port allocation for a service
        
        Args:
            service_name: Name of the service
        """
        if service_name in self.allocated_ports:
            port = self.allocated_ports.pop(service_name)
            self.save_state()
            logger.info(f"Released port {port} from {service_name}")
    
    def get_allocated_port(self, service_name: str) -> Optional[int]:
        """
        Get the allocated port for a service
        
        Args:
            service_name: Name of the service
            
        Returns:
            Port number if allocated, None otherwise
        """
        return self.allocated_ports.get(service_name)
    
    def load_state(self) -> dict:
        """
        Load port allocation state from file
        
        Returns:
            Dictionary of service to port mappings
        """
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load port state: {e}")
        return {}
    
    def save_state(self) -> None:
        """
        Save port allocation state to file
        """
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.allocated_ports, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save port state: {e}")
    
    def find_process_using_port(self, port: int) -> Optional[int]:
        """
        Find the process ID using a specific port
        
        Args:
            port: Port number to check
            
        Returns:
            Process ID if found, None otherwise
        """
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        return proc.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def kill_process_on_port(self, port: int, force: bool = False) -> bool:
        """
        Kill process using a specific port
        
        Args:
            port: Port number
            force: Force kill if True, otherwise try graceful shutdown
            
        Returns:
            True if process was killed, False otherwise
        """
        pid = self.find_process_using_port(port)
        if pid:
            try:
                process = psutil.Process(pid)
                if force:
                    process.kill()
                else:
                    process.terminate()
                logger.info(f"Killed process {pid} using port {port}")
                return True
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.error(f"Failed to kill process {pid}: {e}")
        return False
    
    def get_all_allocated_ports(self) -> dict:
        """
        Get all allocated ports
        
        Returns:
            Dictionary of service to port mappings
        """
        return self.allocated_ports.copy()
    
    def cleanup_stale_allocations(self) -> None:
        """
        Clean up stale port allocations (ports not actually in use)
        """
        stale_services = []
        for service, port in self.allocated_ports.items():
            if self.is_port_available(port):
                stale_services.append(service)
        
        for service in stale_services:
            self.release_port(service)
            logger.info(f"Cleaned up stale allocation for {service}")
    
    def write_port_file(self, port: int, filepath: Optional[Path] = None) -> None:
        """
        Write port number to a file for other processes to read
        
        Args:
            port: Port number to write
            filepath: Path to write to (default: .ai_assistant/current_port.txt)
        """
        if filepath is None:
            filepath = Path.home() / '.ai_assistant' / 'current_port.txt'
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(str(port))
        logger.info(f"Wrote port {port} to {filepath}")
    
    @staticmethod
    def read_port_file(filepath: Optional[Path] = None) -> Optional[int]:
        """
        Read port number from file
        
        Args:
            filepath: Path to read from (default: .ai_assistant/current_port.txt)
            
        Returns:
            Port number if file exists and is valid, None otherwise
        """
        if filepath is None:
            filepath = Path.home() / '.ai_assistant' / 'current_port.txt'
        
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return int(f.read().strip())
            except (ValueError, IOError) as e:
                logger.error(f"Failed to read port file: {e}")
        return None


# Global instance for convenience
_port_discovery = None

def get_port_discovery() -> PortDiscovery:
    """Get or create global PortDiscovery instance"""
    global _port_discovery
    if _port_discovery is None:
        _port_discovery = PortDiscovery()
    return _port_discovery

def discover_backend_port() -> int:
    """
    Convenience function to discover backend port
    
    Returns:
        Available port for backend service
    """
    discovery = get_port_discovery()
    return discovery.find_available_port('backend')

def cleanup_backend_port() -> None:
    """
    Convenience function to cleanup backend port allocation
    """
    discovery = get_port_discovery()
    discovery.release_port('backend')