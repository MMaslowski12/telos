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

# ─────────────────────────────  DEFAULT VALUES  ────────────────────────────
# Default parameters for Environment components
DEFAULT_WING_PARAMS = {
    'span_m': 2.0,                    # C31: Wingspan [m]: 2
    'root_chord_m': 0.2,              # C32: Root Chord [m]: 0.2 (from tools.py sec0_chord)
    'tip_chord_m': 0.1,               # C33: Tip Chord [m]: 0.1 (from tools.py sec1_chord)
    'emp_coeff': 0.08,                # E30: Emp. Coeff: 0.08
    'surface_area_m2': 0.45           # C37: Surface Area [m^2]: 0.45
}

DEFAULT_STAB_PARAMS = {
    'span_m': 0.34,                   # C45: Span [m]: 0.34
    'root_chord_m': 0.05,             # C46: Root Chord [m]: 0.05 (from tools.py elev_sec0_chord)
    'tip_chord_m': 0.02,              # C47: Tip Chord [m]: 0.02 (from tools.py elev_sec1_chord)
    'emp_coeff': 0.0822,              # E44: Emp. Coeff: 0.0822
    'surface_area_m2': 0.03           # C51: Surface Area [m^2]: 0.03
}

DEFAULT_FIN_PARAMS = {
    'span_m': 0.12,                   # C59: Span [m]: 0.12
    'root_chord_m': 0.1,              # C60: Root Chord [m]: 0.1 (from tools.py fin_sec0_chord)
    'tip_chord_m': 0.06,              # C61: Tip Chord [m]: 0.06 (from tools.py fin_sec1_chord)
    'emp_coeff': 0.0822,              # E58: Emp. Coeff: 0.0822
    'surface_area_m2': 0.01           # C65: Surface Area [m^2]: 0.01
}

DEFAULT_ATMOSPHERE_PARAMS = {
    'cruise_height_m': 150.0,          # I30: Cruise Height [m]: 150
    'ref_density_kg_m3': 1.225,        # I34: Reference Air Density [kg/m^3]: 1.225
    'ref_temperature_K': 288.15        # I35: Reference Temperature [K]: 288.15
}

DEFAULT_PROPULSION_PARAMS = {
    'battery_energy_J': 87912.0,       # I3: Battery Energy [J]: 87912
    'cruise_throttle': 0.20,           # I4: Cruise Throttle: 20%
    'battery_efficiency': 0.92,        # I5: Battery Efficiency: 92%
    'motor_eff_g_per_W': 4.7,          # I7: Motor Efficiency for ChosenPropeller [g/W]: 4.7
    'motor_power_draw_W': 289.0,       # I8: Motor Power Draw for Chosen Propeller [W]: 289
    'prop_thrust_gen_g': 1580.0        # K9: Propeller Thrust Generation [g]: 1580
}

DEFAULT_INERTIA_PARAMS = {
    'density_struct_kg_m3': 32.0,      # D4: Density [kg/m^3]: 32 (Foam)
    'motor_mass_kg': 0.115,            # C7: Motor: 0.115 kg
    'propeller_mass_kg': 0.025,        # C8: Propeller: 0.025 kg
    'battery_mass_kg': 0.188,          # C9: Battery: 0.188 kg
    'servos_mass_kg': 0.072,           # C10: Servos: 0.072 kg
    'electronics_mass_kg': 0.010,      # C11: Other Electronics: 0.010 kg
    'fuselage_mass_kg': 0.090,         # C12: Fuselage: 0.090 kg
    'payload_mass_kg': 0.000           # C13: Payload: 0.000 kg
}

DEFAULT_AERO_PARAMS = {
    'cruise_speed_mps': 8.0,           # I16: Cruise Speed [m/s]: 8
    'cruise_CL': -0.005,               # I18: Cruise C_L: -0.005
    'cruise_CD': 0.0,                  # I19: Cruise C_D: (empty in spreadsheet)
    'wing_surface_area_m2': 0.45,      # C37: Updated to match wing surface area
}

# ─────────────────────────────  ENVIRONMENT  ───────────────────────────────
class Environment:
    """Master class managing all components and their interactions."""
    
    def __init__(self, 
                 cruise_speed_mps: float = 0.0,
                 wing_params: Optional[Dict[str, float]] = None,
                 stab_params: Optional[Dict[str, float]] = None,
                 fin_params: Optional[Dict[str, float]] = None,
                 atmosphere_params: Optional[Dict[str, float]] = None,
                 propulsion_params: Optional[Dict[str, float]] = None,
                 inertia_params: Optional[Dict[str, float]] = None,
                 aero_params: Optional[Dict[str, float]] = None,
                 from_gsheet: bool = False,
                 worksheet: Optional[gspread.Worksheet] = None):
        """
        Initialize Environment with all components.
        
        Args:
            cruise_speed_mps: Cruise speed in m/s
            wing_params: Dictionary with wing parameters (span_m, root_chord_m, tip_chord_m, emp_coeff, surface_area_m2)
            stab_params: Dictionary with stabilizer parameters
            fin_params: Dictionary with fin parameters
            atmosphere_params: Dictionary with atmosphere parameters
            propulsion_params: Dictionary with propulsion parameters
            inertia_params: Dictionary with inertia parameters
            aero_params: Dictionary with aerodynamics parameters
            from_gsheet: If True, load values from Google Sheets worksheet
            worksheet: Google Sheets worksheet to read from (required if from_gsheet=True)
        """
        # Set default parameters if not provided
        wing_params = wing_params or DEFAULT_WING_PARAMS
        stab_params = stab_params or DEFAULT_STAB_PARAMS
        fin_params = fin_params or DEFAULT_FIN_PARAMS
        atmosphere_params = atmosphere_params or DEFAULT_ATMOSPHERE_PARAMS
        propulsion_params = propulsion_params or DEFAULT_PROPULSION_PARAMS
        inertia_params = inertia_params or DEFAULT_INERTIA_PARAMS
        aero_params = aero_params or DEFAULT_AERO_PARAMS
        
        # Create components with parameters
        self.wing = Wing(**wing_params)
        self.stab = Stabilizer(**stab_params)
        self.fin = Fin(**fin_params)
        self.atmosphere = Atmosphere(**atmosphere_params)
        self.propulsion = Propulsion(environment=self, **propulsion_params)
        self.inertia = Inertia(environment=self, **inertia_params)
        self.aero = Aerodynamics(environment=self, **aero_params)
        
        # Set default cruise speed (this will also set it in aero component)
        self.cruise_speed_mps = cruise_speed_mps
        self.worksheet = None
        
        # Load from Google Sheets if requested
        if from_gsheet:
            if worksheet is None:
                raise ValueError("worksheet parameter is required when from_gsheet=True")
            self.from_gsheet(worksheet)
    
    @property
    def cruise_speed_mps(self):
        """Get cruise speed from aerodynamics component."""
        return self.aero.cruise_speed_mps
    
    @cruise_speed_mps.setter
    def cruise_speed_mps(self, value):
        """Set cruise speed in aerodynamics component."""
        self.aero.cruise_speed_mps = value
    
    def _get_components(self):
        """Get all component instances in the correct update order."""
        return [
            self.wing, self.stab, self.fin, self.atmosphere,
            self.propulsion, self.inertia, self.aero
        ]
    
    def update_all(self):
        """Update all components and their dependencies."""
        # Update all components in order - each component handles its own dependencies
        for component in self._get_components():
            component.update_all()
    
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
