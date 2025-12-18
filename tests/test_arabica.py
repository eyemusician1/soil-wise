"""
Test script to verify the corrected LSI calculation
Expected result for Arabica Coffee: LSI = 7.42, Classification = Ns
"""

import math

def test_arabica_coffee():
    print("="*80)
    print("ARABICA COFFEE - CORRECTED CALCULATION TEST")
    print("="*80)
    
    # Your parameter ratings
    parameters = {
        'rainfall': (1300, 0.95),
        'temperature': (24.87, 0.60),
        'humidity': (73, 0.85),
        'slope': (3.29, 0.95),
        'flooding': ('Fo', 1.0),
        'drainage': ('Good', 1.0),
        'texture': ('SiC', 0.25),
        'coarse_fragment': (3, 1.0),
        'soil_depth': (135, 0.85),
        'caco3': (0, 1.0),
        'caso4': (0, 1.0),
        'cec': (28, 1.0),
        'sum_basic_cations': (14, 1.0),
        'ph': (6.40, 0.95),
        'base_saturation': (50, 0.95),
        'organic_carbon': (3.5, 1.0),
        'ec': (0, 1.0),
        'esp': (2.8, 1.0)
    }
    
    print("\nParameter Ratings:")
    print(f"{'Parameter':<25} {'Value':<15} {'Rating':<10}")
    print("-"*50)
    
    ratings = []
    for param, (value, rating) in parameters.items():
        print(f"{param:<25} {str(value):<15} {rating:<10.2f}")
        ratings.append(rating)
    
    print("-"*50)
    print(f"Total parameters: {len(ratings)}")
    
    # Find Rmin
    rmin = min(ratings)
    print(f"\nStep 1: Rmin = {rmin:.4f} (Texture - Silty Clay)")
    
    # Calculate product of ALL ratings
    product = math.prod(ratings)
    print(f"\nStep 2: Product of ALL ratings = {product:.10f}")
    
    # Calculate square root
    sqrt_product = math.sqrt(product)
    print(f"\nStep 3: √(product) = {sqrt_product:.10f}")
    
    # Calculate LSI
    lsi = rmin * sqrt_product * 100
    print(f"\nStep 4: LSI = Rmin × √(product) × 100")
    print(f"        LSI = {rmin} × {sqrt_product:.10f} × 100")
    print(f"        LSI = {lsi:.10f}")
    print(f"        LSI (rounded) = {round(lsi, 2)}")
    
    # Classify
    if lsi >= 75:
        classification = "S1"
    elif lsi >= 50:
        classification = "S2"
    elif lsi >= 25:
        classification = "S3"
    else:
        classification = "N"
    
    # Identify limiting factors
    limiting = "s"  # Texture is the limiting factor (physical soil)
    full_classification = f"{classification}{limiting}"
    
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"Calculated LSI: {round(lsi, 2)}")
    print(f"Expected LSI:   7.42")
    print(f"Match: {'✓ YES' if abs(round(lsi, 2) - 7.42) < 0.01 else '✗ NO'}")
    print(f"\nFull Classification: {full_classification}")
    print(f"Expected:            Ns")
    print(f"Match: {'✓ YES' if full_classification == 'Ns' else '✗ NO'}")
    print("="*80)

if __name__ == "__main__":
    test_arabica_coffee()
