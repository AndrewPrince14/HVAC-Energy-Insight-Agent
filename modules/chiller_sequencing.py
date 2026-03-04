import numpy as np

def run_chiller_sequencing(predicted_peak, predicted_avg):
    """
    Simple 3-chiller sequencing logic based on predicted cooling load.
    """

    print("\n--- Chiller Sequencing Plan ---")

    # Assume each chiller capacity
    chiller_capacity = 400  # kWh equivalent cooling load

    # Determine required chillers
    if predicted_peak < chiller_capacity:
        chillers_required = 1
    elif predicted_peak < chiller_capacity * 2:
        chillers_required = 2
    else:
        chillers_required = 3

    # Efficiency assumption
    base_cop = 5.0

    # Estimated COP improvement when properly sequenced
    optimized_cop = base_cop + (0.1 * chillers_required)

    print(f"Predicted Cooling Load Peak: {round(predicted_peak,2)} kWh")
    print(f"Chillers Required: {chillers_required}")
    print(f"Estimated Optimized COP: {round(optimized_cop,2)}")

    sequencing_plan = {
        "chillers_required": chillers_required,
        "optimized_cop": optimized_cop
    }

    return sequencing_plan