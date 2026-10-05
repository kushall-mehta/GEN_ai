def calculate_bmi(height, weight):
    height_m = height / 100
    bmi = weight / (height_m ** 2)

    return round(bmi, 2)


def bmi_node(state):
    bmi = calculate_bmi(
        state["height"],
        state["weight"]
    )
    return {
        "response": f"Your BMI is {bmi}"
    }
