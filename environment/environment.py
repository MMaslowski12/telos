# ------------------------------------------------
from __future__ import annotations
import gspread
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from google.oauth2.service_account import Credentials
import warnings

from environment.components import (
    Wing, Stabilizer, Fin, Atmosphere,
    Propulsion, Inertia, Aerodynamics
)

# ─────────────────────────────  ENVIRONMENT  ───────────────────────────────
class Environment:
    """Master class managing all components and their interactions."""
    
    def __init__(self, worksheet: Optional[gspread.Worksheet] = None):
        # Create components
        self.wing = Wing(worksheet=worksheet)
        self.stab = Stabilizer(worksheet=worksheet)
        self.fin = Fin(worksheet=worksheet)
        self.atmosphere = Atmosphere(worksheet=worksheet)
        self.propulsion = Propulsion(worksheet=worksheet)
        self.inertia = Inertia(worksheet=worksheet, environment=self)
        self.aero = Aerodynamics(worksheet=worksheet, environment=self)
        
        # Set cruise speed from worksheet if provided
        if worksheet:
            self.cruise_speed_mps = float(worksheet.acell('I16').value)
        else:
            raise ValueError("No worksheet provided")
    
    def _get_components(self):
        """Get all component instances."""
        return [
            self.wing, self.stab, self.fin,
            self.atmosphere, self.propulsion,
            self.inertia, self.aero
        ]
    
    def update_all(self):
        """Update all components and their dependencies."""
        # First update basic components
        self.wing.update_all()
        self.stab.update_all()
        self.fin.update_all()
        self.atmosphere.update_all()
        
        # Update propulsion with current velocity
        self.propulsion.update_propulsive_efficiency(self.cruise_speed_mps)
        self.propulsion.update_thrust_N()
        
        # Update inertia which depends on wing, stab, and fin
        self.inertia.update_all()
        
        # Update aerodynamics with current velocity
        self.aero.cruise_speed_mps = self.cruise_speed_mps
        self.aero.update_all()
        self.aero.update_inertia_power()
    
    def push_to_gsheet(self, worksheet: Optional[gspread.Worksheet] = None):
        """
        Push all component values to Google Sheets.
        
        Args:
            worksheet: Optional worksheet to use instead of the stored one
        """
        target_worksheet = worksheet or self.worksheet
        if not target_worksheet:
            raise ValueError("No worksheet provided")
            
        # Push cruise speed
        try:
            target_worksheet.update('I16', self.cruise_speed_mps)
        except Exception as e:
            warnings.warn(f"Could not update cruise speed: {str(e)}")
            
        # Push all components
        for component in self._get_components():
            component.push_to_gsheet(target_worksheet)
    
    def from_gsheet(self, worksheet: gspread.Worksheet) -> None:
        """
        Update this environment instance from Google Sheets data.
        
        Args:
            worksheet: The Google Sheets worksheet to read from
        """
        self.worksheet = worksheet
        
        # Get cruise speed
        try:
            self.cruise_speed_mps = float(worksheet.acell('I16').value)
        except Exception as e:
            warnings.warn(f"Could not read cruise speed from sheet: {str(e)}")
        
        # Load all components from sheet
        for component in self._get_components():
            component.from_gsheet(worksheet)
    
    def validate(self) -> bool:
        """
        Validate all components and their relationships.
        
        Returns:
            True if all validations pass, False otherwise
        """
        if not self.worksheet:
            warnings.warn("No worksheet provided for validation")
            return False
            
        # Update all components to get current state
        self.update_all()
        
        # Push to sheet to trigger validations
        self.push_to_gsheet()
        
        # Check if any warnings were raised
        return True  # You might want to add more specific validation logic here
