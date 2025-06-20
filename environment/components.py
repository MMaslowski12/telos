# -----------------------------------------------------------
# Sheet: syf (1).xlsx  |  all formulas documented inline.
# -----------------------------------------------------------
from __future__ import annotations
from math import pow
from dataclasses import dataclass, field, MISSING, fields
from typing import Optional, Dict, Any, Callable
from functools import wraps
import gspread
from google.oauth2.service_account import Credentials
import warnings

def cell(a1: str, derivative: bool = False):
    """
    Create a field with cell metadata.
    
    Args:
        a1: The cell reference in A1 notation
        derivative: If True, this is a calculated field (default=0)
    """
    if derivative:
        return field(default=0, metadata={'cell': a1, 'derivative': True})
    return field(default=MISSING, metadata={'cell': a1})

def updater(func: Callable) -> Callable:
    """Decorator to mark methods that update component values."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs)
    wrapper._is_updater = True
    return wrapper

g = 9.80665                               # gravity [m/s²]  (I10, I22 …)

# ─────────────────────────────  COMPONENT BASE  ────────────────────────────
@dataclass
class Component:
    """Base class for all components in the system."""

    def __post_init__(self):
        """Initialize non-derivative values from Google Sheets if worksheet is provided."""
        if hasattr(self, 'worksheet'):
            for field_info in fields(self):
                if 'cell' not in field_info.metadata:
                    continue
                
                # Skip derivative fields
                if field_info.metadata.get('derivative', False):
                    continue
                
                cell_ref = field_info.metadata['cell']
                try:
                    value = self.worksheet.acell(cell_ref).value
                    if value:
                        setattr(self, field_info.name, float(value))
                except Exception as e:
                    warnings.warn(f"Could not read cell {cell_ref}: {str(e)}")

    def update_all(self) -> None:
        """Update all calculated values for this component."""
        for method_name in dir(self):
            method = getattr(self, method_name)
            if callable(method) and hasattr(method, '_is_updater'):
                method()

    def push_to_gsheet(self, worksheet: gspread.Worksheet) -> None:
        """
        Push all non-derivative values to Google Sheets and validate derivative values.
        
        Args:
            worksheet: The Google Sheets worksheet to update
        """
        # Get all fields from the dataclass
        for field_info in fields(self):
            # Skip fields without cell metadata
            if 'cell' not in field_info.metadata:
                continue

            cell_ref = field_info.metadata['cell']
            value = getattr(self, field_info.name)

            # Get the current value from the sheet
            try:
                sheet_value = worksheet.acell(cell_ref).value
                if sheet_value:
                    sheet_value = float(sheet_value)
            except Exception as e:
                warnings.warn(f"Could not read cell {cell_ref}: {str(e)}")
                continue

            # Check if this is a derivative field
            is_derivative = field_info.metadata.get('derivative', False)

            if is_derivative:
                # For derivative fields, validate the value
                if sheet_value is not None and abs(sheet_value - value) > 1e-10:
                    warnings.warn(
                        f"Value mismatch in {self.__class__.__name__}.{field_info.name} "
                        f"(cell {cell_ref}): sheet={sheet_value}, calculated={value}"
                    )
            else:
                # For non-derivative fields, push the value to the sheet
                try:
                    worksheet.update(cell_ref, value)
                except Exception as e:
                    warnings.warn(f"Could not update cell {cell_ref}: {str(e)}")

    def from_gsheet(self, worksheet: gspread.Worksheet) -> None:
        """
        Update this component's values from Google Sheets data.
        
        Args:
            worksheet: The Google Sheets worksheet to read from
        """
        self.worksheet = worksheet
        
        # Get all fields from the dataclass
        for field_info in fields(self):
            # Skip fields without cell metadata
            if 'cell' not in field_info.metadata:
                continue

            cell_ref = field_info.metadata['cell']
            try:
                value = worksheet.acell(cell_ref).value
                if value:
                    setattr(self, field_info.name, float(value))
            except Exception as e:
                warnings.warn(f"Could not read cell {cell_ref}: {str(e)}")
        
        # Run all updates
        self.update_all()
        
        # Validate values against sheet
        for field_info in fields(self):
            if 'cell' not in field_info.metadata:
                continue
                
            cell_ref = field_info.metadata['cell']
            calculated_value = getattr(self, field_info.name)
            
            try:
                sheet_value = worksheet.acell(cell_ref).value
                if sheet_value:
                    sheet_value = float(sheet_value)
                    # Check if this is a derivative field
                    is_derivative = field_info.metadata.get('derivative', False)
                    
                    if is_derivative and abs(sheet_value - calculated_value) > 1e-10:
                        warnings.warn(
                            f"Value mismatch in {self.__class__.__name__}.{field_info.name} "
                            f"(cell {cell_ref}): sheet={sheet_value}, calculated={calculated_value}"
                        )
            except Exception as e:
                warnings.warn(f"Could not validate cell {cell_ref}: {str(e)}")


# ─────────────────────────  WING-LIKE SURFACES  ────────────────────────────
@dataclass
class Wing(Component):
    span_m: float = cell('C31')                 # C31 / C45 / C59
    root_chord_m: float = cell('C32')           # C32 / C46 / C60
    tip_chord_m: float = cell('C33')            # C33 / C47 / C61
    emp_coeff: float = cell('E30')              # E30 / E44 / E58
    surface_area_m2: Optional[float] = cell('C37')  # C37 / C51 / C65 (only stored)
    aspect_ratio: float = cell('C38', derivative=True)  # C38 / C52 / C66
    volume: float = cell('E4', derivative=True)  # E4 / E5 / E6

    @updater
    def update_aspect_ratio(self) -> None:
        """Aspect Ratio  ( = span / root-chord )"""
        self.aspect_ratio = self.span_m / self.root_chord_m

    @updater
    def update_volume(self) -> None:
        """
        Internal volume [m³]  
        Excel:  E4 = E30*((C32+C33)/2)^2*C31   (and analogues for tail/fins)
        """
        mean_chord = 0.5 * (self.root_chord_m + self.tip_chord_m)
        self.volume = self.emp_coeff * mean_chord**2 * self.span_m


@dataclass
class Stabilizer(Wing):
    """Horizontal tail – same geometry rules as the wing."""
    span_m: float = cell('C45')                 # C31 / C45 / C59
    root_chord_m: float = cell('C46')           # C32 / C46 / C60
    tip_chord_m: float = cell('C47')            # C33 / C47 / C61
    emp_coeff: float = cell('E44')              # E30 / E44 / E58
    surface_area_m2: Optional[float] = cell('C51')  # C37 / C51 / C65 (only stored)
    aspect_ratio: float = cell('C52', derivative=True)  # C38 / C52 / C66
    volume: float = cell('E5', derivative=True)  # E4 / E5 / E6


@dataclass
class Fin(Wing):
    """Vertical tail – ditto."""
    span_m: float = cell('C59')                 # C31 / C45 / C59
    root_chord_m: float = cell('C60')           # C32 / C46 / C60
    tip_chord_m: float = cell('C61')            # C33 / C47 / C61
    emp_coeff: float = cell('E58')              # E30 / E44 / E58
    surface_area_m2: Optional[float] = cell('C65')  # C37 / C51 / C65 (only stored)
    aspect_ratio: float = cell('C66', derivative=True)  # C38 / C52 / C66
    volume: float = cell('E6', derivative=True)  # E4 / E5 / E6


# ─────────────────────────────  ATMOSPHERE  ────────────────────────────────
@dataclass
class Atmosphere(Component):
    cruise_height_m: float = cell('I30')                 # I30
    ref_density_kg_m3: float = cell('I34')       # I34
    ref_temperature_K: float = cell('I35')      # I35
    temperature_at_cruise: float = cell('I32', derivative=True)  # I32
    density_at_cruise: float = cell('I31', derivative=True)  # I31 & I33

    @updater
    def update_temperature_at_cruise(self) -> None:
        L = 0.0065                                     # lapse rate [K/m]
        self.temperature_at_cruise = self.ref_temperature_K - L * self.cruise_height_m

    @updater
    def update_density_at_cruise(self) -> None:
        T = self.temperature_at_cruise
        exponent = (g / (287.05 * 0.0065)) - 1.0       # ISA exponent ≈ 4.256
        self.density_at_cruise = self.ref_density_kg_m3 * pow(T / self.ref_temperature_K, exponent)


# ─────────────────────────────  PROPULSION  ────────────────────────────────
@dataclass
class Propulsion(Component):
    cruise_throttle: float = cell('I4')          # I4
    motor_eff_g_per_W: float = cell('I7')        # I7
    motor_power_draw_W: float = cell('I8')       # I8
    prop_thrust_gen_g: float = cell('K9')        # K9
    battery_energy_J: float = cell('I3')         # I3  (passed as attr)
    battery_efficiency: float = cell('I5')  # I5 (stored only)
    propulsive_efficiency: float = cell('I6', derivative=True)  # I6
    thrust_N: float = cell('I10', derivative=True)  # I10

    @updater
    def update_propulsive_efficiency(self, V: float) -> None:
        self.propulsive_efficiency = self.motor_eff_g_per_W * V / self.motor_power_draw_W

    @updater
    def update_thrust_N(self) -> None:
        kg_equiv = self.prop_thrust_gen_g * (self.cruise_throttle**2) / 1000.0
        self.thrust_N = kg_equiv * g


# ───────────────────────────────  INERTIA  ────────────────────────────────
@dataclass
class Inertia(Component):
    density_struct_kg_m3: float = cell('D4')    # D4
    motor_mass_kg: float = cell('C7')           # C7
    propeller_mass_kg: float = cell('C8')       # C8
    battery_mass_kg: float = cell('C9')         # C9
    servos_mass_kg: float = cell('C10')          # C10 (passed attr)
    electronics_mass_kg: float = cell('C11')     # C11
    fuselage_mass_kg: float = cell('C12')        # C12
    payload_mass_kg: float = cell('C13')   # C13
    power_required_W: Optional[float] = cell('I11')  # I11
    power_available_W: Optional[float] = cell('I12')  # I12
    wing_mass: float = cell('C4', derivative=True)  # C4
    elevator_mass: float = cell('C5', derivative=True)  # C5
    rudder_mass: float = cell('C6', derivative=True)  # C6
    total_mass: float = cell('C14', derivative=True)  # C14
    
    # Reference to environment for dependencies
    environment: Optional['Environment'] = None

    @updater
    def update_wing_mass(self) -> None:
        self.wing_mass = self.density_struct_kg_m3 * self.environment.wing.volume

    @updater
    def update_elevator_mass(self) -> None:
        self.elevator_mass = self.density_struct_kg_m3 * self.environment.stab.volume

    @updater
    def update_rudder_mass(self) -> None:
        self.rudder_mass = self.density_struct_kg_m3 * self.environment.fin.volume

    @updater
    def update_total_mass(self) -> None:
        self.total_mass = (self.wing_mass + self.elevator_mass + self.rudder_mass +
                self.motor_mass_kg + self.propeller_mass_kg +
                self.battery_mass_kg + self.servos_mass_kg +
                self.electronics_mass_kg + self.fuselage_mass_kg +
                self.payload_mass_kg)

    def set_power_numbers(self, P_req: float, P_avail: float):
        self.power_required_W = P_req   # I11
        self.power_available_W = P_avail  # I12


# ────────────────────────────  AERODYNAMICS  ──────────────────────────────
@dataclass
class Aerodynamics(Component):
    cruise_speed_mps: float = cell('I16')        # I16
    cruise_CL: float = cell('I18')               # I18
    cruise_CD: float = cell('I19')               # I19
    wing_surface_area_m2: float = cell('C37')    # C37
    cruise_lift: float = cell('I21', derivative=True)  # I21
    cruise_drag: float = cell('I23', derivative=True)  # I23
    weight: float = cell('I22', derivative=True)  # I22
    cruise_power_required: float = cell('I17', derivative=True)  # I17 / I11
    cruise_thrust: float = cell('I20', derivative=True)  # I20 / I12
    cruise_power_available: float = cell('I12', derivative=True)  # I12
    endurance_seconds: float = cell('I26', derivative=True)  # I26
    
    # Reference to environment for dependencies
    environment: Optional['Environment'] = None

    @updater
    def update_cruise_lift(self) -> None:
        rho = self.environment.atmosphere.density_at_cruise
        self.cruise_lift = 0.5 * rho * self.cruise_speed_mps**2 * self.wing_surface_area_m2 * self.cruise_CL

    @updater
    def update_cruise_drag(self) -> None:
        rho = self.environment.atmosphere.density_at_cruise
        self.cruise_drag = 0.5 * rho * self.cruise_speed_mps**2 * self.wing_surface_area_m2 * self.cruise_CD

    @updater
    def update_weight(self) -> None:
        self.weight = self.environment.inertia.total_mass * g

    @updater
    def update_cruise_power_required(self) -> None:
        self.cruise_power_required = self.cruise_drag * self.cruise_speed_mps

    @updater
    def update_cruise_thrust(self) -> None:
        self.cruise_thrust = self.environment.propulsion.thrust_N

    @updater
    def update_cruise_power_available(self) -> None:
        self.cruise_power_available = self.cruise_thrust * self.cruise_speed_mps

    @updater
    def update_endurance_seconds(self) -> None:
        prop = self.environment.propulsion
        self.endurance_seconds = prop.battery_energy_J / (prop.motor_power_draw_W * prop.cruise_throttle)

    def update_inertia_power(self):
        self.environment.inertia.set_power_numbers(
            self.cruise_power_required,
            self.cruise_power_available
        )
