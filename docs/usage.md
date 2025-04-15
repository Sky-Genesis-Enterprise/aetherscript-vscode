# Using ArgusScript

This guide explains how to use the ArgusScript language and interpreter.

## Installation

The ArgusScript interpreter is written in Python. To use it, you'll need Python 3.7 or later.

1. Clone the ArgusScript repository:
   ```bash
   git clone https://github.com/yourusername/argusscript.git
   cd argusscript
   ```

2. Make sure the command-line tool is executable:
   ```bash
   chmod +x src/argusscript.py
   ```

3. Create a symbolic link for easier access (optional):
   ```bash
   sudo ln -s "$(pwd)/src/argusscript.py" /usr/local/bin/argusscript
   ```

## Running ArgusScript Programs

### Command-Line Interface

The ArgusScript interpreter provides a command-line interface for running `.argus` files:

```bash
# Run an ArgusScript file
python src/argusscript.py examples/demo.argus

# Check a file for errors without executing it
python src/argusscript.py --check examples/demo.argus

# Specify an output file for UI HTML
python src/argusscript.py examples/demo.argus --output demo.html

# Start an interactive REPL session
python src/argusscript.py --repl
```

If you created the symbolic link, you can use the shorter form:

```bash
argusscript examples/demo.argus
```

### REPL (Interactive Shell)

The REPL provides an interactive environment for experimenting with ArgusScript:

```bash
python src/argusscript.py --repl
```

In the REPL, you can:
- Enter expressions or statements to evaluate them
- Use `show_ui()` to render any UI components to `repl_output.html`
- Type `exit()` or press Ctrl+D to exit

## Language Features

### Variables and Constants

```argus
// Variable declaration with type inference
let x = 10
let name = "John"

// Constant declaration (immutable)
const PI = 3.14159

// Explicit type annotation
let count: Int = 5
let message: String = "Hello"
```

### Functions

```argus
// Basic function
fn add(a: Int, b: Int) -> Int {
    return a + b
}

// Function with default parameters
fn greet(name: String = "World") -> String {
    return f"Hello, {name}!"
}

// Function call
let result = add(5, 3)
let greeting = greet()  // Uses default "World"
let customGreeting = greet("ArgusScript")
```

### Control Flow

```argus
// If-elif-else statement
if (x > 10) {
    print("x is greater than 10")
} elif (x < 5) {
    print("x is less than 5")
} else {
    print("x is between 5 and 10")
}

// For loop
for item in items {
    print(item)
}

// While loop
while (condition) {
    // Do something
}
```

### Data Structures

```argus
// Arrays
let numbers = [1, 2, 3, 4, 5]
let first = numbers[0]

// Objects
let person = {
    name: "John",
    age: 30,
    city: "New York"
}
let age = person.age
```

### Lambda Functions

```argus
// Lambda function (anonymous function)
let multiply = (a: Int, b: Int) => a * b
let result = multiply(2, 3)  // 6

// Lambda with block body
let complex = (x: Int) => {
    let y = x * 2
    return y + 10
}
```

### UI Components

One of ArgusScript's distinctive features is the ability to define UI components directly in the language:

```argus
ui {
    div(class="container") {
        h1("Hello, ArgusScript!")
        p("This is a paragraph.")

        button(id="btn", class="primary", onClick=handleClick) {
            "Click me"
        }
    }
}
```

### Styling

Style blocks allow you to define CSS-like styles directly in your code:

```argus
style {
    .container {
        max-width: 800px
        margin: 0 auto
        padding: 2rem
    }

    h1 {
        color: #3498db
    }

    .primary {
        background-color: #3498db
        color: white
        padding: 0.5rem 1rem
        border: none
        border-radius: 0.25rem
    }
}
```

### String Interpolation

ArgusScript supports string interpolation using the `f` prefix:

```argus
let name = "John"
let age = 30
let message = f"Hello, {name}! You are {age} years old."
```

## Feature Roadmap

The current implementation of ArgusScript is a prototype that demonstrates the language's core concepts. Future development will include:

1. **Enhanced Type System**: Generics, unions, and more sophisticated type inference
2. **Concurrency Improvements**: Full async/await support, goroutine scheduling
3. **Package Management**: Imports from external modules and packages
4. **UI Enhancements**: State management, component lifecycle, and event systems
5. **Compiler Optimization**: Performance improvements and code generation
6. **Standard Library**: Expanding the built-in functionality
7. **Developer Tools**: Language server for IDE integration, debugger, and more

## Contributing

Contributions to ArgusScript are welcome! See the GitHub repository for more information on how to contribute.

## License

ArgusScript is available under the MIT license.
