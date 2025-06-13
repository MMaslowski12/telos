"""
tools.py

Wraps the XFLRpy client in a convenient ToolManager class.
All public methods are typed so that openai_agent.py can auto‑generate
JSON‑schemas for function calling.

NB: XFLR5 must be running in server mode on port 8080 for this to work.
"""

from __future__ import annotations

from typing import List, Dict, Tuple, Optional, Any, Union

import sys
sys.path.insert(0, "xflrpy/PythonClient/xflrpy/PythonClient")

from xflrpy import (
    xflrClient,
    enumApp,
    Plane,
    WingSection,
    WPolar,
    enumPolarType,
    AnalysisSettings3D,
    enumWPolarResult,
    enumAnalysisMethod,
    PointMass,
    Vector3d,
)

import asyncio


class ToolManager:
    """
    Thin wrapper around the xflrpy API exposing a handful of high‑level
    operations (create plane, modify geometry, run polar analysis, add point
    masses).  Each method is designed to be callable from a JSON payload so
    that an LLM can invoke it through OpenAI function calling.
    """

    def __init__(self, project_path: str, project_name: str, plane_name: str):
        self.xp = xflrClient(port=8080, connect_timeout=100)
        self.xp.setApp(enumApp.MIAREX)
        self.app = self.xp.loadProject(files=project_path + project_name, save_current=False)
        self.miarex = self.xp.getApp()
        self.plane_name = plane_name

    # --------------------------------------------------------------------- #
    #  Geometry                                                             #
    # --------------------------------------------------------------------- #
    def setup_airplane(
        self,
        plane_name: Optional[str] = None,
        sec0_foil_name: str = "E387",
        sec0_chord: float = 0.2,
        sec1_chord: float = 0.1,
        sec1_y_position: float = 1.0,
        sec1_offset: float = 0.2,
        sec1_twist: float = 5.0,
        sec1_dihedral: float = 5.0,
        sec1_foil_name: str = "E387",
    ) -> Tuple[Plane, Dict]:
        """Create a new plane and add it to the project, returning plane + data."""
        if plane_name is None:
            plane_name = self.plane_name

        plane = Plane(name=plane_name)

        # --- Wing
        sec0 = WingSection(
            chord=sec0_chord,
            right_foil_name=sec0_foil_name,
            left_foil_name=sec0_foil_name,
        )
        sec1 = WingSection(
            y_position=sec1_y_position,
            chord=sec1_chord,
            offset=sec1_offset,
            twist=sec1_twist,
            dihedral=sec1_dihedral,
            right_foil_name=sec1_foil_name,
            left_foil_name=sec1_foil_name,
        )
        plane.wing.sections.extend([sec0, sec1])

        # --- Elevator
        elev_sec0 = WingSection(
            y_position=0.0,
            chord=0.05,
            right_foil_name="NACA 0012 AIRFOILS",
            left_foil_name="NACA 0012 AIRFOILS",
        )
        elev_sec1 = WingSection(
            y_position=0.1,
            chord=0.02,
            offset=0.02,
            right_foil_name="NACA 0012 AIRFOILS",
            left_foil_name="NACA 0012 AIRFOILS",
        )
        plane.elevator.sections.extend([elev_sec0, elev_sec1])

        # --- Fin
        fin_sec0 = WingSection(
            y_position=0.0,
            chord=0.1,
            right_foil_name="NACA 0012 AIRFOILS",
            left_foil_name="NACA 0012 AIRFOILS",
        )
        fin_sec1 = WingSection(
            y_position=0.12,
            chord=0.06,
            offset=0.04,
            right_foil_name="NACA 0012 AIRFOILS",
            left_foil_name="NACA 0012 AIRFOILS",
        )
        plane.fin.sections.extend([fin_sec0, fin_sec1])

        self.miarex.plane_mgr.addPlane(plane)
        plane_data = self.miarex.plane_mgr.getPlaneData(plane_name)

        return plane, plane_data

    def modify_plane(
        self,
        surface: str,
        section: int,
        attribute: str,
        value: Union[float, str],
        plane_name: Optional[str] = None,
    ) -> Plane:
        """Change a single attribute on a given wing/elevator/fin section."""
        if plane_name is None:
            plane_name = self.plane_name

        plane = self.miarex.plane_mgr.getPlane(plane_name)
        surf_obj = getattr(plane, surface)
        target_section = surf_obj.sections[section]
        target_section[attribute] = value

        # Replace plane in XFLR5
        self.xp._client.call("deletePlane", plane_name)
        self.miarex.plane_mgr.addPlane(plane)
        return plane

    # --------------------------------------------------------------------- #
    #  Analysis                                                              #
    # --------------------------------------------------------------------- #
    def perform_analysis(
        self,
        analysis_name: str,
        plane_name: Optional[str] = None,
        start_alpha: float = -10.0,
        end_alpha: float = 20.0,
        delta_alpha: float = 0.5,
    ) -> List[Dict[str, float]]:
        """Run a fixed‑speed VLM polar over a range of alpha and return results."""
        if plane_name is None:
            plane_name = self.plane_name

        wpolar = WPolar(name=analysis_name, plane_name=plane_name)
        wpolar.spec.polar_type = enumPolarType.FIXEDSPEEDPOLAR
        wpolar.spec.free_stream_speed = 10
        wpolar.spec.analysis_method = enumAnalysisMethod.VLMMETHOD

        self.miarex.define_analysis(wpolar=wpolar)
        settings = AnalysisSettings3D(
            is_sequence=True,
            sequence=(start_alpha, end_alpha, delta_alpha),
        )

        results = self.miarex.analyze(
            analysis_name,
            plane_name,
            settings,
            result_list=[
                enumWPolarResult.ALPHA,
                enumWPolarResult.CLCD,
                enumWPolarResult.CL,
                enumWPolarResult.CD,
                enumWPolarResult.CL32CD,
                enumWPolarResult.CM,
            ],
        )
        return results

    # --------------------------------------------------------------------- #
    #  Mass properties                                                       #
    # --------------------------------------------------------------------- #
    def add_point_masses(
        self,
        point_masses: Optional[List[Dict[str, Any]]] = None,
        plane_name: Optional[str] = None,
    ) -> bool:
        """Add arbitrary point masses to a plane so XFLR5 can compute inertia."""
        if plane_name is None:
            plane_name = self.plane_name

        if point_masses:
            for pm in point_masses:
                point_mass = PointMass(
                    mass=pm["mass"],
                    position=Vector3d(*pm["position"]),
                    tag=pm.get("tag", ""),
                )
                self.miarex.plane_mgr.add_point_mass(plane_name, point_mass)
        return True


__all__ = ["ToolManager"]
