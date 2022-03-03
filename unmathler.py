from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import keyboard

# Initialize Selenium
ser = Service("C:\\Program Files (x86)\chromedriver.exe")
op = webdriver.ChromeOptions()
browser = webdriver.Chrome(service=ser, options=op)

# Generate potential equations
def generate_equations(target_value, equation, potential_equations):
    natural = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    integer = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    operators = ['+', '-', '*', '/']
    if len(equation) == 0:
        for character in natural:
            equation += str(character)
            potential_equations = generate_equations(target_value, equation, potential_equations)
            equation = ""
    elif len(equation) == 5 and equation.isnumeric() and int(equation) >= 10000:
        return potential_equations
    elif len(equation) == 6:
        if equation[len(equation) - 1] in operators:
            return potential_equations
        elif eval(equation) == target_value:
            potential_equations.append(equation)
        return potential_equations
    elif equation[len(equation) - 1].isnumeric():
        for character in integer + operators:
            equation += str(character)
            potential_equations = generate_equations(target_value, equation, potential_equations)
            equation = equation[0:len(equation) - 1]
    elif equation[len(equation) - 1] in operators:
        for character in natural:
            equation += str(character)
            potential_equations = generate_equations(target_value, equation, potential_equations)
            equation = equation[0:len(equation) - 1]
    return potential_equations

# Score and select equation
def score_and_select(potential_equations):
    unique = True
    tmp = []
    for equation in potential_equations:
        for i in range(len(equation)):
            for j in range(i + 1, len(equation)):
                if equation[i] == equation[j]:
                    unique = False
        if unique:
            tmp.append(equation)
        unique = True
    if len(tmp) > 0:
        return tmp[0]
    else:
        return potential_equations[0]

# Enter guess
def enter_guess(equation):
    for character in equation:
        path = "//button[text()='" + character + "']"
        browser.find_element(By.XPATH, path).click()
    keyboard.press_and_release('enter')

# Evaluate guess
def evaluate_guess(guess_number):
    evaluation = []
    tiles = browser.find_elements(By.XPATH, "//div[contains(@class, 'w-14')]")
    for i in range(guess_number * 6, (guess_number * 6) + 6):
        if "green" in tiles[i].get_attribute('class'):
            evaluation.append(2)
        elif "yellow" in tiles[i].get_attribute('class'):
            evaluation.append(1)
        else:
            evaluation.append(0)
    return evaluation

# Trim down potential solutions
def trim_list_of_guesses(potential_equations, selected_equation, evaluation):
    for i in range(6):
        if evaluation[i] == 0:
            remove = True
            occurrences = find(selected_equation, selected_equation[i])
            occurrences.remove(i)
            if len(occurrences) > 0:
                for occurrence in occurrences:
                    if evaluation[occurrence] == 1 or evaluation[occurrence] == 2:
                        remove = False
            if remove:
                for equation in list(potential_equations):
                    if selected_equation[i] in equation:
                        potential_equations.remove(equation)
        elif evaluation[i] == 1:
            for equation in list(potential_equations):
                if selected_equation[i] not in equation or selected_equation[i] == equation[i]:
                    potential_equations.remove(equation)
        else:
            for equation in list(potential_equations):
                if selected_equation[i] != equation[i]:
                    potential_equations.remove(equation)
    return potential_equations

# Return list of occurrences of a character in a string
def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

# Solve Mathler
def unmathler():
    # Set up Selenium browser
    browser.get("https://www.mathler.com")

    # Start program when escape key is pressed
    keyboard.wait('esc')
    print("Running...")

    # Identify target value
    target_value_row = browser.find_element(By.TAG_NAME, 'h2').text
    target_value = int(target_value_row.partition("equals")[2].strip())

    # Generate potential equations
    potential_equations = []
    equation = ""
    potential_equations = generate_equations(target_value, equation, potential_equations)

    # Score and select equation
    equation = score_and_select(potential_equations)

    # Initialize counters
    guess_number = 0

    # Iterate for six attempts
    while guess_number < 5:

        # Enter guess
        enter_guess(equation)

        # Evaluate guess
        evaluation = evaluate_guess(guess_number)

        # Check if Mathler has been solved
        if sum(evaluation) == 12:
            print("Solved in {} attempts!".format(guess_number + 1))
            return

        # Trim down potential solutions
        potential_equations = trim_list_of_guesses(potential_equations, equation, evaluation)

        # Select next guess
        equation = score_and_select(potential_equations)

        # Increment guess number
        guess_number = guess_number + 1

    # Admit failure
    if guess_number == 5:
        print("Could not guess in six attempts!")

if __name__ == '__main__':
    unmathler()