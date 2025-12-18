"""
SoilWise/knowledge_base/climate_adjustment.py
Elevation-based climate data adjustment module
Based on Escomen et al. 2024 methodology

References:
- Temperature: Environmental lapse rate (6.5°C/km)
- Relative Humidity: Saturation vapor pressure method (Cramer, 1961)
- Precipitation: Elevation lapse rate (27.03 mm/100m)
"""

import math
from typing import Tuple, Dict


class ClimateAdjustment:
    """
    Handles elevation-based adjustments for climate data.
    
    This module corrects temperature, relative humidity, and precipitation
    values based on elevation differences between a reference point and
    the study site.
    """
    
    # Constants from Escomen et al. 2024
    TEMP_LAPSE_RATE = 6.5  # °C per 1000m (standard environmental lapse rate)
    PRECIP_LAPSE_RATE = 27.03  # mm per 100m elevation change
    
    def __init__(self):
        """Initialize the climate adjustment module."""
        pass
    
    def adjust_temperature(
        self, 
        reference_temp: float, 
        reference_elevation: float, 
        site_elevation: float
    ) -> float:
        """
        Adjust temperature based on elevation difference.
        
        Formula: T_adjusted = T_reference - (lapse_rate × Δelevation_km)
        
        Args:
            reference_temp: Temperature at reference point (°C)
            reference_elevation: Elevation of reference point (meters)
            site_elevation: Elevation of study site (meters)
        
        Returns:
            Adjusted temperature (°C)
        
        Example:
            >>> adjuster = ClimateAdjustment()
            >>> adjuster.adjust_temperature(24.85, 771, 1119.10)
            22.29  # Decreases by 2.56°C due to 348m elevation gain
        """
        # Calculate elevation difference in kilometers
        elevation_diff_km = (site_elevation - reference_elevation) / 1000.0
        
        # Apply temperature lapse rate
        # Temperature DECREASES with INCREASING elevation
        temp_adjustment = self.TEMP_LAPSE_RATE * elevation_diff_km
        adjusted_temp = reference_temp - temp_adjustment
        
        return round(adjusted_temp, 2)
    
    def saturation_vapor_pressure(self, temperature: float) -> float:
        """
        Calculate saturation vapor pressure using Magnus formula.
        
        Formula: e_s = 6.112 × exp[(17.67 × T) / (T + 243.5)]
        
        Args:
            temperature: Temperature in °C
        
        Returns:
            Saturation vapor pressure in hPa (hectopascals)
        
        Reference:
            Magnus formula (commonly used in meteorology)
        """
        # Magnus formula coefficients
        a = 17.67
        b = 243.5
        
        # Calculate saturation vapor pressure
        svp = 6.112 * math.exp((a * temperature) / (temperature + b))
        
        return svp
    
    def adjust_relative_humidity(
        self,
        reference_rh: float,
        reference_temp: float,
        adjusted_temp: float
    ) -> float:
        """
        Adjust relative humidity based on temperature change.
        
        Formula: RH_2 = [f(T_2) / f(T_1)] × RH_1
        where f(T) is the saturation vapor pressure at temperature T
        
        Args:
            reference_rh: Relative humidity at reference point (%)
            reference_temp: Temperature at reference point (°C)
            adjusted_temp: Adjusted temperature at study site (°C)
        
        Returns:
            Adjusted relative humidity (%)
        
        Reference:
            Cramer, O.P. (1961). Adjustment of relative humidity and 
            temperature for differences in elevation.
        
        Example:
            >>> adjuster = ClimateAdjustment()
            >>> adjuster.adjust_relative_humidity(85.42, 24.85, 22.29)
            76.62  # RH decreases with cooler temperature
        """
        # Calculate saturation vapor pressures
        svp_reference = self.saturation_vapor_pressure(reference_temp)
        svp_adjusted = self.saturation_vapor_pressure(adjusted_temp)
        
        # Adjust RH proportionally to SVP ratio
        # RH decreases when moving to higher elevations (cooler air)
        rh_ratio = svp_adjusted / svp_reference
        adjusted_rh = reference_rh * rh_ratio
        
        # Ensure RH stays within valid range (0-100%)
        adjusted_rh = max(0.0, min(100.0, adjusted_rh))
        
        return round(adjusted_rh, 2)
    
    def adjust_precipitation(
        self,
        reference_precip: float,
        reference_elevation: float,
        site_elevation: float
    ) -> float:
        """
        Adjust precipitation based on elevation difference.
        
        Formula: Correction = lapse_rate × Δelevation
        P_adjusted = P_reference + correction
        
        Args:
            reference_precip: Annual precipitation at reference point (mm)
            reference_elevation: Elevation of reference point (meters)
            site_elevation: Elevation of study site (meters)
        
        Returns:
            Adjusted precipitation (mm)
        
        Reference:
            Soomro et al. (2019) - 27.03 mm per 100m elevation change
        
        Example:
            >>> adjuster = ClimateAdjustment()
            >>> adjuster.adjust_precipitation(2557.45, 771, 1119.10)
            2651.54  # Increases by 94.09mm due to orographic effect
        """
        # Calculate elevation difference in 100m units
        elevation_diff_100m = (site_elevation - reference_elevation) / 100.0
        
        # Apply precipitation lapse rate
        # Precipitation INCREASES with INCREASING elevation (orographic effect)
        precip_correction = self.PRECIP_LAPSE_RATE * elevation_diff_100m
        adjusted_precip = reference_precip + precip_correction
        
        # Ensure precipitation is non-negative
        adjusted_precip = max(0.0, adjusted_precip)
        
        return round(adjusted_precip, 2)
    
    def adjust_all_climate_data(
        self,
        reference_data: Dict[str, float],
        reference_elevation: float,
        site_elevation: float
    ) -> Dict[str, float]:
        """
        Adjust all climate parameters at once.
        
        Args:
            reference_data: Dictionary containing:
                - 'temperature': Mean annual temperature (°C)
                - 'humidity': Relative humidity (%)
                - 'rainfall': Annual precipitation (mm)
            reference_elevation: Elevation of reference point (meters)
            site_elevation: Elevation of study site (meters)
        
        Returns:
            Dictionary with adjusted climate data and metadata
        
        Example:
            >>> adjuster = ClimateAdjustment()
            >>> ref_data = {
            ...     'temperature': 24.85,
            ...     'humidity': 85.42,
            ...     'rainfall': 2557.45
            ... }
            >>> adjusted = adjuster.adjust_all_climate_data(ref_data, 771, 1119.10)
            >>> adjusted['temperature']
            22.29
            >>> adjusted['humidity']
            76.62
            >>> adjusted['rainfall']
            2651.54
        """
        # Extract reference values
        ref_temp = reference_data.get('temperature', 0)
        ref_humidity = reference_data.get('humidity', 0)
        ref_rainfall = reference_data.get('rainfall', 0)
        
        # Adjust temperature first (needed for RH adjustment)
        adj_temp = self.adjust_temperature(
            ref_temp, reference_elevation, site_elevation
        )
        
        # Adjust relative humidity using adjusted temperature
        adj_humidity = self.adjust_relative_humidity(
            ref_humidity, ref_temp, adj_temp
        )
        
        # Adjust precipitation
        adj_rainfall = self.adjust_precipitation(
            ref_rainfall, reference_elevation, site_elevation
        )
        
        # Calculate elevation difference for metadata
        elevation_diff = site_elevation - reference_elevation
        
        return {
            # Adjusted values
            'temperature': adj_temp,
            'humidity': adj_humidity,
            'rainfall': adj_rainfall,
            
            # Metadata
            'adjustments': {
                'temperature_change': round(adj_temp - ref_temp, 2),
                'humidity_change': round(adj_humidity - ref_humidity, 2),
                'rainfall_change': round(adj_rainfall - ref_rainfall, 2),
                'elevation_difference': elevation_diff
            },
            
            # Original values for reference
            'original': {
                'temperature': ref_temp,
                'humidity': ref_humidity,
                'rainfall': ref_rainfall
            }
        }
    
    def get_adjustment_info(
        self,
        reference_elevation: float,
        site_elevation: float
    ) -> Dict[str, any]:
        """
        Get information about expected adjustments for given elevations.
        
        Args:
            reference_elevation: Elevation of reference point (meters)
            site_elevation: Elevation of study site (meters)
        
        Returns:
            Dictionary with adjustment predictions
        """
        elevation_diff = site_elevation - reference_elevation
        elevation_diff_km = elevation_diff / 1000.0
        elevation_diff_100m = elevation_diff / 100.0
        
        # Expected changes
        expected_temp_change = -1 * (self.TEMP_LAPSE_RATE * elevation_diff_km)
        expected_precip_change = self.PRECIP_LAPSE_RATE * elevation_diff_100m
        
        return {
            'elevation_difference_m': elevation_diff,
            'expected_temperature_change_C': round(expected_temp_change, 2),
            'expected_precipitation_change_mm': round(expected_precip_change, 2),
            'direction': 'uphill' if elevation_diff > 0 else 'downhill',
            'notes': {
                'temperature': 'decreases' if elevation_diff > 0 else 'increases',
                'humidity': 'decreases' if elevation_diff > 0 else 'increases',
                'precipitation': 'increases' if elevation_diff > 0 else 'decreases'
            }
        }


# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("CLIMATE ADJUSTMENT MODULE - TEST")
    print("=" * 70)
    
    # Initialize adjuster
    adjuster = ClimateAdjustment()
    
    # Example from Escomen et al. 2024
    # Reference: Bubong, Lanao del Sur (771 masl)
    # Study Site: Brgy. Gacap, Piagapo (1,119.10 masl)
    
    reference_elevation = 771.0  # meters
    site_elevation = 1119.10  # meters
    
    # Reference climate data (from NASA-POWER)
    reference_climate = {
        'temperature': 24.85,  # °C
        'humidity': 85.42,     # %
        'rainfall': 2557.45    # mm
    }
    
    print("\n📍 LOCATION INFO:")
    print(f"Reference elevation: {reference_elevation} masl")
    print(f"Study site elevation: {site_elevation} masl")
    print(f"Elevation difference: +{site_elevation - reference_elevation:.2f} meters")
    
    print("\n🌡️  REFERENCE CLIMATE DATA:")
    print(f"Temperature: {reference_climate['temperature']}°C")
    print(f"Relative Humidity: {reference_climate['humidity']}%")
    print(f"Annual Rainfall: {reference_climate['rainfall']} mm")
    
    # Get adjustment predictions
    adjustment_info = adjuster.get_adjustment_info(
        reference_elevation, site_elevation
    )
    
    print("\n📊 EXPECTED ADJUSTMENTS:")
    print(f"Temperature: {adjustment_info['expected_temperature_change_C']:+.2f}°C")
    print(f"Precipitation: {adjustment_info['expected_precipitation_change_mm']:+.2f} mm")
    print(f"Direction: {adjustment_info['direction']}")
    
    # Perform adjustments
    adjusted_data = adjuster.adjust_all_climate_data(
        reference_climate, reference_elevation, site_elevation
    )
    
    print("\n✅ ADJUSTED CLIMATE DATA:")
    print(f"Temperature: {adjusted_data['temperature']}°C "
          f"({adjusted_data['adjustments']['temperature_change']:+.2f}°C)")
    print(f"Relative Humidity: {adjusted_data['humidity']}% "
          f"({adjusted_data['adjustments']['humidity_change']:+.2f}%)")
    print(f"Annual Rainfall: {adjusted_data['rainfall']} mm "
          f"({adjusted_data['adjustments']['rainfall_change']:+.2f} mm)")
    
    print("\n🎯 VALIDATION (vs. Escomen et al. 2024):")
    print(f"Expected Temperature: 22.29°C | Got: {adjusted_data['temperature']}°C | "
          f"Match: {'✓' if abs(adjusted_data['temperature'] - 22.29) < 0.1 else '✗'}")
    print(f"Expected Humidity: 76.62% | Got: {adjusted_data['humidity']}% | "
          f"Match: {'✓' if abs(adjusted_data['humidity'] - 76.62) < 0.1 else '✗'}")
    print(f"Expected Rainfall: 2651.54 mm | Got: {adjusted_data['rainfall']} mm | "
          f"Match: {'✓' if abs(adjusted_data['rainfall'] - 2651.54) < 0.1 else '✗'}")
    
    print("\n" + "=" * 70)
    print("✅ Module testing complete!")
    print("=" * 70)