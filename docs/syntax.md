# ArgusScript Syntax Specification

This document outlines the syntax and grammar for the ArgusScript programming language.

## 1. Lexical Elements

### Comments
```argus
// Single-line comment

/*
   Multi-line comment
*/
```

### Identifiers
Identifiers must start with a letter or underscore, followed by any combination of letters, digits, or underscores.
```
identifier = [a-zA-Z_][a-zA-Z0-9_]*
```

### Keywords
```
let         const       fn          return      if          else
elif        for         in          while       break       continue
match       case        default     import      from        as
type        interface   impl        pub         priv        async
await       try         catch       throw       ui          style
```

### Literals
```argus
// Numeric literals
123         // integer
123.456     // float
0x1A        // hexadecimal
0b1010      // binary
1_000_000   // with underscores for readability

// String literals
"Hello, world!"           // regular string
'Hello'                   // alternative string
`Multiline                // template string
 string`
f"Hello, {name}!"         // formatted string

// Boolean literals
true
false

// Null/None literal
none

// Array literals
[1, 2, 3]

// Object/Map literals
{name: "John", age: 30}
```

## 2. Basic Grammar

### Variable Declarations
```argus
// Type inference
let name = "John"
const PI = 3.14159

// Explicit typing
let age: Int = 30
let items: [String] = ["apple", "banana"]
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

// Anonymous function/lambda
let multiply = (a: Int, b: Int) -> Int => a * b

// Async function
async fn fetchData(url: String) -> Response {
  return await http.get(url)
}
```

### Control Flow
```argus
// If-else statement
if condition {
  // code
} elif another_condition {
  // code
} else {
  // code
}

// Match statement (pattern matching)
match value {
  case 1 => "one"
  case 2 => "two"
  case n if n > 10 => "many"
  case _ => "other"
}

// Loops
for item in items {
  // code
}

while condition {
  // code
}

for i in 0..10 {
  // code
}
```

### Error Handling
```argus
try {
  // code that might throw
} catch e: Error {
  // handle error
}

// Result type for functional error handling
let result = operation()
match result {
  case .ok(value) => use(value)
  case .err(error) => handle(error)
}
```

## 3. Types

```argus
// Basic types
type Person {
  name: String
  age: Int
  email: String?  // Optional type
}

// Generic types
type Box<T> {
  value: T
}

// Union types
type NumberOrString = Int | String

// Interfaces
interface Printable {
  fn print() -> String
}

// Implementation
impl Printable for Person {
  fn print() -> String {
    return f"Person(name={this.name}, age={this.age})"
  }
}
```

## 4. Modules and Imports

```argus
// Importing from standard library
import { http, json } from "std"

// Importing from other modules
import { User } from "./models"
import * as utils from "./utils"

// Exporting
pub fn exposed_function() {
  // code
}

priv fn internal_function() {
  // code
}
```

## 5. Concurrency

```argus
// Goroutine-like concurrency
go function()

// Channels
let ch = chan<Int>()
ch <- 5       // send value
let x = <-ch  // receive value

// Async/await
async fn process() {
  let result = await fetchData()
  return transform(result)
}
```

## 6. UI Components

The UI components are one of ArgusScript's most distinctive features, embedding HTML/CSS-like functionality directly in the language.

```argus
fn Button(text: String, onClick: fn()) {
  ui {
    button(class="primary-btn", onClick=onClick) {
      text
    }
  }

  style {
    .primary-btn {
      background: #3498db
      color: white
      padding: 0.5rem 1rem
      border-radius: 0.25rem
      border: none
      cursor: pointer
    }

    .primary-btn:hover {
      background: #2980b9
    }
  }
}

fn App() {
  let count = 0

  fn increment() {
    count += 1
  }

  ui {
    div(class="app") {
      h1("Counter App")
      p(f"Count: {count}")
      Button("Increment", onClick=increment)
    }
  }

  style {
    .app {
      max-width: 500px
      margin: 0 auto
      padding: 2rem
      font-family: sans-serif
    }
  }
}
```

## 7. Grammar (in BNF-like notation)

