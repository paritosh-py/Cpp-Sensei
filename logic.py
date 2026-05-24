import re
from typing import Optional, Tuple, List

class SenseiLogic:
    def __init__(self):
        # The order matters! Specific rules should generally come before generic ones.
        self.rules = [
            # ==============================================================================
            # GROUP 1: PREPROCESSOR & HEADERS
            # ==============================================================================
            (r'#include\s*<bits/stdc\+\+\.h>',
             "COMPETITIVE CODING HEADER: Importing absolutely everything in C++.",
             "CONCEPT: This is a 'convenience header' often used in competitive programming. It includes every standard library file (vectors, strings, algorithms, IO, etc.) in one go. \n\nPROS: You don't have to remember specific includes. \nCONS: It increases compile time significantly and isn't standard in all compilers. Avoid this in professional software engineering.",
             "https://en.cppreference.com/w/cpp/header"),

            # Fix: Ensure <iostream> is captured. Using ([^>]+) to capture text inside <>
            (r'#include\s*<([^>]+)>',
             "HEADER IMPORT: Fetching the toolset <{}>.",
             "CONCEPT: Think of this like opening a toolbox. C++ is lean; it doesn't load everything by default. <iostream> gives you input/output tools, <vector> gives you dynamic arrays, and <algorithm> gives you sorting/searching functions. The preprocessor literally copies that file into your code before compiling.",
             "https://en.cppreference.com/w/cpp/header"),

            (r'using\s+namespace\s+std;',
             "NAMESPACE DIRECTIVE: Unlocking the 'std' label.",
             "CONCEPT: Without this, you have to type 'std::cout' or 'std::vector'. This line tells the compiler, 'If you don't recognize a name, check the standard (std) library.' \n\nWARNING: In large projects, this is dangerous because if you name a variable 'count', it might clash with 'std::count'.",
             "https://en.cppreference.com/w/cpp/language/namespace"),

            # ==============================================================================
            # GROUP 2B: ARRAYS (Must come BEFORE standard variables to prevent misclassification)
            # ==============================================================================
            # Rule for: char str[] = "Hello";
            (r'char\s+(\w+)\[\]\s*=\s*"(.*)"\s*;',
             "C-STYLE STRING: A character array initialized with text '{1}'.",
             "DETAILED: In C++, a string literal like \"{1}\" is actually an array of characters ending with a special 'null terminator' (\\0). This is the old C way of handling text.",
             "https://en.cppreference.com/w/cpp/language/string_literal"),

            # Rule for: int arr[5]; OR int arr[5] = {1,2};
            # Removing strict semi-colon check to allow initialization lines
            # Groups: 0:Type, 1:Name, 2:Size
            (r'(\w+)\s+(\w+)\[(\d+)\]',
             "ARRAY DECLARATION: Creating a fixed-size list named '{1}' that holds {2} items of type '{0}'.",
             "DETAILED: An array is a collection of items stored in contiguous memory. Once you set the size (here, {2}), it cannot be changed. All items in the array must be of the same type.",
             "https://en.cppreference.com/w/cpp/language/array"),

            # Rule for: int arr[] = {1, 2, 3};
            # Groups: 0:Type, 1:Name, 2:Content
            (r'(\w+)\s+(\w+)\[\]\s*=\s*\{(.*)\}',
             "ARRAY INITIALIZATION: Creating an array '{1}' and filling it with: {{ {2} }}.",
             "DETAILED: When you initialize an array with {{ }}, C++ automatically counts the items to determine the array's size for you.",
             "https://en.cppreference.com/w/cpp/language/array#Initialization"),

            # Rule for: arr[0] = 10; or cout << arr[i];
            # Groups: 0:Name, 1:Index
            (r'(\w+)\[(.*)\]',
             "ARRAY ACCESS: Accessing the item at position (index) '{1}' in array '{0}'.",
             "DETAILED: C++ uses **Zero-Based Indexing**. This means the first element is at [0], the second at [1], and so on. Be careful: accessing an index outside the array size will crash your program or cause 'Undefined Behavior'.",
             "https://en.cppreference.com/w/cpp/language/array#Usage"),

            # ==============================================================================
            # GROUP 2: DATA TYPES & VARIABLES
            # ==============================================================================

            (r'\b(const)\s+',
             "CONSTANT: Making a value unchangeable.",
             "CONCEPT: 'const' is a promise that this variable will never change after it is created. It helps prevent bugs and lets the compiler optimize your code (e.g., putting it in read-only memory).",
             "https://en.cppreference.com/w/cpp/language/cv"),

            # Group 0: Type, Group 1: Name
            # Added (?!\s*\[) to ensure we don't match arrays as simple variables
            (r'\b(int|long long)\s+(\w+)(?!\s*\[)',
             "INTEGER DECLARATION: Creating a whole number variable '{1}' (type: {0}).",
             "CONCEPT: 'int' is the standard integer size (usually 32-bit, up to ~2 billion). Use 'long long' if you need massive numbers (64-bit, up to ~9 quintillion). If you try to store 2.5 inside an int, the .5 gets chopped off instantly.",
             "https://en.cppreference.com/w/cpp/language/types"),

            (r'\b(float|double)\s+(\w+)(?!\s*\[)',
             "DECIMAL DECLARATION: Creating a precise number variable '{1}' (type: {0}).",
             "CONCEPT: 'double' (double precision) is the standard for decimals. 'float' saves memory but is less precise. Be careful: computers can't store decimals perfectly (e.g., 0.1 + 0.2 might equal 0.300000004).",
             "https://en.cppreference.com/w/cpp/language/types"),

            (r'\b(char)\s+(\w+)(?!\s*\[)',
             "CHARACTER: Storing a single symbol '{1}'.",
             "CONCEPT: Computers only understand numbers. A 'char' actually stores a small integer (ASCII code) that represents a letter. For example, 'A' is stored as 65.",
             "https://en.cppreference.com/w/cpp/language/types"),

            (r'\b(bool)\s+(\w+)(?!\s*\[)',
             "BOOLEAN: A simple switch (True/False) named '{1}'.",
             "CONCEPT: The smallest unit of logic. Internally, C++ often treats 'false' as 0 and 'true' as 1 (or anything non-zero). Used heavily in 'if' statements.",
             "https://en.cppreference.com/w/cpp/language/types"),

            (r'\b(string)\s+(\w+)(?!\s*\[)',
             "STRING: A text variable '{1}'.",
             "CONCEPT: Unlike 'char' (which is one letter), 'string' is a dynamic chain of characters. It handles memory management for you, so you can resize it, add to it (+), or search inside it easily.",
             "https://en.cppreference.com/w/cpp/string/basic_string"),



            # ==============================================================================
            # GROUP 3: MEMORY (POINTERS, REFS, DYNAMIC)
            # ==============================================================================
            (r'(\w+)\s*\*\s*(\w+)\s*=',
             "POINTER DECLARATION: '{}' stores a memory address, not a value.",
             "CONCEPT: A pointer is a map coordinate. If 'int x = 10' is a house with 10 people, 'int* p = &x' is a piece of paper with the house's address written on it. You use pointers for dynamic memory and efficient array handling.",
             "https://en.cppreference.com/w/cpp/language/pointer"),

            (r'(\w+)\s*&\s*(\w+)\s*=',
             "REFERENCE: '{}' is an alias (nickname) for another variable.",
             "CONCEPT: A reference is NOT a copy. It is a permanent link to the original variable. If you change the reference, you change the original. It's safer and easier to read than pointers.",
             "https://en.cppreference.com/w/cpp/language/reference"),

            (r'new\s+(\w+)',
             "DYNAMIC ALLOCATION: Manually requesting memory on the Heap.",
             "CONCEPT: Standard variables live on the 'Stack' and die automatically. 'new' creates data on the 'Heap' that stays alive until you explicitly kill it. Use this for objects that need to survive across different functions.",
             "https://en.cppreference.com/w/cpp/language/new"),

            (r'delete\s+(\w+)',
             "MEMORY CLEANUP: Returning borrowed memory to the system.",
             "CONCEPT: C++ does not have a Garbage Collector. If you used 'new', you MUST use 'delete'. If you forget, your program will consume more and more RAM (a Memory Leak) until it crashes.",
             "https://en.cppreference.com/w/cpp/language/delete"),

            # ==============================================================================
            # GROUP 4: STL & DATA STRUCTURES
            # ==============================================================================
            (r'vector\s*<\s*(\w+)\s*>',
             "STL VECTOR: A dynamic, resizeable array of type '{0}'.",
             "CONCEPT: Standard arrays are fixed size. A vector is flexible. If it gets full, it automatically finds a larger memory space, copies itself over, and deletes the old one. It is the go-to list structure in C++.",
             "https://en.cppreference.com/w/cpp/container/vector"),

            # Groups: 0:KeyType, 1:ValueType
            (r'map\s*<\s*(\w+)\s*,\s*(\w+)\s*>',
             "STL MAP: A dictionary linking keys ({0}) to values ({1}).",
             "CONCEPT: Maps store pairs. You look up data by a 'Key' instead of an index. It's usually implemented as a Red-Black Tree, meaning lookups are very fast (O(log n)) and the data is always sorted by the Key.",
             "https://en.cppreference.com/w/cpp/container/map"),

            (r'set\s*<\s*(\w+)\s*>',
             "STL SET: A collection of unique '{0}' items.",
             "CONCEPT: Sets automatically sort your data and remove duplicates. If you try to insert the same number twice, the set ignores the second one. Great for filtering unique elements.",
             "https://en.cppreference.com/w/cpp/container/set"),

            (r'struct\s+(\w+)',
             "STRUCT DEFINITION: A simple data bundle '{0}'.",
             "CONCEPT: Structs are the precursors to Classes. By default, everything inside is 'public'. Use structs for passive data objects (like a Coordinate point with x, y) that don't have complex logic or privacy needs.",
             "https://en.cppreference.com/w/cpp/language/class"),

            # ==============================================================================
            # GROUP 5: CONTROL FLOW
            # ==============================================================================
            (r'if\s*\((.*)\)',
             "CONDITIONAL: Branching logic based on '{}'.",
             "CONCEPT: The gatekeeper. If the math inside () evaluates to True, we enter the gate. Note: In C++, '0' is False, and everything else is True.",
             "https://en.cppreference.com/w/cpp/language/if"),

            (r'else\s+if',
             "ALTERNATE CONDITION: Checking a secondary option.",
             "CONCEPT: Used when the first 'if' failed, but you still have specific criteria to check before giving up.",
             "https://en.cppreference.com/w/cpp/language/if"),

            (r'for\s*\((.*)\)',
             "FOR LOOP: Repeating code a specific number of times.",
             "CONCEPT: The standard loop. It has three parts: Initialization (start here), Condition (keep going while this is true), and Update (do this after every round).",
             "https://en.cppreference.com/w/cpp/language/for"),

            (r'while\s*\((.*)\)',
             "WHILE LOOP: Repeating code as long as '{}' is true.",
             "CONCEPT: Use this when you don't know how many times you need to loop (e.g., reading a file until the end). Caution: If the condition never becomes false, you get an Infinite Loop.",
             "https://en.cppreference.com/w/cpp/language/while"),

            (r'do\s*{',
             "DO-WHILE LOOP: Run once, then check the condition.",
             "CONCEPT: Unlike a standard 'while' loop, this guarantees the code inside runs AT LEAST once before checking if it should stop.",
             "https://en.cppreference.com/w/cpp/language/do"),

            (r'switch\s*\((.*)\)',
             "SWITCH STATEMENT: Jumping to a specific case for '{}'.",
             "CONCEPT: A cleaner alternative to many 'else if' statements when checking a single variable against fixed values. It jumps directly to the matching 'case'.",
             "https://en.cppreference.com/w/cpp/language/switch"),

            # ==============================================================================
            # GROUP 6: FUNCTIONS & I/O
            # ==============================================================================
            (r'cin\s*>>\s*(.*);',
             "INPUT: Reading user input into '{}'.",
             "CONCEPT: 'Console IN'. The '>>' arrows point to where the data is going (into the variable). It automatically detects spaces as separators.",
             "https://en.cppreference.com/w/cpp/io/cin"),

            (r'cout\s*<<\s*(.*);',
             "OUTPUT: Printing '{}' to the screen.",
             "CONCEPT: 'Console OUT'. The '<<' arrows point out of the program towards the screen. You can chain them: cout << name << age;",
             "https://en.cppreference.com/w/cpp/io/cout"),

            (r'void\s+(\w+)',
             "VOID FUNCTION: Action function '{}' (No result returned).",
             "CONCEPT: A 'void' function is a doer, not a calculator. It might print to the screen or save a file, but it doesn't give a number back to the code that called it.",
             "https://en.cppreference.com/w/cpp/language/functions"),

            (r'return\s+0;',
             "SUCCESS EXIT: Signaling that the program finished correctly.",
             "CONCEPT: In the main() function, returning 0 is the universal standard for 'No Errors'. The operating system reads this code.",
             "https://en.cppreference.com/w/cpp/language/return"),

             (r'return\s+1;',
             "ERROR EXIT: Signaling that something went wrong.",
             "CONCEPT: Non-zero return codes usually indicate an error state to the operating system or the script that ran this program.",
             "https://en.cppreference.com/w/cpp/language/return"),

            # ==============================================================================
            # GROUP 7: OOP PILLARS, CONSTRUCTORS & TEMPLATES
            # ==============================================================================
            (r'template\s*<\s*(typename|class)\s+(\w+)\s*>',
             "TEMPLATE DECLARATION: Making a generic structure with placeholder type '{1}'.",
             "CONCEPT: Templates enable generic programming in C++. It allows a class or function to operate with different data types without rewriting code for each one. The compiler generates concrete classes/functions behind the scenes.",
             "https://en.cppreference.com/w/cpp/language/templates"),

            (r'class\s+(\w+)',
             "CLASS: Blueprint for a complex object '{}'.",
             "CONCEPT: A Class bundles data (attributes) and logic (methods) together. It is the foundation of Object-Oriented Programming.",
             "https://en.cppreference.com/w/cpp/language/class"),

            (r'public:',
             "ACCESS MODIFIER: Opening access to everyone.",
             "CONCEPT: Public members are the 'Interface'. Anyone outside the class can see and use these functions.",
             "https://en.cppreference.com/w/cpp/language/access_specifiers"),

            (r'private:',
             "ACCESS MODIFIER: Restricting access to internal logic.",
             "CONCEPT: ENCAPSULATION. Private members are secrets. Only the class itself can touch them. This prevents external code from breaking the internal state of the object.",
             "https://en.cppreference.com/w/cpp/language/access_specifiers"),

            (r'class\s+(\w+)\s*:\s*public\s+(\w+)',
             "INHERITANCE: '{}' is a child of '{}'.",
             "CONCEPT: The child class gets all the public/protected traits of the parent. This creates an 'IS-A' relationship (e.g., Car is a Vehicle). It promotes code reusability.",
             "https://en.cppreference.com/w/cpp/language/derived_class"),

            (r'virtual\s+.*\s*=\s*0;',
             "PURE VIRTUAL: Enforcing Abstraction (Interface).",
             "CONCEPT: ABSTRACTION. This line says 'I don't know how to do this action yet, but any class that inherits from me MUST define it.' A class with this is an Abstract Class and cannot be instantiated directly.",
             "https://en.cppreference.com/w/cpp/language/abstract_class"),

            (r'virtual\s+',
             "VIRTUAL FUNCTION: Enabling Polymorphism.",
             "CONCEPT: POLYMORPHISM. 'Virtual' tells the compiler: 'Don't bind this function call yet. Wait until the program runs to see what kind of object this really is.' This allows a parent pointer to call the child's version of a function.",
             "https://en.cppreference.com/w/cpp/language/virtual"),

            # Constructors (Copy, Default, Parameterized)
            (r'^\s*(\w+)\s*\(\s*\1\s*&\s*(\w+)\s*\)\s*\{?$',
             "COPY CONSTRUCTOR: Defining copy constructor for class '{0}' copying from '{1}'.",
             "CONCEPT: A copy constructor initializes a new object using an existing object of the same class. It performs a member-wise copy of all fields.",
             "https://en.cppreference.com/w/cpp/language/copy_constructor"),

            (r'^\s*(\w+)\s*\(\s*\)\s*\{?$',
             "DEFAULT CONSTRUCTOR: Initializer for class '{}' with no parameters.",
             "CONCEPT: The default constructor is called automatically when an object is instantiated without any arguments. It is used to set initial default values for class fields.",
             "https://en.cppreference.com/w/cpp/language/default_constructor"),

            (r'^\s*(?!\s*(?:if|for|while|switch|return|void|int|float|double|char|bool|string)\b)(\w+)\s*\(([^&)]+)\)\s*\{?$',
             "PARAMETERIZED CONSTRUCTOR: Initializer for class '{0}' taking inputs: ({1}).",
             "CONCEPT: A parameterized constructor allows passing arguments during object creation to initialize fields to specific values.",
             "https://en.cppreference.com/w/cpp/language/initializer_list"),

            # Object creations
            (r'\b(?!int|float|double|char|bool|string|void|return|const|class|struct|public|private|protected|template)(\w+)\s+(\w+)\s*\(([^)]+)\)\s*;',
             "OBJECT CREATION: Creating object '{1}' of type '{0}' with parameters ({2}).",
             "CONCEPT: Instantiates an object of custom class '{0}' on the Stack by calling its parameterized (or copy) constructor with arguments '{2}'.",
             "https://en.cppreference.com/w/cpp/language/constructor"),

            (r'\b(?!int|float|double|char|bool|string|void|return|const|class|struct|public|private|protected|template)(\w+)\s+(\w+)\s*(?:;|=)?\s*$',
             "OBJECT CREATION: Creating object '{1}' of type '{0}' with default constructor.",
             "CONCEPT: Instantiates an object of custom class '{0}' on the Stack. Because no arguments are specified, the default constructor is invoked.",
             "https://en.cppreference.com/w/cpp/language/default_constructor"),

            # Method Calls
            (r'\b(\w+)\s*(\.|->)\s*(\w+)\s*\((.*)\)\s*;',
             "METHOD CALL: Calling '{2}' on object '{0}' with arguments ({3}).",
             "CONCEPT: Invoking a member function (method) of an object. The '.' operator is used for direct objects, and '->' is used when accessing members via a pointer to an object.",
             "https://en.cppreference.com/w/cpp/language/member_functions"),
        ]

    def explain_line(self, line: str) -> str:
        """
        High-level summary for the code explorer UI. 
        Returns a short, scannable string or a fallback message.
        """
        line = line.strip()
        # Skip purely structural lines
        if not line or line in ["{", "}", "};", "public:", "private:", "protected:"]:
            if line in ["public:", "private:", "protected:"]:
                # Special case: these are short but meaningful, so we check rules
                pass
            else:
                return "..."
        
        for pattern, summary, detail, _ in self.rules:
            match = re.search(pattern, line)
            if match:
                # Use strict error handling for formatting to avoid crashes
                try:
                    # Combine Summary and Concept (Detail)
                    full_text = f"**{summary.format(*match.groups())}**\n\n{detail.format(*match.groups())}"
                    return full_text
                except IndexError:
                    return f"**{summary}**\n\n{detail}"

        # Fallback for unsupported lines
        return "Line analysis unsupported. (AI Explanation Available)"

    def explain_line_structured(self, line: str) -> dict:
        """
        Structured line explanation returning summary, detail, and reference URL.
        """
        line = line.strip()
        if not line or line in ["{", "}", "};", "public:", "private:", "protected:"]:
            return {
                "summary": "...",
                "detail": "",
                "url": None
            }
        
        for pattern, summary, detail, url in self.rules:
            match = re.search(pattern, line)
            if match:
                try:
                    s = summary.format(*match.groups())
                    d = detail.format(*match.groups())
                except IndexError:
                    s = summary
                    d = detail
                return {
                    "summary": s,
                    "detail": d,
                    "url": url
                }
        return {
            "summary": "Line analysis unsupported",
            "detail": "Use the AI Assistant on the right for in-depth questions.",
            "url": None
        }

    def explain_more(self, line: str) -> Optional[Tuple[str, str]]:
        """
        Technical drill-down with documentation link.
        Returns (Description, URL) or None.
        """
        line = line.strip()
        for pattern, _, detail, url in self.rules:
            match = re.search(pattern, line)
            if match:
                try:
                    return (detail.format(*match.groups()), url)
                except IndexError:
                    return (detail, url)
        return None

    def get_options(self, line: str) -> List[str]:
        """UI helper to show if 'More Info' is available."""
        return ['more'] if self.explain_more(line) else []