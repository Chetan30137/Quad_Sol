import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from fractions import Fraction


# readable fraction, if it's not a fraction then it's just a normal number
def input_fraction_or_decimal(prompt):
    value = input(prompt)
    try:
        return float(Fraction(value))
    except ValueError:
        return float(value)


# Math for the standard form (god I hated this)
def standard_form(a, b, c):
    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        return "No real solutions."
    elif discriminant == 0:
        x = -b / (2 * a)
        return f"One real solution: x = {x}"
    else:
        x1 = (-b + math.sqrt(discriminant)) / (2 * a)
        x2 = (-b - math.sqrt(discriminant)) / (2 * a)
        return f"Two real solutions: x1 = {x1}, x2 = {x2}"

# think I studied factored and vertex form more then standard lol ezpz
def factored_form(a, r, s):
    x1 = -r
    x2 = -s
    return a, -a * (r + s), a * r * s

def vertex_form(a, h, k):
    return a, -2 * a * h, a * h ** 2 + k


# used data from quadratic formula weeeeeeeeeeeeeee
def plot_quadratic(a, b, c, x_limit, y_limit):
    x = np.linspace(-x_limit, x_limit, 400)
    y = a * x ** 2 + b * x + c

    plt.plot(x, y)
    plt.axhline(0, color='black', lw=1)
    plt.axvline(0, color='black', lw=1)
    plt.title("Quadratic Equation")
    plt.xlabel("x")
    plt.ylabel("y")

# felt proud of this one, able to let the user set the x and y limits lol
    plt.xticks(np.arange(-x_limit, x_limit + 1, 1))
    plt.yticks(np.arange(-y_limit, y_limit + 1, 1))

    plt.xlim(-x_limit, x_limit)
    plt.ylim(-y_limit, y_limit)

    # Plot integer points
    for x_int in range(-x_limit, x_limit + 1):
        y_int = a * x_int ** 2 + b * x_int + c
        if y_int.is_integer():
            plt.scatter(x_int, y_int, color='red', marker='o')

    plt.grid(True)
    plt.show()

    # Plot integer points because why not
    for x_int in range(-10, 11):
        y_int = a * x_int**2 + b * x_int + c
        if y_int.is_integer():
            plt.scatter(x_int, y_int, color='red', marker='o')

    plt.grid(True)
    plt.show()


# Prompting user to choose what calculator to use
def main():
    print("Quadratic Formula Calculator")
    print("1. Standard form (ax^2 + bx + c)")
    print("2. Factored form (a(x - r)(x - s))")
    print("3. Vertex form (a(x - h)^2 + k)")

    choice = int(input("Enter the number of the form you want to use: "))

    x_limit = int(input("Enter the x-axis limit (integer): "))
    y_limit = int(input("Enter the y-axis limit (integer): "))


    if choice == 1:
        a = input_fraction_or_decimal("Enter a: ")
        b = input_fraction_or_decimal("Enter b: ")
        c = input_fraction_or_decimal("Enter c: ")
        result = standard_form(a, b, c)
    elif choice == 2:
        a = input_fraction_or_decimal("Enter a: ")
        r = input_fraction_or_decimal("Enter r: ")
        s = input_fraction_or_decimal("Enter s: ")
        a, b, c = factored_form(a, r, s)
        result = standard_form(a, b, c)
    elif choice == 3:
        a = input_fraction_or_decimal("Enter a: ")
        h = input_fraction_or_decimal("Enter h: ")
        k = input_fraction_or_decimal("Enter k: ")
        a, b, c = vertex_form(a, h, k)
        result = standard_form(a, b, c)
    else:
        result = "Invalid choice."

    print(result)

    plot_quadratic(a, b, c, x_limit, y_limit)
if __name__ == "__main__":
    main()