```
program        ::= statement*

statement      ::= var_decl | func_decl | type_decl | import_stmt | expr_stmt | control_flow

var_decl       ::= ('let' | 'const') IDENTIFIER [':' type] '=' expr

func_decl      ::= ['async'] 'fn' IDENTIFIER '(' [param_list] ')' ['->' type] block

param_list     ::= param (',' param)*
param          ::= IDENTIFIER ':' type ['=' expr]

type_decl      ::= 'type' IDENTIFIER [generic_params] '{' field_list '}'
                 | 'interface' IDENTIFIER [generic_params] '{' method_list '}'
                 | 'impl' IDENTIFIER 'for' IDENTIFIER '{' func_decl* '}'

field_list     ::= (IDENTIFIER ':' type ','?)*
method_list    ::= (func_decl ','?)*

import_stmt    ::= 'import' ('{' IDENTIFIER (',' IDENTIFIER)* '}' | '*' 'as' IDENTIFIER) 'from' STRING_LITERAL

expr_stmt      ::= expr ';'?

control_flow   ::= if_stmt | for_stmt | while_stmt | match_stmt | return_stmt

if_stmt        ::= 'if' expr block ('elif' expr block)* ['else' block]

for_stmt       ::= 'for' IDENTIFIER 'in' expr block

while_stmt     ::= 'while' expr block

match_stmt     ::= 'match' expr '{' (case_clause)* '}'
case_clause    ::= 'case' pattern [guard] '=>' (expr | block)
guard          ::= 'if' expr

return_stmt    ::= 'return' [expr]

ui_block       ::= 'ui' '{' ui_element* '}'
ui_element     ::= IDENTIFIER ['(' attr_list ')'] ['{' (ui_element | expr)* '}']
attr_list      ::= (IDENTIFIER '=' expr ','?)*

style_block    ::= 'style' '{' style_rule* '}'
style_rule     ::= selector '{' style_decl* '}'
selector       ::= IDENTIFIER | '.' IDENTIFIER | '#' IDENTIFIER | (selector '+' selector) | (selector '>' selector)
style_decl     ::= IDENTIFIER ':' (STRING_LITERAL | NUMBER | IDENTIFIER) ','?

type           ::= basic_type | array_type | optional_type | union_type | func_type
basic_type     ::= IDENTIFIER [generic_args]
array_type     ::= '[' type ']'
optional_type  ::= type '?'
union_type     ::= type '|' type
func_type      ::= '(' [type (',' type)*] ')' '->' type

generic_params ::= '<' IDENTIFIER (',' IDENTIFIER)* '>'
generic_args   ::= '<' type (',' type)* '>'

expr           ::= literal | unary_expr | binary_expr | call_expr | index_expr | member_expr | lambda_expr | ui_expr
literal        ::= NUMBER | STRING_LITERAL | BOOLEAN | 'none' | array_literal | object_literal
array_literal  ::= '[' [expr (',' expr)*] ']'
object_literal ::= '{' [IDENTIFIER ':' expr (',' IDENTIFIER ':' expr)*] '}'
unary_expr     ::= ('-' | '!' | 'await') expr
binary_expr    ::= expr operator expr
operator       ::= '+' | '-' | '*' | '/' | '%' | '==' | '!=' | '<' | '>' | '<=' | '>=' | '&&' | '||'
call_expr      ::= expr '(' [expr (',' expr)*] ')'
index_expr     ::= expr '[' expr ']'
member_expr    ::= expr '.' IDENTIFIER
lambda_expr    ::= ['async'] '(' [param_list] ')' ['->' type] '=>' (expr | block)
ui_expr        ::= ui_block [style_block]

block          ::= '{' statement* '}'
```

## 8. Standard Library

ArgusScript will include a comprehensive standard library that covers functionality from Python, Go, and HTML/CSS:

- **Core**: Basic types, functions, and utilities
- **IO**: File and stream operations
- **HTTP**: Client and server implementations
- **Database**: SQL and NoSQL database connectors
- **Concurrency**: Goroutines, channels, mutex, etc.
- **UI**: Built-in UI components and styling primitives
- **Math**: Mathematical functions and operations
- **Data**: Data processing, manipulation, and analysis
- **Net**: Networking and socket programming
- **Crypto**: Cryptography and security
- **Time**: Date and time handling
- **Regex**: Regular expression support
- **JSON/XML**: Data format handling
- **OS**: Operating system interaction
- **Testing**: Unit testing framework
