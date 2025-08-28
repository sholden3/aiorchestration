#!/usr/bin/env python3
"""
@fileoverview Example file that follows all governance requirements
@author Alex Novak v3.0 & Dr. Sarah Chen v1.2 - 2025-01-28
@architecture Backend/Integration - Example component
@responsibility Demonstrate proper governance compliance
@dependencies None - standalone example
@integration_points None - example only
@testing_strategy Unit tests with full coverage
@governance Fully compliant with all requirements

Business Logic Summary:
- Demonstrates secure coding practices
- Shows proper documentation
- Includes error handling

Architecture Integration:
- Example of compliant code
- Can be used as template
- Shows best practices
"""

import logging
from typing import Optional

# Configure logging properly
logger = logging.getLogger(__name__)


class GovernanceCompliantExample:
    """
    @class GovernanceCompliantExample
    @description Example class following all governance rules
    @architecture_role Demonstration of compliance
    @business_logic Shows proper patterns
    @failure_modes Handles all errors gracefully
    @debugging_info Full logging and tracing
    
    Defensive Programming Patterns:
    - Input validation on all methods
    - Proper error handling
    - Resource cleanup
    
    Integration Boundaries:
    - No external dependencies
    - Self-contained example
    - Safe to use as template
    """
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize example with optional config
        
        @param config Optional configuration dict
        @validation Config must be dict or None
        @side_effects Initializes internal state
        @error_handling Defaults to empty config if None
        """
        self.config = config or {}
        self.initialized = True
        logger.info("GovernanceCompliantExample initialized")
    
    def process_data(self, data: str) -> str:
        """
        Process data following all security rules
        
        @method process_data
        @description Safely processes input data
        @business_rule No eval, exec, or dangerous operations
        @validation Input must be string
        @side_effects None
        @error_handling Returns empty string on error
        @performance O(n) where n is data length
        @testing_requirements Unit test with various inputs
        
        @param data Input data to process
        @returns Processed data string
        @throws ValueError if data is not string
        
        Architecture Notes:
        - No external calls
        - Safe string operations only
        - Proper validation
        
        Sarah's Framework Check:
        - What breaks first: Invalid input type
        - How we know: Type checking
        - Plan B: Return empty string
        """
        # BUSINESS RULE: Validate input type
        # VALIDATION: Must be string
        # ERROR HANDLING: Raise ValueError for wrong type
        if not isinstance(data, str):
            logger.error(f"Invalid input type: {type(data)}")
            raise ValueError("Data must be string")
        
        # BUSINESS LOGIC: Safe processing only
        # SARAH'S FRAMEWORK: No dangerous operations
        # ALEX'S 3AM TEST: Clear error messages
        
        try:
            # Safe string processing
            processed = data.strip().lower()
            
            # No secrets in code
            # No eval or exec
            # No hardcoded credentials
            
            logger.debug(f"Processed data length: {len(processed)}")
            return processed
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return ""  # Safe fallback
    
    def cleanup(self):
        """
        Proper cleanup method
        
        @method cleanup
        @description Ensures proper resource cleanup
        @side_effects Resets internal state
        """
        self.initialized = False
        logger.info("Cleanup completed")


# Example usage (would be in separate test file normally)
if __name__ == "__main__":
    # This is just an example
    example = GovernanceCompliantExample()
    result = example.process_data("Test Data")
    print(f"Result: {result}")
    example.cleanup()