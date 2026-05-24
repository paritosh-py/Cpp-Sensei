import re
from typing import Optional, Tuple, List

class SenseiLogic:
    def __init__(self):
        # ======================================================================
        # HEADER-SPECIFIC EXPLANATION DICTIONARY
        # Maps header names to (summary, detail, url) tuples.
        # When #include <X> is detected, we look up X here for a precise explanation.
        # ======================================================================
        self.header_explanations = {
            "iostream": (
                "INPUT/OUTPUT LIBRARY: Enabling keyboard input and screen output.",
                "CONCEPT: This is the most fundamental library in C++. It gives you access to 'cout' (which prints text to the screen) and 'cin' (which reads input from the keyboard). Think of it as plugging in a keyboard and monitor to your program — without this library, your program cannot communicate with the user at all.\n\nThe name 'iostream' stands for 'Input/Output Stream'. In C++, all input and output happens through 'streams' — imagine data flowing like water through a pipe. 'cout' sends data out through the output pipe to your screen, and 'cin' receives data in through the input pipe from your keyboard.\n\nThis is almost always the first library you include in any C++ program.",
                "https://en.cppreference.com/w/cpp/header/iostream"
            ),
            "vector": (
                "DYNAMIC ARRAY LIBRARY: Enabling flexible, resizable lists.",
                "CONCEPT: A vector is like an array that can grow and shrink automatically. Regular arrays in C++ have a fixed size — once you create an array of 5 elements, it stays at 5 forever. Vectors solve this problem by managing their own memory.\n\nImagine you have a notebook with exactly 10 pages. If you need an 11th page, you're stuck. A vector is like a magical notebook that adds new pages whenever you need them. Behind the scenes, when a vector runs out of space, it creates a bigger block of memory, copies everything over, and frees the old space.\n\nVectors are the most commonly used container in C++ and should be your default choice for storing lists of things. You can add items with .push_back(), remove the last item with .pop_back(), access items with [index], and check the size with .size().",
                "https://en.cppreference.com/w/cpp/header/vector"
            ),
            "string": (
                "STRING LIBRARY: Enabling easy text handling.",
                "CONCEPT: This library gives you the 'string' type, which makes working with text in C++ much easier than the old C-style character arrays. A string automatically manages its own memory, so you can freely concatenate text, search within it, or resize it without worrying about buffer sizes.\n\nWithout this library, you would have to use character arrays (like 'char name[50]') and manually track lengths, copy characters one by one, and worry about running out of space. The string class handles all of that for you.\n\nYou can combine strings with the + operator (like 'hello' + ' world'), compare them with == and <, find substrings with .find(), get individual characters with [index], and check the length with .length() or .size().",
                "https://en.cppreference.com/w/cpp/header/string"
            ),
            "cmath": (
                "MATH LIBRARY: Enabling mathematical functions.",
                "CONCEPT: This library provides standard mathematical operations that go beyond basic arithmetic (+, -, *, /). It includes functions like sqrt() for square roots, pow() for exponents, abs() for absolute values, sin()/cos()/tan() for trigonometry, log() for logarithms, ceil() and floor() for rounding, and many more.\n\nThe name 'cmath' comes from the C language's 'math.h' header — the 'c' prefix means it's the C++ version of a C library. If you need to calculate anything more complex than basic addition and multiplication, you'll need this library.\n\nFor example, to calculate the hypotenuse of a right triangle: sqrt(pow(a, 2) + pow(b, 2)).",
                "https://en.cppreference.com/w/cpp/header/cmath"
            ),
            "algorithm": (
                "ALGORITHM LIBRARY: Enabling sorting, searching, and data manipulation.",
                "CONCEPT: This is one of the most powerful libraries in C++. It provides ready-made functions for common operations you would otherwise have to code yourself: sort() to arrange data in order, find() to search for values, count() to count occurrences, reverse() to flip a sequence, min()/max() to find extremes, and many more.\n\nThink of it as a toolkit of pre-built solutions. Instead of writing your own sorting algorithm (which is error-prone and time-consuming), you simply call sort() and it uses an optimized algorithm (IntroSort) that's faster than what most programmers could write themselves.\n\nMost algorithm functions work with iterators — pointers that walk through containers. The typical pattern is: sort(vec.begin(), vec.end()) to sort an entire vector.",
                "https://en.cppreference.com/w/cpp/header/algorithm"
            ),
            "fstream": (
                "FILE STREAM LIBRARY: Enabling reading from and writing to files.",
                "CONCEPT: This library lets your program interact with files on the computer's hard drive. It provides three main tools: 'ifstream' for reading files (Input File Stream), 'ofstream' for writing files (Output File Stream), and 'fstream' for both reading and writing.\n\nThink of it like opening a document on your computer. 'ifstream' opens the document in read-only mode, 'ofstream' creates or overwrites a document, and 'fstream' opens it for editing. You use the same << and >> operators you use with cout and cin, making file I/O feel natural.\n\nAlways remember to close your files when you're done (.close()), or use the automatic closing that happens when the file stream object goes out of scope.",
                "https://en.cppreference.com/w/cpp/header/fstream"
            ),
            "iomanip": (
                "I/O FORMATTING LIBRARY: Controlling how output looks.",
                "CONCEPT: This library gives you precise control over how numbers and text appear on screen. It provides manipulators like setw() (set width — add padding), setprecision() (control decimal places), fixed (force fixed-point notation), left/right (alignment), setfill() (choose padding character), and more.\n\nFor example, if you want to display prices with exactly 2 decimal places: cout << fixed << setprecision(2) << price. Or if you want to create a neat table with aligned columns: cout << setw(10) << left << name.\n\nThis library is essential when you need your output to look professional and formatted, rather than just dumping raw numbers to the screen.",
                "https://en.cppreference.com/w/cpp/header/iomanip"
            ),
            "map": (
                "ORDERED MAP LIBRARY: Enabling key-value pair storage.",
                "CONCEPT: A map is like a dictionary — it stores pairs of data where each 'key' is linked to a 'value'. You look things up by key instead of by position. For example, you could map student names (keys) to their grades (values).\n\nMaps in C++ keep all keys automatically sorted in ascending order and guarantee that every key is unique. Behind the scenes, they use a balanced binary search tree (Red-Black Tree), which means looking up any key takes O(log n) time — very fast even with millions of entries.\n\nUse map when you need fast lookups by a descriptive key rather than a numeric index. If you don't need sorted keys, use unordered_map instead (it's even faster for lookups).",
                "https://en.cppreference.com/w/cpp/header/map"
            ),
            "set": (
                "ORDERED SET LIBRARY: Enabling unique, sorted collections.",
                "CONCEPT: A set is a collection that automatically removes duplicates and keeps everything sorted. If you insert the number 5 three times, the set will only contain one copy of 5.\n\nThis is incredibly useful when you need to track unique items — for example, finding all unique words in a document, or checking if a value has been seen before. Sets use a balanced binary search tree internally, so insertion, deletion, and lookup all take O(log n) time.\n\nUse set when you need uniqueness and sorted order. If you only need uniqueness without sorting, use unordered_set (which uses a hash table and is faster).",
                "https://en.cppreference.com/w/cpp/header/set"
            ),
            "queue": (
                "QUEUE LIBRARY: Enabling First-In-First-Out (FIFO) data structure.",
                "CONCEPT: A queue works exactly like a real-life queue (line) at a store — the first person to join the line is the first person to be served. In programming, this is called FIFO (First-In, First-Out).\n\nYou add elements to the back with .push() and remove them from the front with .pop(). You can peek at the front element with .front() and the back with .back(). Queues are used extensively in algorithms like Breadth-First Search (BFS), task scheduling, and message processing.\n\nThis library also provides 'priority_queue', where elements come out in priority order (highest value first by default) rather than insertion order.",
                "https://en.cppreference.com/w/cpp/header/queue"
            ),
            "stack": (
                "STACK LIBRARY: Enabling Last-In-First-Out (LIFO) data structure.",
                "CONCEPT: A stack works like a stack of plates — you can only add or remove from the top. The last item you put in is the first one you take out. This is called LIFO (Last-In, First-Out).\n\nYou add elements with .push(), remove the top element with .pop(), and peek at the top with .top(). Stacks are fundamental in computer science — they're used for function call tracking, undo operations, expression evaluation, backtracking algorithms, and Depth-First Search (DFS).\n\nFun fact: Every time your program calls a function, the computer uses a stack (the 'call stack') to remember where to return when the function finishes.",
                "https://en.cppreference.com/w/cpp/header/stack"
            ),
            "array": (
                "FIXED ARRAY LIBRARY: Enabling safe, fixed-size arrays.",
                "CONCEPT: This library provides std::array, which is a safer, more modern alternative to traditional C-style arrays. Unlike C arrays, std::array knows its own size (.size()), can be compared with == and <, and provides bounds-checked access with .at().\n\nThe key difference from vectors is that std::array has a fixed size determined at compile time — it cannot grow or shrink. Use it when you know exactly how many elements you need and that number won't change.",
                "https://en.cppreference.com/w/cpp/header/array"
            ),
            "deque": (
                "DOUBLE-ENDED QUEUE LIBRARY: Enabling fast insertion at both ends.",
                "CONCEPT: A deque (pronounced 'deck') is like a vector that can efficiently add and remove elements from both the front AND the back. Regular vectors can only efficiently add/remove at the back. Deque stands for 'Double-Ended Queue'.\n\nUse deque when you need fast access at both ends — for example, implementing a sliding window algorithm or a work-stealing task scheduler.",
                "https://en.cppreference.com/w/cpp/header/deque"
            ),
            "list": (
                "LINKED LIST LIBRARY: Enabling a doubly-linked list.",
                "CONCEPT: A list is a doubly-linked list — each element knows the address of both the next and previous elements. This makes inserting or removing elements from the middle extremely fast (O(1) if you have an iterator to the position), but accessing elements by index is slow (O(n)) because you have to walk through the chain.\n\nUse list when you need frequent insertions/deletions in the middle and don't need random access by index.",
                "https://en.cppreference.com/w/cpp/header/list"
            ),
            "unordered_map": (
                "HASH MAP LIBRARY: Enabling ultra-fast key-value lookups.",
                "CONCEPT: An unordered_map is like a regular map (key-value pairs), but instead of keeping keys sorted, it uses a hash table for O(1) average-time lookups. This makes it significantly faster than map for most use cases.\n\nThe trade-off is that keys are stored in no particular order. Use unordered_map when you need the fastest possible lookups and don't care about key ordering.",
                "https://en.cppreference.com/w/cpp/header/unordered_map"
            ),
            "unordered_set": (
                "HASH SET LIBRARY: Enabling ultra-fast unique element tracking.",
                "CONCEPT: An unordered_set is like a regular set (unique elements only), but uses a hash table for O(1) average-time lookups instead of a sorted tree. It's the fastest way to check 'have I seen this value before?'.\n\nUse unordered_set when you need uniqueness checking and don't need the elements to be sorted.",
                "https://en.cppreference.com/w/cpp/header/unordered_set"
            ),
            "cstdlib": (
                "C STANDARD LIBRARY: General purpose utilities.",
                "CONCEPT: This library provides miscellaneous utility functions inherited from the C language. Key functions include rand() and srand() for generating random numbers, abs() for absolute values of integers, atoi()/atof() for converting strings to numbers, system() for running operating system commands, exit() for terminating the program, and malloc()/free() for C-style memory management.\n\nThe 'c' prefix means this is the C++ version of C's <stdlib.h> header.",
                "https://en.cppreference.com/w/cpp/header/cstdlib"
            ),
            "climits": (
                "INTEGER LIMITS LIBRARY: Defining maximum and minimum values for data types.",
                "CONCEPT: This library defines constants like INT_MAX (the largest value an int can hold, typically 2,147,483,647), INT_MIN (the smallest int, typically -2,147,483,648), CHAR_MAX, LONG_MAX, and similar limits for all integer types.\n\nThese constants are essential when you need to initialize variables to extreme values (like setting a minimum tracker to INT_MAX before searching for the actual minimum in an array).",
                "https://en.cppreference.com/w/cpp/header/climits"
            ),
            "cstring": (
                "C STRING LIBRARY: Functions for C-style character arrays.",
                "CONCEPT: This library provides functions for manipulating C-style strings (null-terminated character arrays): strlen() to get length, strcpy() to copy, strcat() to concatenate, strcmp() to compare, strstr() to find substrings, and memset()/memcpy() for raw memory operations.\n\nIn modern C++, you should usually prefer std::string over C-style strings, but these functions are still widely used in competitive programming, legacy code, and systems programming.",
                "https://en.cppreference.com/w/cpp/header/cstring"
            ),
            "sstream": (
                "STRING STREAM LIBRARY: Treating strings as input/output streams.",
                "CONCEPT: This library lets you use strings as if they were input/output streams (like cin/cout). 'istringstream' reads from a string, 'ostringstream' writes to a string, and 'stringstream' does both.\n\nThis is extremely useful for parsing — for example, splitting a line of text into individual words, or converting numbers to strings and vice versa. It's a cleaner alternative to C-style sprintf/sscanf.",
                "https://en.cppreference.com/w/cpp/header/sstream"
            ),
            "numeric": (
                "NUMERIC LIBRARY: Numeric operations on sequences.",
                "CONCEPT: This library provides functions for numeric computations on ranges: accumulate() to sum all elements, partial_sum() for running totals, inner_product() for dot products, adjacent_difference() for differences between consecutive elements, and iota() to fill a range with incrementing values.\n\nFor example, to sum all elements of a vector: accumulate(v.begin(), v.end(), 0).",
                "https://en.cppreference.com/w/cpp/header/numeric"
            ),
            "memory": (
                "SMART POINTER LIBRARY: Enabling automatic memory management.",
                "CONCEPT: This library provides smart pointers — objects that automatically manage dynamically allocated memory. 'unique_ptr' owns memory exclusively and deletes it when the pointer goes out of scope. 'shared_ptr' allows multiple pointers to share ownership, deleting memory only when the last shared_ptr is destroyed.\n\nSmart pointers prevent memory leaks (forgetting to delete) and dangling pointers (using memory after it's freed). In modern C++, you should almost never use raw 'new' and 'delete' — use smart pointers instead.",
                "https://en.cppreference.com/w/cpp/header/memory"
            ),
            "utility": (
                "UTILITY LIBRARY: Pair, move semantics, and general utilities.",
                "CONCEPT: This library provides several fundamental utilities. The most commonly used is 'pair', which bundles two values together (like storing both a name and an age). It also provides 'move()' for efficient resource transfer, 'swap()' for exchanging values, and 'make_pair()' for creating pairs.\n\nPairs are used extensively with maps (each map entry is a pair of key and value) and when functions need to return two values.",
                "https://en.cppreference.com/w/cpp/header/utility"
            ),
            "cctype": (
                "CHARACTER TYPE LIBRARY: Character classification and conversion.",
                "CONCEPT: This library provides functions to test and convert individual characters: isalpha() checks if a character is a letter, isdigit() checks if it's a digit, isalnum() checks for letter or digit, isupper()/islower() check case, toupper()/tolower() convert case, and isspace() checks for whitespace.\n\nThese are essential for text processing — for example, counting vowels in a string or converting user input to uppercase.",
                "https://en.cppreference.com/w/cpp/header/cctype"
            ),
            "ctime": (
                "TIME LIBRARY: Date, time, and clock functions.",
                "CONCEPT: This library provides functions for working with dates and times: time() gets the current time, clock() measures CPU time used, difftime() calculates time differences, and localtime()/strftime() format time as readable strings.\n\nCommonly used for measuring how long code takes to run, generating timestamps, or seeding random number generators with srand(time(0)).",
                "https://en.cppreference.com/w/cpp/header/ctime"
            ),
            "bitset": (
                "BITSET LIBRARY: Fixed-size sequence of bits.",
                "CONCEPT: A bitset is a compact way to store and manipulate a fixed number of binary flags (0s and 1s). It provides bitwise operations (AND, OR, XOR, NOT), counting set bits (.count()), testing individual bits (.test()), and converting to/from strings and integers.\n\nUseful in competitive programming for subset enumeration, sieve algorithms, and anywhere you need compact boolean storage.",
                "https://en.cppreference.com/w/cpp/header/bitset"
            ),
            "tuple": (
                "TUPLE LIBRARY: Grouping multiple values of different types.",
                "CONCEPT: A tuple is like a pair but can hold any number of values, each of a different type. You access elements with get<0>(t), get<1>(t), etc. Tuples are useful when you need to group 3 or more related values together without creating a full struct or class.\n\nFor example, you could represent a 3D point as tuple<double, double, double> or a student record as tuple<string, int, double> for name, age, and GPA.",
                "https://en.cppreference.com/w/cpp/header/tuple"
            ),
            "regex": (
                "REGULAR EXPRESSION LIBRARY: Pattern matching in text.",
                "CONCEPT: This library provides tools for searching, matching, and replacing text using regular expressions (regex) — powerful pattern descriptions. For example, you can check if a string looks like an email address, extract all numbers from text, or replace all occurrences of a pattern.\n\nRegex is a mini-language for describing text patterns. While powerful, it can be slow for large inputs compared to manual parsing.",
                "https://en.cppreference.com/w/cpp/header/regex"
            ),
            "chrono": (
                "MODERN TIME LIBRARY: High-precision time measurement.",
                "CONCEPT: This is C++'s modern time library, providing high-precision clocks and duration types. It's the proper way to measure execution time in modern C++: take a time point before and after your code, then calculate the difference.\n\nUnlike ctime, chrono provides type-safe time durations (seconds, milliseconds, microseconds) and steady clocks that aren't affected by system clock adjustments.",
                "https://en.cppreference.com/w/cpp/header/chrono"
            ),
            "functional": (
                "FUNCTION OBJECTS LIBRARY: Storing and passing functions.",
                "CONCEPT: This library provides tools for working with functions as objects. The most important is std::function, which can store any callable — a regular function, a lambda, or a function object. It also provides standard function objects like plus<>, minus<>, greater<>, less<> for use with algorithms.\n\nUseful when you need to pass functions as arguments to other functions (callbacks), or store functions in containers.",
                "https://en.cppreference.com/w/cpp/header/functional"
            ),
            "cassert": (
                "ASSERTION LIBRARY: Runtime debugging checks.",
                "CONCEPT: This library provides the assert() macro — a debugging tool that checks if a condition is true. If the condition is false, the program immediately crashes with a helpful error message showing the exact file, line number, and failed condition.\n\nAssertions are used during development to catch impossible situations early. They are automatically disabled in release builds for performance.",
                "https://en.cppreference.com/w/cpp/header/cassert"
            ),
            "cstdio": (
                "C STANDARD I/O LIBRARY: C-style input/output functions.",
                "CONCEPT: This library provides C-style I/O functions: printf() for formatted output, scanf() for formatted input, fprintf()/fscanf() for file I/O, sprintf() for string formatting, and more.\n\nWhile iostream is the C++ standard, printf/scanf are still widely used in competitive programming because they are often faster than cout/cin. Many experienced C++ programmers use both styles depending on the situation.",
                "https://en.cppreference.com/w/cpp/header/cstdio"
            ),
        }

        # The order matters! Specific rules should generally come before generic ones.
        self.rules = [
            # ==============================================================================
            # GROUP 0: COMMENTS (Must be first — comments should never fall through)
            # ==============================================================================
            (r'^\s*/\*\*',
             "DOCUMENTATION COMMENT: A special comment block for generating documentation.",
             "CONCEPT: This is a documentation comment, commonly used with tools like Doxygen. Documentation comments use a special format (starting with /**) to describe what functions, classes, or files do. These comments can be automatically processed to generate beautiful documentation web pages for your code.\n\nWhile the compiler ignores these just like regular comments, they serve an important professional purpose — they help other programmers (and your future self) understand your code's design and usage without reading through every line.",
             "https://en.cppreference.com/w/cpp/comment"),

            (r'^\s*///\s*(.*)',
             "DOCUMENTATION COMMENT: A single-line documentation note.",
             "CONCEPT: Triple-slash comments (///) are another style of documentation comment. Like /**, these are used by documentation generation tools to create automatic documentation. They describe the purpose, parameters, or return values of the code that follows.\n\nThe compiler treats these exactly like regular comments — they are completely ignored during compilation. Their value is entirely for human readers and documentation tools.",
             "https://en.cppreference.com/w/cpp/comment"),

            (r'^\s*//\s*(.*)',
             "COMMENT: A note from the programmer — '{0}'.",
             "CONCEPT: This is a single-line comment. Comments are notes that programmers write inside the code to explain what the code is doing, why certain decisions were made, or to leave reminders for future work. The computer completely ignores everything after the // on this line — it has zero effect on how the program runs.\n\nComments are extremely important in programming because code is read far more often than it is written. Good comments explain the 'why' behind the code (not just the 'what'), making it easier for other programmers (or your future self) to understand the logic months or years later.\n\nBest practice: Write comments to explain complex logic, not obvious things. For example, '// Check if user is adult' is better than '// Set x to 18' — the first explains intent, the second just repeats the code.",
             "https://en.cppreference.com/w/cpp/comment"),

            (r'^\s*/\*',
             "MULTI-LINE COMMENT START: Beginning a block comment.",
             "CONCEPT: This begins a multi-line comment block. Everything between /* and the closing */ is treated as a comment by the compiler, even if it spans multiple lines. This is useful when you need to write longer explanations, temporarily disable a block of code during debugging, or add a file header with copyright and author information.\n\nUnlike single-line comments (//) which only cover one line, block comments can wrap around as many lines as you need. Just remember to close them with */ — forgetting to close a block comment is a common source of confusing compilation errors.",
             "https://en.cppreference.com/w/cpp/comment"),

            (r'^\s*\*/',
             "MULTI-LINE COMMENT END: Closing a block comment.",
             "CONCEPT: This closes a multi-line comment block that was started with /*. Everything between the opening /* and this closing */ was ignored by the compiler. The code after this line will be read and compiled normally again.\n\nA common formatting style is to align the */ with the opening /* and put a * at the start of each comment line in between, creating a neat visual block.",
             "https://en.cppreference.com/w/cpp/comment"),

            (r'^\s*\*\s*(.*)',
             "COMMENT CONTINUATION: Continuing a block comment — '{0}'.",
             "CONCEPT: This line is part of a multi-line comment block (between /* and */). The leading * is a formatting convention — it makes the comment block visually neat and easy to identify. The compiler ignores this entire line.\n\nThis style is commonly used for function descriptions, file headers, and detailed explanations that span multiple lines.",
             "https://en.cppreference.com/w/cpp/comment"),

            # ==============================================================================
            # GROUP 1: PREPROCESSOR & HEADERS
            # ==============================================================================
            (r'#include\s*<bits/stdc\+\+\.h>',
             "COMPETITIVE CODING HEADER: Importing absolutely everything in C++.",
             "CONCEPT: This is a special 'convenience header' often used in competitive programming contests. Instead of including individual libraries one by one (iostream, vector, algorithm, etc.), this single line includes ALL standard library headers at once — hundreds of them.\n\nPROS: You never have to think about which headers to include. It saves time during timed competitions.\n\nCONS: It dramatically increases compilation time because the compiler has to process thousands of lines of library code you probably don't need. It's also NOT part of the official C++ standard — it only works with the GCC compiler (g++), so code using this won't compile on Visual Studio or Clang.\n\nFor learning purposes and real software projects, it's much better to include only the specific headers you actually need. This teaches you what each library provides and keeps your code portable across different compilers.",
             "https://en.cppreference.com/w/cpp/header"),

            # Generic #include <header> — uses dictionary lookup for specific explanations
            (r'#include\s*<([^>]+)>',
             "HEADER IMPORT: Loading the <{0}> library.",
             "__HEADER_LOOKUP__",
             "https://en.cppreference.com/w/cpp/header"),

            # User-defined header includes
            (r'#include\s*"([^"]+)"',
             "USER HEADER: Including your own file '{0}'.",
             "CONCEPT: This includes a header file that YOU wrote (or that is part of your project), rather than a standard library header. The double quotes tell the compiler to first look in your project's directory before searching the system library folders.\n\nHeader files typically contain declarations — they announce what functions, classes, and variables exist so that other files in your project can use them. The actual code (definitions) usually goes in a separate .cpp file.\n\nFor example, if you wrote helper functions in 'utils.h', you include them with #include \"utils.h\" in any file that needs those functions. This is how large C++ programs are organized across multiple files.",
             "https://en.cppreference.com/w/cpp/preprocessor/include"),

            # Preprocessor directives
            (r'#define\s+(\w+)\s*(.*)',
             "MACRO DEFINITION: Creating a text replacement rule '{0}'.",
             "CONCEPT: The #define directive creates a 'macro' — a text substitution rule that the preprocessor applies before the compiler even sees the code. Everywhere the name '{0}' appears in your code after this line, the preprocessor replaces it with '{1}'.\n\nMacros are commonly used to define constants (like #define PI 3.14159), create shorthand for repetitive code, and enable/disable features with conditional compilation. However, in modern C++, using 'const' or 'constexpr' for constants is preferred because they provide type safety — macros are just raw text replacement and can cause subtle bugs.\n\nWARNING: Macros don't follow normal C++ scoping rules and can lead to surprising behavior. Use them sparingly and prefer proper C++ alternatives when possible.",
             "https://en.cppreference.com/w/cpp/preprocessor/replace"),

            (r'#ifdef\s+(\w+)',
             "CONDITIONAL COMPILATION: Compile this section only if '{0}' is defined.",
             "CONCEPT: This is part of the preprocessor's conditional compilation system. The code between #ifdef and the matching #endif will ONLY be included in the compilation if the macro '{0}' has been previously defined with #define.\n\nThis is commonly used for: platform-specific code (compile different code for Windows vs Linux), debug-only features (#ifdef DEBUG), and header include guards (preventing the same header file from being included twice, which would cause errors).\n\nConditional compilation happens BEFORE the actual C++ compiler runs — the preprocessor literally removes the irrelevant code sections.",
             "https://en.cppreference.com/w/cpp/preprocessor/conditional"),

            (r'#ifndef\s+(\w+)',
             "INCLUDE GUARD: Compile only if '{0}' is NOT defined.",
             "CONCEPT: This is the standard 'include guard' pattern. It checks if a macro has NOT been defined yet. It's almost always used at the top of header files in this pattern:\n\n#ifndef MY_HEADER_H\n#define MY_HEADER_H\n// ... header contents ...\n#endif\n\nThis prevents a common problem: if two different files both #include the same header, the compiler would see the definitions twice and throw errors. The include guard ensures the header's contents are only processed once, no matter how many times it's included.\n\nAlternatively, some compilers support '#pragma once' which achieves the same thing with less code.",
             "https://en.cppreference.com/w/cpp/preprocessor/conditional"),

            (r'#endif',
             "END CONDITIONAL: Closing a conditional compilation block.",
             "CONCEPT: This marks the end of a conditional compilation block that was started with #ifdef, #ifndef, or #if. All the code between the opening directive and this #endif is either included or excluded from compilation based on the condition.\n\nEvery #ifdef/#ifndef/#if must have a matching #endif — forgetting one will cause confusing compilation errors that seem to affect code far away from the actual problem.",
             "https://en.cppreference.com/w/cpp/preprocessor/conditional"),

            (r'#pragma\s+(.*)',
             "COMPILER DIRECTIVE: Special instruction to the compiler — '{0}'.",
             "CONCEPT: #pragma directives are special instructions that tell the compiler to do something specific. The most common is '#pragma once', which is a modern shorthand for include guards — it tells the compiler to only include this header file once.\n\nOther pragmas control warnings, optimization settings, memory alignment, and compiler-specific features. Unlike standard C++ code, pragmas are compiler-specific — a pragma that works on GCC might not work on Visual Studio.\n\nNote: #pragma is technically not part of the C++ language standard, but '#pragma once' is supported by virtually all modern compilers.",
             "https://en.cppreference.com/w/cpp/preprocessor/impl"),

            (r'using\s+namespace\s+std;',
             "NAMESPACE DIRECTIVE: Making standard library names available directly.",
             "CONCEPT: By default, everything in the C++ standard library lives inside a 'namespace' called 'std' (short for 'standard'). Without this line, you would have to write 'std::cout', 'std::cin', 'std::string', 'std::vector', etc. — adding 'std::' before every standard library name.\n\nThis line says: 'If you see a name you don't recognize in my code, also check the std namespace.' This lets you write just 'cout' instead of 'std::cout', making code shorter and easier to read for beginners.\n\nIMPORTANT WARNING: In large projects and professional code, this is considered bad practice because it can cause 'name collisions' — if you create a variable with the same name as something in the standard library (like 'count', 'find', or 'swap'), the compiler gets confused. In professional code, you'll see 'std::' used explicitly instead.",
             "https://en.cppreference.com/w/cpp/language/namespace"),

            
            # ==============================================================================
            # GROUP 4: MEMORY (POINTERS, REFS, DYNAMIC)
            # ==============================================================================
            (r'(\w+)\s*\*\s*(\w+)\s*=\s*nullptr',
             "NULL POINTER: Creating a pointer '{1}' that points to nothing.",
             "CONCEPT: This creates a pointer variable that intentionally points to nothing. 'nullptr' is C++'s way of saying 'this pointer doesn't have a valid address yet.' It's like having an empty envelope with no address written on it.\n\nAlways initialize pointers to nullptr when you don't have an address to assign yet. This makes it easy to check if a pointer is valid before using it: 'if (ptr != nullptr)'. Using a pointer that points to random garbage memory is one of the most dangerous bugs in C++.\n\nNOTE: In older C and C++ code, you might see NULL or 0 used instead of nullptr. Prefer nullptr in modern C++ — it's type-safe and can't be confused with the integer 0.",
             "https://en.cppreference.com/w/cpp/language/nullptr"),

            (r'(\w+)\s*\*\s*(\w+)\s*=',
             "POINTER: '{1}' stores a memory address, not a direct value.",
             "CONCEPT: A pointer is a variable that stores the MEMORY ADDRESS of another variable, rather than a value itself. Think of it like a piece of paper with a house address written on it — the paper isn't the house, but it tells you where to find the house.\n\nIf 'int x = 42' is a house containing the number 42, then 'int* p = &x' is a piece of paper that says 'the house at address 0x7fff5fbff8ac'. To get the actual value, you 'dereference' the pointer with *p, which follows the address and returns 42.\n\nPointers are essential for: dynamic memory allocation (new/delete), efficient passing of large data to functions, building data structures like linked lists and trees, and polymorphism (a parent pointer can point to child objects).\n\nWARNING: Using pointers incorrectly (dangling pointers, null dereference, memory leaks) is the #1 source of bugs and security vulnerabilities in C/C++ programs.",
             "https://en.cppreference.com/w/cpp/language/pointer"),

            (r'(\w+)\s*&\s*(\w+)\s*=',
             "REFERENCE: '{1}' is a permanent alias for another variable.",
             "CONCEPT: A reference is an alternative name (alias) for an existing variable. Once a reference is created, it is permanently bonded to the original variable — they share the same memory. Changing the reference changes the original, and vice versa.\n\nThink of it like a person with a nickname. If your name is 'Robert' and your nickname is 'Bob', both names refer to the same person. If 'Bob' gets a haircut, 'Robert' also has short hair — they're the same person.\n\nReferences are commonly used for function parameters to avoid copying large objects: 'void process(const string& text)' passes the original string directly instead of making a full copy. This is both faster and uses less memory.\n\nKEY DIFFERENCES FROM POINTERS: References can never be null, can never be reassigned to a different variable, and don't need special syntax (* or ->) to use. They are safer and simpler than pointers.",
             "https://en.cppreference.com/w/cpp/language/reference"),

            (r'new\s+(\w+)\[',
             "DYNAMIC ARRAY: Allocating an array on the heap.",
             "CONCEPT: This creates an array in the 'heap' memory area (as opposed to the 'stack' where normal variables live). The heap is a large pool of memory that you manage manually. The array stays alive until you explicitly free it with 'delete[]'.\n\nUse dynamic arrays when you need the size to be determined at runtime (not known at compile time), or when the array is very large (the stack has limited space, typically 1-8 MB).\n\nCRITICAL: Always pair 'new[]' with 'delete[]' (not just 'delete'). Using plain 'delete' on an array causes undefined behavior. Better yet, use std::vector instead of manual dynamic arrays — it handles memory automatically.",
             "https://en.cppreference.com/w/cpp/language/new"),

            (r'new\s+(\w+)',
             "DYNAMIC ALLOCATION: Manually requesting memory on the heap.",
             "CONCEPT: The 'new' keyword allocates memory on the 'heap' — a large memory area separate from the 'stack' where normal variables live. Standard variables on the stack are automatically destroyed when the function ends. Heap objects persist until you explicitly destroy them with 'delete'.\n\nThis is essential when you need objects that outlive the function that created them, or when you need to create objects whose exact type is determined at runtime (polymorphism).\n\nMODERN C++ WARNING: Raw 'new' and 'delete' are considered error-prone. Modern C++ strongly recommends using smart pointers (unique_ptr, shared_ptr) from the <memory> library, which automatically manage memory and prevent leaks.",
             "https://en.cppreference.com/w/cpp/language/new"),

            (r'delete\s*\[\]\s*(\w+)',
             "ARRAY MEMORY CLEANUP: Freeing a dynamically allocated array.",
             "CONCEPT: This frees the memory of a dynamic array that was created with 'new[]'. It's absolutely critical that you use 'delete[]' (with brackets) for arrays, not just 'delete' (without brackets).\n\nUsing 'delete' without brackets on an array only frees the first element, leaving the rest as a memory leak. Using 'delete[]' properly calls the destructor for EVERY element in the array and then frees all the memory.\n\nRemember: Every 'new[]' must have exactly one matching 'delete[]'. Too few = memory leak. Too many = double-free crash.",
             "https://en.cppreference.com/w/cpp/language/delete"),

            (r'delete\s+(\w+)',
             "MEMORY CLEANUP: Returning borrowed memory to the system.",
             "CONCEPT: This frees memory that was previously allocated with 'new'. In C++, there is no automatic garbage collector like in Java or Python — if you allocate memory with 'new', YOU are responsible for freeing it with 'delete'. If you forget, your program has a 'memory leak' — it gradually consumes more and more RAM until it runs out.\n\nAfter deleting a pointer, it becomes a 'dangling pointer' — it still holds the old address, but that memory is no longer yours. Accessing a dangling pointer causes undefined behavior. Best practice: set the pointer to nullptr immediately after deleting: 'delete ptr; ptr = nullptr;'.",
             "https://en.cppreference.com/w/cpp/language/delete"),

            (r'unique_ptr\s*<\s*(\w+)\s*>',
             "SMART POINTER (unique): Automatic memory management for one owner.",
             "CONCEPT: A unique_ptr is the modern C++ solution to manual memory management. It wraps a raw pointer and guarantees that the memory will be automatically freed when the unique_ptr goes out of scope (when the function ends, or the object is destroyed).\n\n'Unique' means exactly one unique_ptr can own the object at a time — you cannot copy it, only 'move' it to transfer ownership. This prevents the common bug of accidentally freeing the same memory twice.\n\nUse unique_ptr whenever you need dynamic allocation. Create it with: auto ptr = make_unique<int>(42); This completely eliminates the need for 'new' and 'delete' in most code.",
             "https://en.cppreference.com/w/cpp/memory/unique_ptr"),

            (r'shared_ptr\s*<\s*(\w+)\s*>',
             "SMART POINTER (shared): Automatic memory management for multiple owners.",
             "CONCEPT: A shared_ptr allows multiple pointers to share ownership of the same dynamically allocated object. It uses reference counting — it keeps track of how many shared_ptrs point to the object, and only frees the memory when the LAST shared_ptr is destroyed.\n\nUse shared_ptr when multiple parts of your program need to access the same resource and you can't determine which one will finish last. Create it with: auto ptr = make_shared<int>(42).\n\nWARNING: Be careful of circular references (A points to B, B points to A) — this can prevent the reference count from ever reaching zero, causing a memory leak. Use weak_ptr to break cycles.",
             "https://en.cppreference.com/w/cpp/memory/shared_ptr"),

            # ==============================================================================
            # GROUP 5: STL CONTAINERS & DATA STRUCTURES
            # ==============================================================================
            (r'vector\s*<\s*(\w+)\s*>',
             "STL VECTOR: A dynamic, resizable array of '{0}' values.",
             "CONCEPT: A vector is the most commonly used container in C++. Think of it as a super-powered array that can grow and shrink automatically. Unlike regular arrays whose size is fixed at creation, vectors adjust their capacity as you add or remove elements.\n\nKey operations:\n• .push_back(value) — add an element to the end\n• .pop_back() — remove the last element\n• .size() — how many elements are currently stored\n• [index] — access an element by position (fast, no bounds checking)\n• .at(index) — access with bounds checking (throws an exception if out of range)\n• .empty() — check if the vector has no elements\n• .clear() — remove all elements\n\nBehind the scenes: When a vector runs out of internal space, it allocates a new block of memory (usually double the current size), copies all elements over, and frees the old block. This makes push_back() very fast on average (amortized O(1)).\n\nVectors should be your default choice whenever you need a list of things in C++.",
             "https://en.cppreference.com/w/cpp/container/vector"),

            (r'map\s*<\s*(\w+)\s*,\s*(\w+)\s*>',
             "STL MAP: A sorted dictionary linking '{0}' keys to '{1}' values.",
             "CONCEPT: A map stores data in key-value pairs — like a real dictionary where words (keys) map to definitions (values). You look up data by its key rather than by a numeric position.\n\nFor example, map<string, int> ages could store: 'Alice' → 25, 'Bob' → 30. You access values with ages[\"Alice\"], which returns 25.\n\nKey properties:\n• Keys are always unique — inserting a duplicate key overwrites the old value\n• Keys are automatically kept in sorted order (ascending by default)\n• Lookup, insertion, and deletion all take O(log n) time\n• Internally uses a balanced binary search tree (Red-Black Tree)\n\nIf you don't need sorted keys, use unordered_map instead — it uses a hash table and provides O(1) average lookup time, making it faster for most use cases.",
             "https://en.cppreference.com/w/cpp/container/map"),

            (r'set\s*<\s*(\w+)\s*>',
             "STL SET: A sorted collection of unique '{0}' values.",
             "CONCEPT: A set is a container that stores unique elements in sorted order. If you try to insert a value that already exists, the set simply ignores the duplicate — no error, no crash, it just does nothing.\n\nThis makes sets perfect for: tracking which items you've already seen, filtering duplicates from data, maintaining a sorted collection that automatically stays sorted as you add and remove items.\n\nKey operations:\n• .insert(value) — add an element (ignored if already present)\n• .erase(value) — remove an element\n• .count(value) — returns 1 if present, 0 if not (useful for checking membership)\n• .find(value) — returns an iterator to the element, or .end() if not found\n\nLike map, it uses a balanced binary search tree with O(log n) operations. For faster operations without ordering, use unordered_set.",
             "https://en.cppreference.com/w/cpp/container/set"),

            (r'stack\s*<\s*(\w+)\s*>',
             "STL STACK: A Last-In-First-Out container of '{0}' values.",
             "CONCEPT: A stack is like a stack of plates — you can only add to the top and remove from the top. The last plate placed on the stack is the first one taken off. This behavior is called LIFO (Last-In, First-Out).\n\nKey operations:\n• .push(value) — place an element on top\n• .pop() — remove the top element (but doesn't return it!)\n• .top() — look at the top element without removing it\n• .empty() — check if the stack is empty\n• .size() — how many elements are in the stack\n\nStacks are fundamental in computer science. They're used for: tracking function calls (the 'call stack'), implementing undo functionality, evaluating mathematical expressions, depth-first search (DFS) algorithms, and checking balanced parentheses.\n\nFun fact: Every time your C++ program calls a function, the computer uses a stack to remember where to return when the function finishes.",
             "https://en.cppreference.com/w/cpp/container/stack"),

            (r'queue\s*<\s*(\w+)\s*>',
             "STL QUEUE: A First-In-First-Out container of '{0}' values.",
             "CONCEPT: A queue works exactly like a real-life queue (waiting line) — the first person to join the line is the first person to be served. This behavior is called FIFO (First-In, First-Out).\n\nKey operations:\n• .push(value) — add an element to the back of the line\n• .pop() — remove the element from the front\n• .front() — look at the front element\n• .back() — look at the back element\n• .empty() — check if the queue is empty\n\nQueues are used for: task scheduling (process tasks in the order they arrive), Breadth-First Search (BFS) algorithms, printer job management, message processing systems, and any situation where fairness (first-come-first-served) matters.",
             "https://en.cppreference.com/w/cpp/container/queue"),

            (r'deque\s*<\s*(\w+)\s*>',
             "STL DEQUE: A double-ended queue of '{0}' values.",
             "CONCEPT: A deque (pronounced 'deck', short for 'Double-Ended Queue') combines the best of vectors and queues. It allows fast insertion and removal at BOTH the front and back, unlike vectors which are only fast at the back.\n\nKey operations: .push_front(), .push_back(), .pop_front(), .pop_back(), plus random access with [index] just like vectors.\n\nUse deque when you need to frequently add or remove elements from both ends. It's also useful as the underlying container for both stack and queue.",
             "https://en.cppreference.com/w/cpp/container/deque"),

            (r'list\s*<\s*(\w+)\s*>',
             "STL LIST: A doubly-linked list of '{0}' values.",
             "CONCEPT: A list is a doubly-linked list where each element stores pointers to both the next and previous elements. This makes inserting or removing elements from ANYWHERE in the list extremely fast (O(1) if you have an iterator to the position).\n\nThe trade-off: Unlike vectors and arrays, you CANNOT access elements by index (list[5] doesn't work). To reach the 5th element, you have to walk through elements 0, 1, 2, 3, 4 — which takes O(n) time.\n\nUse list when you need frequent insertions and deletions in the middle of the container and don't need random access by index.",
             "https://en.cppreference.com/w/cpp/container/list"),

            (r'unordered_map\s*<\s*(\w+)\s*,\s*(\w+)\s*>',
             "HASH MAP: An unordered dictionary linking '{0}' keys to '{1}' values.",
             "CONCEPT: An unordered_map is like a regular map (key-value pairs), but uses a hash table instead of a tree. This makes lookups, insertions, and deletions blazingly fast — O(1) average time compared to map's O(log n).\n\nThe trade-off: Elements are stored in no particular order (hence 'unordered'). If you iterate through an unordered_map, the order is unpredictable. If you need sorted keys, use regular map instead.\n\nFor most practical purposes, unordered_map should be your default choice for key-value storage unless you specifically need sorted keys.",
             "https://en.cppreference.com/w/cpp/container/unordered_map"),

            (r'unordered_set\s*<\s*(\w+)\s*>',
             "HASH SET: An unordered collection of unique '{0}' values.",
             "CONCEPT: An unordered_set is like a regular set (unique elements only), but uses a hash table for O(1) average-time operations instead of a tree's O(log n). It's the fastest way to check 'have I seen this value before?'.\n\nThe trade-off: Elements are not stored in any particular order. Use regular set if you need sorted elements.",
             "https://en.cppreference.com/w/cpp/container/unordered_set"),

            (r'pair\s*<\s*(\w+)\s*,\s*(\w+)\s*>',
             "STL PAIR: Bundling two values together — ({0} and {1}).",
             "CONCEPT: A pair is a simple container that holds exactly two values, which can be of different types. You access the first value with .first and the second with .second.\n\nPairs are used everywhere in C++: map entries are pairs (key-value), functions that need to return two values can return a pair, and algorithms like min_element/max_element return iterators that pair positions with values.\n\nCreate a pair with: pair<{0}, {1}> p = make_pair(val1, val2); or in modern C++: auto p = make_pair(val1, val2);",
             "https://en.cppreference.com/w/cpp/utility/pair"),

            (r'struct\s+(\w+)',
             "STRUCT DEFINITION: Creating a data bundle named '{0}'.",
             "CONCEPT: A struct (short for 'structure') groups related variables together into a single custom type. Think of it as creating your own data type — for example, a 'Student' struct could bundle together a name, age, and GPA into one package.\n\nStructs are very similar to classes in C++, with one key difference: everything inside a struct is 'public' by default (accessible from outside), while everything inside a class is 'private' by default.\n\nUse structs for simple data containers that just hold related values together (like a 2D point with x and y coordinates, or a color with red/green/blue values). Use classes when you need complex behavior, data hiding, and inheritance.",
             "https://en.cppreference.com/w/cpp/language/class"),

            # ==============================================================================
            # GROUP 6: CONTROL FLOW
            # ==============================================================================
            (r'if\s*\((.+)\)',
             "CONDITIONAL: Making a decision based on '{0}'.",
             "CONCEPT: The 'if' statement is the most fundamental decision-making tool in programming. It evaluates the condition inside the parentheses: if the condition is TRUE, the code inside the curly braces runs; if it's FALSE, the code is skipped entirely.\n\nThink of it like a fork in the road — the condition determines which path your program takes. The condition must produce a true/false result, typically using comparison operators:\n• == (equal to), != (not equal to)\n• < (less than), > (greater than)\n• <= (less than or equal), >= (greater than or equal)\n\nYou can combine conditions with logical operators: && (AND — both must be true), || (OR — at least one must be true), ! (NOT — flips true to false).\n\nCOMMON BEGINNER MISTAKE: Using = (assignment) instead of == (comparison) in conditions. 'if (x = 5)' SETS x to 5 and always runs! Use 'if (x == 5)' to CHECK if x equals 5.",
             "https://en.cppreference.com/w/cpp/language/if"),

            (r'else\s+if\s*\((.+)\)',
             "ALTERNATE CONDITION: Checking '{0}' since the previous condition was false.",
             "CONCEPT: 'else if' is checked ONLY when all previous 'if' and 'else if' conditions above it were false. It lets you create a chain of multiple conditions that are tested in order.\n\nThink of it like a priority checklist: 'First check if it's raining. If not, check if it's sunny. If not, check if it's cloudy.' The program checks each condition in sequence and executes the FIRST one that is true, then skips all the rest.\n\nYou can have as many 'else if' blocks as you need, and optionally end with a plain 'else' to handle the case where none of the conditions were true.",
             "https://en.cppreference.com/w/cpp/language/if"),

            (r'^\s*else\s*\{?\s*$',
             "ELSE BLOCK: Running this code when no previous condition was true.",
             "CONCEPT: The 'else' block is the 'last resort' — it runs ONLY when every 'if' and 'else if' condition above it evaluated to false. Think of it as the 'otherwise' or 'in all other cases' branch.\n\nIt catches everything that wasn't handled by the specific conditions above. Having an else block is good defensive programming — it ensures your code always does something, even in unexpected situations.",
             "https://en.cppreference.com/w/cpp/language/if"),

            (r'for\s*\(\s*(\w+)\s+(\w+)\s*:\s*(.+)\s*\)',
             "RANGE-BASED FOR LOOP: Iterating through each element of '{2}'.",
             "CONCEPT: This is the modern, cleaner way to loop through every element in a container (vector, array, string, set, map, etc.). Instead of manually tracking an index, you directly get each element one by one.\n\nFor example: 'for (int num : myVector)' goes through every number in myVector, one at a time, storing the current number in 'num'. It's equivalent to: 'for (int i = 0; i < myVector.size(); i++) {{ int num = myVector[i]; ... }}' — but much shorter and less error-prone.\n\nTIP: Use 'const auto&' for efficiency when you don't need to modify elements: 'for (const auto& item : container)'. This avoids copying each element.",
             "https://en.cppreference.com/w/cpp/language/range-for"),

            (r'for\s*\((.+)\)',
             "FOR LOOP: Repeating code with controlled iteration.",
             "CONCEPT: The 'for' loop is the workhorse of repetition in programming. It has three parts separated by semicolons:\n\n1. INITIALIZATION: Runs once before the loop starts (e.g., 'int i = 0' — start counting from 0)\n2. CONDITION: Checked before EVERY iteration — the loop continues as long as this is true (e.g., 'i < 10' — keep going while i is less than 10)\n3. UPDATE: Runs after EVERY iteration (e.g., 'i++' — add 1 to i each time)\n\nThe execution flow is: Init → Check → Body → Update → Check → Body → Update → ... until Check is false.\n\nFor example, 'for (int i = 0; i < 5; i++)' runs the body 5 times with i = 0, 1, 2, 3, 4. This is the most common loop pattern for when you know exactly how many times to repeat.\n\nCOMMON MISTAKE: Off-by-one errors. 'i < 5' runs 5 times (0-4), while 'i <= 5' runs 6 times (0-5). Be careful which one you mean!",
             "https://en.cppreference.com/w/cpp/language/for"),

            (r'while\s*\((.+)\)',
             "WHILE LOOP: Repeating as long as '{0}' remains true.",
             "CONCEPT: A 'while' loop repeats its body as long as the condition remains true. Unlike 'for' loops where you typically know the number of iterations in advance, 'while' loops are perfect when you don't know how many times to repeat — you just keep going until some condition changes.\n\nCommon use cases:\n• Reading input until the user types 'quit'\n• Processing data until you reach the end of a file\n• Searching for something until you find it\n• Games running until the player loses\n\nThe loop checks the condition BEFORE each iteration. If the condition is false from the very start, the body never executes at all.\n\nDANGER: If the condition NEVER becomes false, you get an infinite loop — your program freezes and runs forever. Always make sure something inside the loop changes the condition: 'while (x > 0) {{ x--; }}' works because x eventually reaches 0.",
             "https://en.cppreference.com/w/cpp/language/while"),

            (r'do\s*\{?',
             "DO-WHILE LOOP: Execute first, then check the condition.",
             "CONCEPT: A do-while loop is similar to a while loop, but with one crucial difference: it runs the body FIRST and checks the condition AFTER. This guarantees the body executes at least once, even if the condition is false.\n\nThis is useful when you need to perform an action before you can even check the condition. The classic example is a menu system:\ndo {\n    show_menu();\n    get_choice();\n} while (choice != 'quit');\n\nHere, you NEED to show the menu and get a choice before you can check if the user wants to quit. A regular 'while' loop would check the condition first, but 'choice' wouldn't have a value yet.",
             "https://en.cppreference.com/w/cpp/language/do"),

            (r'switch\s*\((.+)\)',
             "SWITCH STATEMENT: Branching based on the specific value of '{0}'.",
             "CONCEPT: A switch statement is a cleaner alternative to writing many 'if/else if' checks when you're comparing ONE variable against several specific values. The program 'jumps' directly to the matching case.\n\nInstead of:\nif (day == 1) ... else if (day == 2) ... else if (day == 3) ...\n\nYou write:\nswitch (day) {{ case 1: ... break; case 2: ... break; case 3: ... break; default: ... }}\n\nIMPORTANT: You MUST include 'break;' after each case! Without it, execution 'falls through' to the next case, running code you didn't intend. The 'default' case handles any value not matched by the specific cases.\n\nSwitch only works with integers, characters, and enums — NOT with strings, floats, or complex conditions.",
             "https://en.cppreference.com/w/cpp/language/switch"),

            (r'\bcase\s+(.+)\s*:',
             "CASE LABEL: Handling the specific value '{0}'.",
             "CONCEPT: This is one branch inside a switch statement. When the switch variable equals '{0}', execution jumps to this point and runs the code that follows.\n\nREMEMBER: Always end your case with 'break;' unless you intentionally want execution to 'fall through' to the next case. Forgetting 'break' is one of the most common bugs in switch statements — the code will silently continue into the next case, producing incorrect results.",
             "https://en.cppreference.com/w/cpp/language/switch"),

            (r'\bdefault\s*:',
             "DEFAULT CASE: Handling any unmatched value.",
             "CONCEPT: The 'default' case in a switch statement is the catch-all — it runs when NONE of the specific 'case' values matched. Think of it as the 'else' of a switch statement.\n\nAlways include a default case, even if you think you've covered all possibilities. It acts as a safety net for unexpected values and makes your code more robust. It's also a good place to display error messages or handle edge cases.",
             "https://en.cppreference.com/w/cpp/language/switch"),

            (r'\bbreak\s*;',
             "BREAK: Immediately exiting the current loop or switch.",
             "CONCEPT: 'break' is an emergency exit — it immediately stops the innermost loop (for, while, do-while) or switch statement and continues with the code after it.\n\nCommon uses:\n• Stopping a search loop when you find what you're looking for\n• Exiting a switch case to prevent fall-through\n• Breaking out of an infinite loop when a condition is met (while(true) { ... if(done) break; })\n\nIMPORTANT: 'break' only exits the INNERMOST loop. If you have nested loops (a loop inside another loop), break only exits the inner one. The outer loop continues running.",
             "https://en.cppreference.com/w/cpp/language/break"),

            (r'\bcontinue\s*;',
             "CONTINUE: Skipping to the next iteration of the loop.",
             "CONCEPT: 'continue' skips the rest of the current loop iteration and jumps directly to the next one. It's like saying 'never mind this one, move on to the next.'\n\nFor example, in a loop processing numbers, if you want to skip negative numbers:\nfor (int x : numbers) {\n    if (x < 0) continue;  // Skip negatives\n    process(x);  // Only positive numbers reach here\n}\n\nThe loop doesn't stop — it just skips the remaining code for this iteration and starts the next one. In a 'for' loop, the update step (i++) still runs after continue.",
             "https://en.cppreference.com/w/cpp/language/continue"),

            (r'(.+)\s*\?\s*(.+)\s*:\s*(.+)',
             "TERNARY OPERATOR: If {0} is true, use {1}; otherwise, use {2}.",
             "CONCEPT: The ternary operator is a shorthand for a simple if-else that produces a value. Instead of:\nif (condition) {{ result = valueA; }} else {{ result = valueB; }}\n\nYou can write:\nresult = condition ? valueA : valueB;\n\nIt's called 'ternary' because it has three parts: the condition, the true-value, and the false-value. Use it for simple choices. Avoid nesting ternary operators — it makes code very hard to read.",
             "https://en.cppreference.com/w/cpp/language/operator_other"),

            # ==============================================================================
            # GROUP 8: OOP — CLASSES, CONSTRUCTORS, TEMPLATES
            # ==============================================================================
            (r'template\s*<\s*(typename|class)\s+(\w+)\s*>',
             "TEMPLATE: Making code generic with placeholder type '{1}'.",
             "CONCEPT: Templates are C++'s way of writing code that works with ANY data type without rewriting it for each one. '{1}' is a placeholder — when you USE the template, you replace it with a real type like int, string, or your own class.\n\nFor example, instead of writing separate functions for finding the maximum of two ints, two doubles, and two strings, you write ONE template function:\ntemplate <typename T> T findMax(T a, T b) {{ return (a > b) ? a : b; }}\n\nNow findMax(3, 5) works with ints, findMax(3.14, 2.72) works with doubles, and findMax(\"apple\", \"banana\") works with strings — all from the same code.\n\nBehind the scenes, the compiler generates separate concrete versions for each type you actually use. Templates are the foundation of the entire Standard Template Library (STL).",
             "https://en.cppreference.com/w/cpp/language/templates"),

            (r'enum\s+class\s+(\w+)',
             "SCOPED ENUM: Creating a type-safe set of named constants '{0}'.",
             "CONCEPT: An 'enum class' (scoped enumeration) defines a set of named constant values. Unlike old-style enums, enum class values are type-safe — they don't implicitly convert to integers and don't leak their names into the surrounding scope.\n\nFor example: enum class Color {{ Red, Green, Blue }}; creates three constants accessed as Color::Red, Color::Green, Color::Blue. You can't accidentally compare Color::Red with an integer or with a value from a different enum.\n\nEnum class is the modern C++ way to define enumerations and should be preferred over plain 'enum' in all new code.",
             "https://en.cppreference.com/w/cpp/language/enum"),
            (r'class\s+(\w+)\s*:\s*(public|protected|private)\s+(\w+)',
             "INHERITANCE: '{0}' inherits from parent class '{2}'.",
             "CONCEPT: Inheritance creates an 'is-a' relationship between classes — '{0}' IS A type of '{2}'. The child class ({0}) automatically gets all the public and protected members (variables and functions) of the parent class ({2}), plus can add its own unique members.\n\nThink of it like genetics: a child inherits traits from their parents but can also have unique traits of their own. A 'Car' class could inherit from 'Vehicle', getting properties like speed and fuel level, while adding car-specific features like trunk space.\n\nThe '{1}' keyword controls what the child can access:\n• 'public' inheritance: Parent's public members stay public in the child (most common)\n• 'protected' inheritance: Parent's public members become protected in the child\n• 'private' inheritance: Parent's public members become private in the child\n\nInheritance enables code reuse and polymorphism — two of the four pillars of Object-Oriented Programming.",
             "https://en.cppreference.com/w/cpp/language/derived_class"),

            (r'class\s+(\w+)',
             "CLASS DEFINITION: Creating a blueprint for objects of type '{0}'.",
             "CONCEPT: A class is a blueprint or template for creating objects. It bundles together DATA (attributes/properties) and BEHAVIOR (methods/functions) into a single, self-contained unit. This is the foundation of Object-Oriented Programming (OOP).\n\nThink of a class like an architectural blueprint for a house. The blueprint defines what every house of this type will have (rooms, doors, windows), but it's not an actual house. When you CREATE an object from the class, that's like building an actual house from the blueprint.\n\nBy default, everything inside a class is 'private' — only the class itself can access its members. You use 'public:', 'private:', and 'protected:' sections to control who can access what.\n\nThe four pillars of OOP that classes enable:\n1. ENCAPSULATION: Hiding internal details\n2. ABSTRACTION: Showing only what's necessary\n3. INHERITANCE: Building new classes from existing ones\n4. POLYMORPHISM: Same interface, different behavior",
             "https://en.cppreference.com/w/cpp/language/class"),

            (r'public\s*:',
             "ACCESS MODIFIER: Opening access — everyone can use these members.",
             "CONCEPT: Members declared after 'public:' can be accessed by ANY code — inside the class, in derived classes, and from outside the class. These form the class's 'interface' — the buttons and controls that users of the class interact with.\n\nThink of it like a vending machine: the buttons on the front are 'public' — anyone can press them. The internal mechanics are 'private' — users can't reach inside.\n\nTypically, you make methods (functions) public so they can be called from outside, while keeping data (variables) private to protect the class's internal state from accidental corruption.",
             "https://en.cppreference.com/w/cpp/language/access"),

            (r'private\s*:',
             "ACCESS MODIFIER: Restricting access — only this class can use these members.",
             "CONCEPT: Members declared after 'private:' can ONLY be accessed from within the class itself — not by code outside the class, and not even by classes that inherit from it. This is the principle of ENCAPSULATION — hiding internal implementation details.\n\nWhy restrict access? To protect the class's internal state from being corrupted. For example, if a BankAccount class stores a balance, making it private prevents external code from directly setting 'account.balance = -1000' — instead, they must use the public withdraw() method, which can validate the amount.\n\nThis separation between 'what a class does' (public interface) and 'how it does it' (private implementation) is fundamental to good software design.",
             "https://en.cppreference.com/w/cpp/language/access"),

            (r'protected\s*:',
             "ACCESS MODIFIER: Accessible by this class and its children only.",
             "CONCEPT: 'protected' is the middle ground between public and private. Protected members can be accessed by the class itself AND by any class that inherits from it, but NOT by unrelated external code.\n\nThis is useful when you want child classes to access certain parent data or helper methods, but don't want outside code to use them directly. It's like a family secret — shared within the family (inheritance hierarchy) but not with strangers.",
             "https://en.cppreference.com/w/cpp/language/access"),

            (r'virtual\s+.*=\s*0\s*;',
             "PURE VIRTUAL FUNCTION: Forcing child classes to implement this.",
             "CONCEPT: A pure virtual function (marked with '= 0') declares 'I know this action needs to exist, but I don't know how to do it yet. Any class that inherits from me MUST provide its own implementation.'\n\nThis is ABSTRACTION — defining WHAT something should do without specifying HOW. A class with at least one pure virtual function becomes an 'abstract class' — you cannot create objects from it directly; you can only create objects from its child classes that implement all the pure virtual functions.\n\nFor example, an abstract Shape class might have 'virtual double area() = 0;' — every specific shape (Circle, Rectangle, Triangle) must define its own area calculation, but they all share the concept of having an area.",
             "https://en.cppreference.com/w/cpp/language/abstract_class"),

            (r'virtual\s+',
             "VIRTUAL FUNCTION: Enabling runtime polymorphism.",
             "CONCEPT: The 'virtual' keyword enables POLYMORPHISM — one of the most powerful features in Object-Oriented Programming. It tells the compiler: 'Don't decide which version of this function to call at compile time. Wait until the program is actually running to see what type of object is really being used.'\n\nWhy does this matter? Imagine you have a parent class 'Animal' with a virtual function 'speak()'. A Dog overrides it to bark, a Cat overrides it to meow. If you have an 'Animal*' pointer, calling speak() through that pointer calls the RIGHT version (bark or meow) based on what the object ACTUALLY is — not what the pointer type says.\n\nWithout 'virtual', the compiler would always call the parent's version, ignoring the child's override. This is called 'static binding' vs 'dynamic binding'.",
             "https://en.cppreference.com/w/cpp/language/virtual"),

            (r'override\b',
             "OVERRIDE: Explicitly marking that this function replaces a parent's virtual function.",
             "CONCEPT: The 'override' keyword is a safety check. It tells the compiler: 'I intend this function to replace a virtual function from the parent class. If there's no matching virtual function in the parent, give me an error.'\n\nWithout 'override', if you accidentally misspell the function name or use wrong parameter types, the compiler silently creates a NEW function instead of overriding the parent's — a very sneaky bug. 'override' catches this mistake at compile time.\n\nAlways use 'override' when overriding virtual functions. It's a modern C++ best practice that prevents subtle inheritance bugs.",
             "https://en.cppreference.com/w/cpp/language/override"),

            (r'friend\s+',
             "FRIEND DECLARATION: Granting private access to an outsider.",
             "CONCEPT: The 'friend' keyword breaks the normal access rules by letting a specific external function or class access this class's private and protected members. It's like giving a trusted friend a key to your house.\n\nFriend declarations should be used sparingly because they create tight coupling between classes. Common legitimate uses include: operator overloading (especially << for output), factory functions, and test classes.\n\nIMPORTANT: Friendship is granted by the class being accessed, not requested by the accessor. Friendship is not inherited (your friend's children don't get keys) and is not mutual (giving you my key doesn't give me yours).",
             "https://en.cppreference.com/w/cpp/language/friend"),

            (r'static\s+',
             "STATIC: Shared across all instances or persistent across calls.",
             "CONCEPT: 'static' has different meanings depending on context:\n\n• INSIDE A CLASS: A static member belongs to the CLASS itself, not to individual objects. All objects share the same static member. For example, a static 'count' variable could track how many objects have been created.\n\n• INSIDE A FUNCTION: A static local variable is initialized only once (the first time the function is called) and remembers its value between calls. Normally, local variables are destroyed when the function ends — static ones persist.\n\n• AT FILE SCOPE: A static global variable or function is visible only within its source file, preventing name conflicts with other files.\n\nStatic is a versatile keyword that essentially means 'shared' or 'persistent' depending on context.",
             "https://en.cppreference.com/w/cpp/language/static"),

            (r'this\s*->',
             "THIS POINTER: Referring to the current object's own member.",
             "CONCEPT: 'this' is a hidden pointer that every non-static member function receives automatically. It points to the specific object that the function was called on. 'this->' makes it explicit that you're accessing THIS object's member, not a local variable or parameter with the same name.\n\nThe most common use is to disambiguate when a parameter has the same name as a member variable:\nvoid setName(string name) {{ this->name = name; }}  // 'this->name' is the member, 'name' is the parameter\n\n'this' is also used to return the current object from a function (return *this;) for method chaining.",
             "https://en.cppreference.com/w/cpp/language/this"),

            (r'namespace\s+(\w+)\s*\{',
             "NAMESPACE: Creating a named scope '{0}' to avoid naming conflicts.",
             "CONCEPT: A namespace is like a folder for your code — it groups related functions, classes, and variables under a unique name to prevent conflicts. Just like you can have files with the same name in different folders, you can have functions with the same name in different namespaces.\n\nFor example, two libraries might both define a 'sort()' function. By putting them in different namespaces (LibA::sort() and LibB::sort()), you can use both without conflict.\n\nThe entire C++ standard library lives in the 'std' namespace — that's why you see 'std::cout', 'std::vector', etc. Defining your own namespaces is good practice for larger projects.",
             "https://en.cppreference.com/w/cpp/language/namespace"),

            (r'~(\w+)\s*\(',
             "DESTRUCTOR: Cleanup function for class '{0}'.",
             "CONCEPT: A destructor is the opposite of a constructor — it's automatically called when an object is destroyed (goes out of scope, is deleted, etc.). Its job is to clean up any resources the object acquired during its lifetime: freeing dynamic memory, closing files, releasing network connections, etc.\n\nDestructors are marked with a ~ (tilde) before the class name. A class can only have ONE destructor, and it takes no parameters.\n\nIf your class uses 'new' to allocate memory, you MUST write a destructor that uses 'delete' to free it. Otherwise, every time an object is destroyed, that memory is leaked. This is the basis of the RAII (Resource Acquisition Is Initialization) pattern — one of C++'s most important idioms.",
             "https://en.cppreference.com/w/cpp/language/destructor"),

            (r'operator\s*([+\-*/%=<>!&|^~\[\]]+)',
             "OPERATOR OVERLOAD: Defining custom behavior for the '{0}' operator.",
             "CONCEPT: Operator overloading lets you define what standard operators (+, -, ==, <<, etc.) mean for YOUR custom classes. For example, you can make the + operator add two 'Vector2D' objects component-wise, or make the == operator compare two 'Student' objects by their ID.\n\nThis makes custom types feel as natural as built-in types. Instead of calling 'v1.add(v2)', you can write 'v1 + v2' — much more readable.\n\nRules:\n• You can't create new operators — only redefine existing ones\n• You can't change the number of operands (+ always takes two)\n• Some operators can't be overloaded (::, ., .*, ?:)\n• At least one operand must be a user-defined type (you can't redefine int + int)",
             "https://en.cppreference.com/w/cpp/language/operators"),
            # ==============================================================================
            # GROUP 7: FUNCTIONS & I/O
            # ==============================================================================
            (r'^\s*int\s+main\s*\(\s*(void)?\s*\)\s*\{?\s*$',
             "MAIN FUNCTION: The starting point of your C++ program.",
             "CONCEPT: Every C++ program must have exactly one main() function — it's where the program begins executing. When you run a compiled C++ program, the operating system finds main() and starts running the code inside it from top to bottom.\n\nThe 'int' before main means the function returns an integer to the operating system when the program finishes. By convention, returning 0 means success, and any other number indicates an error.\n\nEverything your program does — reading input, computing results, printing output — happens inside main() or inside functions that main() calls.",
             "https://en.cppreference.com/w/cpp/language/main_function"),
            (r'cin\s*>>\s*(.*);',
             "INPUT: Reading user input into '{0}'.",
             "CONCEPT: 'cin' (short for 'Console Input') reads data from the keyboard and stores it in a variable. The >> arrows (extraction operator) point toward where the data is going — from the keyboard INTO your variable.\n\nKey behaviors:\n• cin automatically determines the type — if the variable is int, it reads a number; if string, it reads text\n• cin stops reading at whitespace (space, tab, newline). So if the user types 'John Smith', cin >> name only captures 'John'\n• If the user enters wrong data (text when expecting a number), cin enters an error state and stops working until you clear it\n\nTo read an entire line including spaces, use getline(cin, variable) instead of cin >>.\n\nTIP: You can chain input: 'cin >> name >> age;' reads two values in one line.",
             "https://en.cppreference.com/w/cpp/io/cin"),

            (r'cout\s*<<\s*(.*);',
             "OUTPUT: Displaying '{0}' to the screen.",
             "CONCEPT: 'cout' (short for 'Console Output') sends data from your program to the screen. The << arrows (insertion operator) point away from the program toward the output — from your program OUT to the screen.\n\nYou can chain multiple outputs: 'cout << \"Name: \" << name << \", Age: \" << age << endl;' This prints everything in sequence on one line.\n\nKey notes:\n• 'endl' adds a new line AND flushes the output buffer (forces the text to appear immediately)\n• '\\n' adds a new line without flushing (slightly faster but may delay output)\n• You can output any type: numbers, characters, strings, and even expressions like 'cout << 2 + 3'\n\nRemember: cout doesn't add spaces or newlines automatically — you must add them yourself where you want them.",
             "https://en.cppreference.com/w/cpp/io/cout"),

            (r'getline\s*\(\s*cin\s*,\s*(\w+)\s*\)',
             "LINE INPUT: Reading an entire line of text into '{0}'.",
             "CONCEPT: While 'cin >>' stops reading at the first space, getline() reads the ENTIRE line until the user presses Enter, including all spaces. This is essential when you need to read full names, addresses, sentences, or any text with spaces.\n\nWARNING: If you use cin >> before getline(), there's a common trap — cin leaves a newline character in the input buffer, and getline immediately reads that leftover newline as an empty string. Fix this by adding 'cin.ignore()' between cin >> and getline().",
             "https://en.cppreference.com/w/cpp/string/basic_string/getline"),

            (r'cerr\s*<<',
             "ERROR OUTPUT: Sending an error message to the error stream.",
             "CONCEPT: 'cerr' works like cout but writes to the standard error stream instead of the standard output stream. The error stream is typically displayed on the screen just like cout, but it can be redirected separately.\n\nThis is useful for error messages and debugging information — even if someone redirects your program's normal output to a file, error messages sent through cerr will still appear on the screen.\n\ncerr is also unbuffered, meaning messages appear immediately without waiting for the buffer to fill.",
             "https://en.cppreference.com/w/cpp/io/cerr"),

            (r'void\s+(\w+)\s*\(',
             "VOID FUNCTION: An action function '{0}' that performs a task without returning a value.",
             "CONCEPT: A 'void' function performs an action but doesn't produce a result that you can store or use. Think of the difference between asking someone 'What is 2+2?' (returns a value: 4) versus 'Please clean the room' (performs an action but doesn't give you a number back).\n\nVoid functions are used for tasks like: printing output to the screen, modifying data structures, writing to files, or any operation where you don't need a result back.\n\nInside a void function, you can use 'return;' (without a value) to exit the function early, but you cannot use 'return 42;' because void means 'I promise not to return anything.'",
             "https://en.cppreference.com/w/cpp/language/functions"),

            (r'\b(int|double|float|long long|bool|char|string)\s+(\w+)\s*\(([^)]*)\)\s*\{?',
             "FUNCTION DEFINITION: Creating function '{1}' that returns {0} and takes ({2}).",
             "CONCEPT: A function is a reusable block of code that performs a specific task. Think of it like a recipe — you define it once, then 'call' it whenever you need that task done.\n\nThis function has three key parts:\n• Return type '{0}': What kind of result the function gives back when it finishes\n• Name '{1}': How you refer to and call this function from other parts of your code\n• Parameters '({2})': The inputs the function needs to do its job\n\nFunctions are the building blocks of well-organized code. Instead of writing the same logic multiple times, you write it once in a function and call it wherever needed. This makes code shorter, easier to test, and easier to maintain.\n\nWhen the function finishes, it uses 'return' to send a value of type '{0}' back to wherever it was called from.",
             "https://en.cppreference.com/w/cpp/language/functions"),

            (r'return\s+0\s*;',
             "SUCCESS EXIT: Signaling that the program finished correctly.",
             "CONCEPT: In the main() function, 'return 0' is the universal standard for telling the operating system: 'Everything went well, no errors occurred.' The operating system reads this code — scripts and other programs can check it to know if your program succeeded.\n\nBy convention:\n• 0 = success (no errors)\n• Any non-zero value = failure (something went wrong)\n\nIn modern C++, the main() function automatically returns 0 if you don't write a return statement. However, explicitly writing 'return 0;' is considered good practice for clarity.",
             "https://en.cppreference.com/w/cpp/language/return"),

            (r'return\s+(.+);',
             "RETURN VALUE: Sending the result '{0}' back to the caller.",
             "CONCEPT: The 'return' statement does two things:\n1. It specifies the VALUE that the function gives back to whatever code called it\n2. It IMMEDIATELY exits the function — any code after the return statement is never reached\n\nFor example, if a function calculates the area of a rectangle, 'return length * width;' sends the calculated area back to wherever the function was called. The caller can then store or use that value: 'double area = calculateArea(5, 3);'.\n\nThe returned value must match the function's declared return type. A function declared as 'int add(...)' must return an integer, not a string or double.",
             "https://en.cppreference.com/w/cpp/language/return"),

            
            # ==============================================================================
            # GROUP 9: EXCEPTION HANDLING
            # ==============================================================================
            (r'try\s*\{?',
             "TRY BLOCK: Attempting code that might fail.",
             "CONCEPT: A try block wraps code that might throw an exception — an error that disrupts the normal flow of the program. Think of it as saying 'try to do this, but if something goes wrong, I have a plan.'\n\nWithout try-catch, errors like dividing by zero, accessing invalid memory, or opening a non-existent file would crash your program. With try-catch, you can handle these errors gracefully — show a message, retry the operation, or use a default value.\n\nThe try block is always paired with one or more 'catch' blocks that specify how to handle different types of errors.",
             "https://en.cppreference.com/w/cpp/language/try_catch"),

            (r'catch\s*\((.+)\)',
             "CATCH BLOCK: Handling an error of type '{0}'.",
             "CONCEPT: A catch block defines what to do when a specific type of error occurs in the preceding try block. You can have multiple catch blocks to handle different error types differently.\n\n'catch (exception& e)' catches standard library exceptions and lets you access the error message with e.what(). 'catch (...)' catches ANY exception — it's a catch-all safety net.\n\nBest practice: Catch specific exception types first (like out_of_range, invalid_argument), then broader types (exception), and optionally catch(...) last as a final safety net.\n\nIMPORTANT: Catch exceptions by reference (exception& e), not by value, to avoid slicing and unnecessary copying.",
             "https://en.cppreference.com/w/cpp/language/try_catch"),

            (r'throw\s+',
             "THROW: Raising an error signal.",
             "CONCEPT: 'throw' immediately stops the current function and sends an error (exception) up to the nearest try-catch block. If no try-catch is found, the entire program terminates.\n\nThink of it like pulling a fire alarm — everything stops immediately and control transfers to the emergency handler (catch block). Any cleanup code after the throw statement is NOT executed.\n\nYou can throw any type, but it's best practice to throw standard exception types (std::runtime_error, std::invalid_argument, etc.) or your own classes derived from std::exception.",
             "https://en.cppreference.com/w/cpp/language/throw"),

            # ==============================================================================
            # GROUP 10: FILE I/O
            # ==============================================================================
            (r'ifstream\s+(\w+)',
             "FILE INPUT: Opening a file for reading with stream '{0}'.",
             "CONCEPT: 'ifstream' (Input File Stream) opens a file so your program can read data from it — like opening a book to read its contents. You use the same >> operator you use with cin.\n\nTypical usage:\nifstream file(\"data.txt\");\nif (file.is_open()) {{ string line; while (getline(file, line)) {{ /* process line */ }} file.close(); }}\n\nAlways check .is_open() before reading — the file might not exist, or you might not have permission to read it. Always .close() the file when done (though it closes automatically when the ifstream goes out of scope).",
             "https://en.cppreference.com/w/cpp/io/basic_ifstream"),

            (r'ofstream\s+(\w+)',
             "FILE OUTPUT: Opening a file for writing with stream '{0}'.",
             "CONCEPT: 'ofstream' (Output File Stream) opens a file so your program can write data to it — like opening a notebook to write in it. You use the same << operator you use with cout.\n\nBy default, ofstream OVERWRITES the file (deletes old content). To APPEND (add to the end), open with: ofstream file(\"log.txt\", ios::app);\n\nTypical usage:\nofstream file(\"output.txt\");\nfile << \"Hello, File!\" << endl;\nfile.close();\n\nIf the file doesn't exist, ofstream creates it automatically. Always close the file when done to ensure all data is actually written to disk.",
             "https://en.cppreference.com/w/cpp/io/basic_ofstream"),

            (r'fstream\s+(\w+)',
             "FILE I/O: Opening a file for both reading and writing with stream '{0}'.",
             "CONCEPT: 'fstream' (File Stream) can both read from AND write to a file — it combines the capabilities of ifstream and ofstream. Use this when you need to modify a file's contents or read and write in the same operation.\n\nYou need to specify the mode when opening: fstream file(\"data.txt\", ios::in | ios::out);\n\nMost of the time, you'll use ifstream or ofstream separately, which is simpler and clearer about your intent.",
             "https://en.cppreference.com/w/cpp/io/basic_fstream"),

            # ==============================================================================
            # GROUP 11: MISCELLANEOUS MODERN C++
            # ==============================================================================
            (r'typedef\s+(\w+)\s+(\w+)',
             "TYPE ALIAS: Creating a shorthand name '{1}' for type '{0}'.",
             "CONCEPT: 'typedef' creates a new name (alias) for an existing type. It doesn't create a new type — it just gives you a shorter or more meaningful name to use.\n\nFor example: 'typedef long long ll;' lets you write 'l' instead of 'long long' everywhere. This is popular in competitive programming for brevity.\n\nIn modern C++, the 'using' keyword is preferred: 'using ll = long long;' does the same thing with clearer syntax.",
             "https://en.cppreference.com/w/cpp/language/typedef"),

            (r'using\s+(\w+)\s*=\s*(.+);',
             "TYPE ALIAS: Creating name '{0}' as a shorthand for '{1}'.",
             "CONCEPT: The 'using' declaration creates a type alias — a new name for an existing type. This is the modern C++ way to create type aliases, replacing the older 'typedef' syntax.\n\nFor example: 'using Matrix = vector<vector<int>>;' lets you write 'Matrix grid;' instead of 'vector<vector<int>> grid;' — much more readable.\n\nThis is especially valuable with complex template types that would otherwise make your code hard to read.",
             "https://en.cppreference.com/w/cpp/language/type_alias"),

            (r'sizeof\s*\(\s*(\w+)\s*\)',
             "SIZE QUERY: Getting the memory size of '{0}' in bytes.",
             "CONCEPT: 'sizeof' tells you exactly how many bytes of memory a type or variable occupies. It's evaluated at compile time (not at runtime), so it has zero performance cost.\n\nCommon sizes (may vary by system): char = 1 byte, int = 4 bytes, double = 8 bytes, pointer = 4 or 8 bytes.\n\nsizeof is useful for: calculating array lengths (sizeof(arr)/sizeof(arr[0])), ensuring data fits in specific memory constraints, and understanding memory layout.",
             "https://en.cppreference.com/w/cpp/language/sizeof"),

            (r'static_cast\s*<\s*(\w+)\s*>',
             "STATIC CAST: Explicitly converting to type '{0}'.",
             "CONCEPT: static_cast performs a type conversion at compile time. It's the safest and most common way to convert between related types: int to double, double to int, enum to int, etc.\n\nFor example: 'double avg = static_cast<double>(sum) / count;' converts sum to double before dividing, preventing integer division truncation.\n\nC++ has four cast types: static_cast (general conversions), dynamic_cast (safe downcasting with runtime check), const_cast (remove/add const), and reinterpret_cast (dangerous raw bit reinterpretation). Use static_cast for most situations.",
             "https://en.cppreference.com/w/cpp/language/static_cast"),

            (r'dynamic_cast\s*<\s*([^>]+)\s*>',
             "DYNAMIC CAST: Safe runtime type conversion to '{0}'.",
             "CONCEPT: dynamic_cast performs a type conversion with a runtime safety check. It's used for safe downcasting in inheritance hierarchies — converting a parent pointer to a child pointer, with verification that the object really is the child type.\n\nIf the conversion is invalid, dynamic_cast returns nullptr (for pointers) or throws std::bad_cast (for references), letting you handle the error gracefully instead of crashing.\n\nThis requires the class hierarchy to have at least one virtual function (polymorphic types).",
             "https://en.cppreference.com/w/cpp/language/dynamic_cast"),

            (r'\[([^\]]*)\]\s*\(([^)]*)\)\s*(\{|->)',
             "LAMBDA EXPRESSION: Creating an anonymous inline function.",
             "CONCEPT: A lambda is a function without a name — defined right where you need it. Lambdas are perfect for short, one-off operations, especially as arguments to algorithms like sort(), find_if(), and for_each().\n\nThe syntax has three parts:\n• [captures] — which outside variables the lambda can access\n• (parameters) — the inputs, like regular function parameters\n• {{ body }} — the code to execute\n\nExample: sort(v.begin(), v.end(), [](int a, int b) {{ return a > b; }}); — sorts in descending order using an inline comparison function.\n\nCapture modes: [=] copies all outside variables, [&] references all, [x] copies x, [&x] references x, [] captures nothing.",
             "https://en.cppreference.com/w/cpp/language/lambda"),

            
            (r'enum\s+(\w+)',
             "ENUM: Creating a set of named integer constants '{0}'.",
             "CONCEPT: An enum (enumeration) creates a set of named constant values that represent related options. Instead of using raw numbers (0, 1, 2) which are meaningless, you use descriptive names (Monday, Tuesday, Wednesday).\n\nFor example: enum Direction {{ North, South, East, West }}; lets you write 'Direction d = North;' instead of 'int d = 0;' — much more readable.\n\nBy default, values start at 0 and increment by 1 (North=0, South=1, etc.), but you can assign custom values: enum Status {{ OK=200, NotFound=404, Error=500 }}.\n\nNote: In modern C++, 'enum class' is preferred because it provides type safety and scope isolation.",
             "https://en.cppreference.com/w/cpp/language/enum"),

            # ==============================================================================
            # GROUP 12: COMMON STL METHOD CALLS
            # ==============================================================================
            (r'\.\s*push_back\s*\(',
             "VECTOR APPEND: Adding an element to the end of the container.",
             "CONCEPT: .push_back() adds a new element to the END of a vector (or deque/list). The container automatically grows to accommodate the new element. This is the most common way to build up a vector element by element.\n\nFor example: vector<int> nums; nums.push_back(10); nums.push_back(20); creates a vector containing [10, 20].\n\nPerformance: push_back is very fast — O(1) amortized time. Occasionally, when the vector runs out of internal space, it needs to reallocate and copy everything, but this happens rarely enough that the average cost stays constant.",
             "https://en.cppreference.com/w/cpp/container/vector/push_back"),

            (r'\.\s*pop_back\s*\(',
             "VECTOR REMOVE LAST: Removing the last element from the container.",
             "CONCEPT: .pop_back() removes the last element from a vector (or deque/list). The container shrinks by one element. Note that pop_back() does NOT return the removed value — if you need the value, read it with .back() BEFORE calling pop_back().\n\nWARNING: Calling pop_back() on an empty container causes undefined behavior — always check .empty() first.",
             "https://en.cppreference.com/w/cpp/container/vector/pop_back"),

            (r'\.\s*size\s*\(\s*\)',
             "SIZE QUERY: Getting the number of elements in the container.",
             "CONCEPT: .size() returns how many elements are currently stored in the container. This works on vectors, strings, maps, sets, lists, deques, and virtually all standard containers.\n\nThe return type is 'size_t' (an unsigned integer), which means it can never be negative. Be careful when comparing .size() with signed integers — the compiler may warn about signed/unsigned comparison.\n\nTIP: Use .empty() instead of .size() == 0 to check for emptiness — it's more readable and potentially more efficient.",
             "https://en.cppreference.com/w/cpp/container/vector/size"),

            (r'\.\s*empty\s*\(\s*\)',
             "EMPTY CHECK: Checking if the container has no elements.",
             "CONCEPT: .empty() returns true if the container has zero elements, false otherwise. It's the recommended way to check if a container is empty — clearer and potentially faster than checking .size() == 0.\n\nAlways check .empty() before calling .front(), .back(), .top(), or .pop() on containers that don't allow these operations on empty containers.",
             "https://en.cppreference.com/w/cpp/container/vector/empty"),

            (r'\.\s*begin\s*\(\s*\)',
             "ITERATOR BEGIN: Getting a pointer to the first element.",
             "CONCEPT: .begin() returns an iterator pointing to the FIRST element of the container. Iterators are like smart pointers that know how to walk through a container element by element.\n\nIterators are used extensively with algorithms: sort(v.begin(), v.end()) sorts the entire vector from first to last element. The range [begin, end) is a half-open range — begin is included, end is excluded.\n\nYou can dereference an iterator with * to get the value: *v.begin() gives the first element (same as v[0] for vectors).",
             "https://en.cppreference.com/w/cpp/container/vector/begin"),

            (r'\.\s*end\s*\(\s*\)',
             "ITERATOR END: Getting a pointer past the last element.",
             "CONCEPT: .end() returns an iterator pointing to the position AFTER the last element — not to the last element itself. This might seem strange, but it makes loops and algorithms cleaner.\n\nThe range [begin(), end()) defines all elements in the container. Standard loop: for (auto it = v.begin(); it != v.end(); ++it) — the loop runs while the iterator hasn't reached the 'past-the-end' position.\n\nNEVER dereference .end() — it doesn't point to a valid element. It's only used as a boundary marker.",
             "https://en.cppreference.com/w/cpp/container/vector/end"),

            (r'sort\s*\(',
             "SORT ALGORITHM: Arranging elements in order.",
             "CONCEPT: sort() rearranges elements in ascending order by default. It's one of the most commonly used algorithms in C++ and is highly optimized (uses IntroSort — a hybrid of QuickSort, HeapSort, and InsertionSort).\n\nUsage: sort(v.begin(), v.end()); sorts the entire vector in ascending order.\n\nFor descending order: sort(v.begin(), v.end(), greater<int>());\nOr with a lambda: sort(v.begin(), v.end(), [](int a, int b) {{ return a > b; }});\n\nPerformance: O(n log n) average and worst case — very efficient. Don't write your own sorting algorithm unless you have a very specific reason; sort() is almost certainly faster.",
             "https://en.cppreference.com/w/cpp/algorithm/sort"),

            (r'reverse\s*\(',
             "REVERSE ALGORITHM: Flipping the order of elements.",
             "CONCEPT: reverse() flips the order of elements in a range — the first becomes last, the second becomes second-to-last, and so on.\n\nUsage: reverse(v.begin(), v.end()); reverses the entire vector.\nYou can also reverse a substring: reverse(s.begin() + 2, s.begin() + 5);",
             "https://en.cppreference.com/w/cpp/algorithm/reverse"),

            # ==============================================================================
            # GROUP 2: ARRAYS (Must come BEFORE standard variables to prevent misclassification)
            # ==============================================================================
            (r'char\s+(\w+)\[\]\s*=\s*"(.*)"\s*;',
             "C-STYLE STRING: A character array '{0}' initialized with text \"{1}\".",
             "CONCEPT: This creates a C-style string — the old way of handling text in C++. A string literal like \"{1}\" is actually stored as an array of individual characters, with a special invisible character called the 'null terminator' (\\0) added at the end to mark where the string stops.\n\nFor example, \"Hi\" is actually stored as: ['H', 'i', '\\0'] — 3 characters, not 2. The null terminator is how functions like strlen() know where the string ends.\n\nWhile this approach works, modern C++ strongly recommends using std::string instead, which handles memory management automatically and provides many convenient methods like .length(), .find(), and .substr().",
             "https://en.cppreference.com/w/cpp/language/string_literal"),

            (r'(\w+)\s+(\w+)\[(\d+)\]',
             "ARRAY DECLARATION: Creating a fixed-size list '{1}' that holds {2} items of type '{0}'.",
             "CONCEPT: An array is one of the most fundamental data structures in programming. Think of it as a row of numbered boxes, where each box holds one value. Here, you are creating {2} boxes, each capable of holding one '{0}' value, and naming the entire row '{1}'.\n\nIMPORTANT RULES:\n• All boxes must hold the same type of data (all integers, all floats, etc.)\n• The size ({2}) is fixed forever — you cannot add more boxes later\n• Boxes are numbered starting from 0, not 1 (so {1}[0] is the first box, {1}[{2}-1] is the last)\n• Accessing a box number that doesn't exist (like {1}[{2}]) causes 'undefined behavior' — your program might crash, give garbage values, or corrupt other data\n\nIf you need a list that can grow and shrink, use a vector instead: vector<{0}> {1};",
             "https://en.cppreference.com/w/cpp/language/array"),

            (r'(\w+)\s+(\w+)\[\]\s*=\s*\{(.*)\}',
             "ARRAY INITIALIZATION: Creating array '{1}' and filling it with values: {{ {2} }}.",
             "CONCEPT: This creates an array AND fills it with initial values at the same time. When you provide values inside the curly braces {{ }}, C++ automatically counts them to determine the array's size — you don't need to specify the number in the brackets.\n\nFor example, 'int scores[] = {{90, 85, 77}}' creates an array of 3 integers. This is the safest way to create arrays because the size exactly matches the number of values you provide, making it impossible to accidentally leave boxes uninitialized.\n\nNote: Uninitialized array elements contain 'garbage values' — random leftover data from whatever was in that memory before. Always initialize your arrays!",
             "https://en.cppreference.com/w/cpp/language/array"),

            (r'(\w+)\[(.+)\]',
             "ARRAY ACCESS: Accessing position [{1}] in array '{0}'.",
             "CONCEPT: This accesses a specific element in the array '{0}' at the position (index) indicated by '{1}'. Remember that C++ uses ZERO-BASED INDEXING — the first element is at position [0], the second at [1], and so on.\n\nThis is one of the most common operations in programming. You can use array access to both READ a value (like 'cout << {0}[{1}]') and WRITE a value (like '{0}[{1}] = 42').\n\nCRITICAL WARNING: If you access an index outside the valid range, C++ does NOT stop you or give an error message. Instead, you get 'undefined behavior' — your program might read random garbage from memory, crash, or even appear to work correctly but produce wrong results. This is one of the most common and dangerous bugs in C/C++ programming. Use vectors with .at() for bounds-checked access during development.",
             "https://en.cppreference.com/w/cpp/language/operator_member_access"),

            # ==============================================================================
            # GROUP 3: DATA TYPES & VARIABLES
            # ==============================================================================
            (r'\b(const)\s+',
             "CONSTANT: Making a value that can never change.",
             "CONCEPT: The 'const' keyword is a promise to the compiler — and to anyone reading your code — that this value will NEVER be modified after it is created. If any code later tries to change it, the compiler will refuse to compile and show an error.\n\nWhy use const? Three important reasons:\n1. SAFETY: It prevents accidental modifications. If you know a value should never change (like the number of days in a week), marking it const catches bugs at compile time.\n2. READABILITY: When other programmers see 'const', they immediately know this value is fixed, making the code easier to understand.\n3. OPTIMIZATION: The compiler can sometimes generate faster code when it knows a value won't change.\n\nExample: 'const double PI = 3.14159;' — PI should never change, so const protects it.",
             "https://en.cppreference.com/w/cpp/language/cv"),

            (r'\b(int|long long)\s+(\w+)(?!\s*\[)',
             "INTEGER VARIABLE: Creating a whole number variable '{1}' (type: {0}).",
             "CONCEPT: This creates a variable that can store whole numbers (no decimal points). '{0}' determines the range of numbers it can hold:\n\n• 'int' (32-bit): Stores numbers from about -2.1 billion to +2.1 billion. This is the most commonly used integer type and should be your default choice for most situations.\n• 'long long' (64-bit): Stores much larger numbers — up to about 9.2 quintillion (9,200,000,000,000,000,000). Use this when you're working with very large numbers, such as in competitive programming or financial calculations.\n\nIMPORTANT: If you try to store a decimal number like 3.7 in an integer variable, the decimal part is silently chopped off — you get 3, not 4. This is called 'truncation', and it's a common source of bugs for beginners. If you need decimals, use 'double' instead.",
             "https://en.cppreference.com/w/cpp/language/types"),

            (r'\b(float|double)\s+(\w+)(?!\s*\[)',
             "DECIMAL VARIABLE: Creating a decimal number variable '{1}' (type: {0}).",
             "CONCEPT: This creates a variable that can store numbers with decimal points (like 3.14, -0.5, or 1000.0). '{0}' determines the precision:\n\n• 'double' (64-bit): The default choice for decimal numbers. It provides about 15-16 significant digits of precision. Use this unless you have a specific reason not to.\n• 'float' (32-bit): Uses half the memory but only gives about 6-7 significant digits of precision. Only use float when memory is extremely limited (like embedded systems or processing millions of values).\n\nIMPORTANT WARNING: Computers cannot store most decimal numbers perfectly — they use a binary approximation. This means 0.1 + 0.2 might equal 0.30000000000000004 instead of 0.3. Never compare decimal numbers with == directly. Instead, check if the difference is very small: abs(a - b) < 0.0001.",
             "https://en.cppreference.com/w/cpp/language/types"),

            (r'\b(char)\s+(\w+)(?!\s*\[)',
             "CHARACTER VARIABLE: Storing a single character in '{1}'.",
             "CONCEPT: A 'char' variable holds exactly one character — a single letter, digit, symbol, or space. Characters in C++ are always enclosed in SINGLE quotes: 'A', '7', '$', ' '.\n\nBehind the scenes, computers don't actually store letters. Instead, each character is mapped to a number using the ASCII table. For example: 'A' = 65, 'B' = 66, 'a' = 97, '0' = 48, ' ' = 32. This means you can actually do math with characters! 'A' + 1 gives you 'B', and 'a' - 'A' gives you 32 (the difference between uppercase and lowercase).\n\nIMPORTANT: Don't confuse single quotes (for char: 'A') with double quotes (for strings: \"Hello\"). They are completely different types in C++.",
             "https://en.cppreference.com/w/cpp/language/types"),

            (r'\b(bool)\s+(\w+)(?!\s*\[)',
             "BOOLEAN VARIABLE: A true/false switch named '{1}'.",
             "CONCEPT: A boolean (bool) is the simplest type of variable — it can only hold one of two values: 'true' or 'false'. Think of it like a light switch that is either ON (true) or OFF (false).\n\nBooleans are the backbone of decision-making in programming. Every 'if' statement, every 'while' loop condition, and every comparison ultimately produces a boolean result. For example, 'x > 5' produces true if x is greater than 5, and false otherwise.\n\nINTERNALLY: C++ treats false as 0 and true as 1 (or any non-zero value). This means you can use integers where booleans are expected: 'if (1)' always executes (true), while 'if (0)' never does (false). However, using explicit true/false makes your code much clearer.",
             "https://en.cppreference.com/w/cpp/language/types"),

            (r'\b(string)\s+(\w+)(?!\s*\[)',
             "STRING VARIABLE: A text variable named '{1}'.",
             "CONCEPT: A string is a sequence of characters — essentially a word, sentence, or any piece of text. Unlike 'char' which holds just one character, a string can hold text of any length, and it automatically manages its own memory (growing and shrinking as needed).\n\nStrings are enclosed in DOUBLE quotes: \"Hello, World!\". You can combine strings using the + operator (\"Hello\" + \" World\" gives \"Hello World\"), compare them with == and <, access individual characters with [index], find substrings with .find(), get the length with .length(), and much more.\n\nDon't forget to #include <string> at the top of your file to use string variables (though some compilers include it automatically through iostream).",
             "https://en.cppreference.com/w/cpp/string/basic_string"),

            (r'\bauto\s+(\w+)\s*=',
             "AUTO TYPE: Letting the compiler figure out the type of '{0}'.",
             "CONCEPT: The 'auto' keyword tells the compiler: 'You can see what value I'm assigning — figure out the type yourself.' For example, 'auto x = 5' makes x an int, 'auto pi = 3.14' makes pi a double, and 'auto name = \"Alice\"' makes name a string.\n\nThis is especially useful with complex types. Instead of writing 'map<string, vector<int>>::iterator it = myMap.begin()', you can simply write 'auto it = myMap.begin()'. The compiler knows exactly what type 'it' should be.\n\nBest practice: Use auto when the type is obvious from context or when the full type name is very long. Don't use it when it makes the code harder to understand — 'auto x = calculate()' doesn't tell the reader what type x is.",
             "https://en.cppreference.com/w/cpp/language/auto"),
            # ==============================================================================
            # GROUP 13: OPERATORS & ASSIGNMENTS
            # ==============================================================================
            (r'(\w+)\s*\+=\s*(.+);',
             "ADD-ASSIGN: Adding {1} to {0} (same as {0} = {0} + {1}).",
             "CONCEPT: The += operator is a shorthand for adding a value to a variable and storing the result back in the same variable. Writing 'x += 5' is exactly the same as writing 'x = x + 5', but shorter and cleaner.\n\nSimilar compound operators exist for all arithmetic: -= (subtract), *= (multiply), /= (divide), %= (modulo). These are used extremely often in loops and accumulation patterns.",
             "https://en.cppreference.com/w/cpp/language/operator_assignment"),

            (r'(\w+)\s*-=\s*(.+);',
             "SUBTRACT-ASSIGN: Subtracting {1} from {0} (same as {0} = {0} - {1}).",
             "CONCEPT: The -= operator subtracts a value from a variable and stores the result back. Writing 'x -= 3' is exactly the same as 'x = x - 3'. This is a compound assignment operator — a common shorthand in C++ that makes code more concise.",
             "https://en.cppreference.com/w/cpp/language/operator_assignment"),

            (r'(\w+)\s*\*=\s*(.+);',
             "MULTIPLY-ASSIGN: Multiplying {0} by {1} (same as {0} = {0} * {1}).",
             "CONCEPT: The *= operator multiplies a variable by a value and stores the result back. Writing 'x *= 2' doubles the value of x. This is equivalent to 'x = x * 2'.",
             "https://en.cppreference.com/w/cpp/language/operator_assignment"),

            (r'(\w+)\s*/=\s*(.+);',
             "DIVIDE-ASSIGN: Dividing {0} by {1} (same as {0} = {0} / {1}).",
             "CONCEPT: The /= operator divides a variable by a value and stores the result back. Writing 'x /= 4' is the same as 'x = x / 4'. Remember: if both operands are integers, the result is also an integer (decimal part is truncated).",
             "https://en.cppreference.com/w/cpp/language/operator_assignment"),

            (r'(\w+)\+\+',
             "INCREMENT: Adding 1 to '{0}'.",
             "CONCEPT: The ++ operator increases a variable's value by exactly 1. 'x++' (postfix) and '++x' (prefix) both add 1, but they differ in WHEN:\n\n• x++ (postfix): Returns the OLD value, THEN adds 1\n• ++x (prefix): Adds 1 FIRST, then returns the NEW value\n\nThis difference matters in expressions: if x is 5, then 'y = x++' sets y to 5 (old value) and x to 6. But 'y = ++x' sets both y and x to 6.\n\nIn standalone statements (just 'x++;' on its own line), both forms are equivalent. In loops, 'i++' and '++i' produce the same result.",
             "https://en.cppreference.com/w/cpp/language/operator_incdec"),

            (r'(\w+)--',
             "DECREMENT: Subtracting 1 from '{0}'.",
             "CONCEPT: The -- operator decreases a variable's value by exactly 1. Like ++, it has postfix (x--) and prefix (--x) forms with the same timing difference.\n\nDecrement is commonly used in countdown loops: 'for (int i = 10; i > 0; i--)' counts down from 10 to 1.",
             "https://en.cppreference.com/w/cpp/language/operator_incdec"),

            # ==============================================================================
            # GROUP 14: CONSTRUCTORS & OBJECT CREATION (Keep after specific patterns)
            # ==============================================================================
            (r'^\s*(\w+)\s*\(\s*\1\s*&\s*(\w+)\s*\)\s*\{?$',
             "COPY CONSTRUCTOR: Creating '{0}' by copying from '{1}'.",
             "CONCEPT: A copy constructor creates a new object as an exact copy of an existing object. It takes a reference to another object of the same class and duplicates all its member values.\n\nC++ provides a default copy constructor that copies each member variable one by one (shallow copy). However, if your class contains pointers or dynamically allocated memory, you MUST write a custom copy constructor to perform a 'deep copy' — otherwise, two objects will share the same pointer, and deleting one will corrupt the other.",
             "https://en.cppreference.com/w/cpp/language/copy_constructor"),

            (r'^\s*(\w+)\s*\(\s*\)\s*\{?$',
             "DEFAULT CONSTRUCTOR: Creating a '{0}' object with no parameters.",
             "CONCEPT: A default constructor initializes an object when no arguments are provided. It's called automatically when you create an object without parentheses: '{0} obj;'.\n\nIf you don't write ANY constructors, C++ provides a default one that does nothing. But the moment you write ANY constructor (like a parameterized one), C++ stops providing the default. If you still need objects with no arguments, you must explicitly write a default constructor.",
             "https://en.cppreference.com/w/cpp/language/default_constructor"),

            (r'^\s*(?!\s*(?:if|for|while|switch|return|void|int|float|double|char|bool|string|auto|const|static|virtual|class|struct|enum|namespace|template|try|catch|throw|public|private|protected|using|typedef|friend|delete|new|else|do|case|break|continue|goto|sizeof|include|define|ifdef|ifndef|endif|pragma)\b)(\w+)\s*\(([^&)]+)\)\s*\{?$',
             "PARAMETERIZED CONSTRUCTOR: Initializing '{0}' with inputs: ({1}).",
             "CONCEPT: A parameterized constructor allows you to create an object and set its initial values in one step. Instead of creating a blank object and then setting each property separately, you pass the values directly when creating the object.\n\nFor example: Student(\"Alice\", 20) creates a Student with the name and age already set, which is much cleaner and safer than:\nStudent s;\ns.name = \"Alice\";\ns.age = 20;\n\nThe parameters are received and typically assigned to the class's member variables inside the constructor body.",
             "https://en.cppreference.com/w/cpp/language/constructor"),

            # Object creation
            (r'\b(?!int|float|double|char|bool|string|void|return|const|class|struct|public|private|protected|template|auto|static|virtual|enum|namespace|using|typedef|friend|if|for|while|switch|try|catch|throw|new|delete|else|do|case|break|continue)(\w+)\s+(\w+)\s*\(([^)]+)\)\s*;',
             "OBJECT CREATION: Creating '{1}' of type '{0}' with arguments ({2}).",
             "CONCEPT: This creates an object of type '{0}' on the stack (automatic memory) by calling its parameterized constructor with the given arguments. The object is automatically destroyed when it goes out of scope (typically at the end of the current block).\n\nStack allocation is the preferred way to create objects in C++ — it's fast, safe, and the memory is managed automatically. Only use 'new' (heap allocation) when you need the object to outlive the current scope.",
             "https://en.cppreference.com/w/cpp/language/constructor"),

            # Method Calls
            (r'\b(\w+)\s*(\.|-\>)\s*(\w+)\s*\((.+)\)\s*;',
             "METHOD CALL: Calling function '{2}' on object '{0}'.",
             "CONCEPT: This invokes a member function (method) of an object. The '{1}' operator connects the object to its method:\n• '.' (dot) — used with regular objects and references\n• '->' (arrow) — used with pointers to objects\n\nThink of it as giving an instruction to a specific object: '{0}, please do {2} with these inputs: {3}'.\n\nThe method has access to all the object's internal data and can modify the object's state.",
             "https://en.cppreference.com/w/cpp/language/member_functions"),

            # ==============================================================================
            # GROUP 15: STRUCTURAL LINES (Last resort — catch structural tokens)
            # ==============================================================================
            
            (r'^\s*\{\s*$',
             "OPENING BRACE: Starting a new code block.",
             "CONCEPT: The opening curly brace marks the beginning of a code block — a group of statements that belong together. Code blocks define the body of functions, loops, if-statements, classes, and other structures.\n\nVariables declared inside a block are 'local' to that block — they only exist within the braces and are automatically destroyed when execution reaches the closing brace. This is called 'scope'.",
             "https://en.cppreference.com/w/cpp/language/scope"),

            (r'^\s*\}\s*$',
             "CLOSING BRACE: Ending a code block.",
             "CONCEPT: The closing curly brace marks the end of a code block. When execution reaches this brace, any local variables declared inside the block are automatically destroyed (their destructors are called), and control returns to the enclosing scope.\n\nIn functions, reaching the closing brace is equivalent to 'return;' for void functions. In loops, it triggers the next iteration check.",
             "https://en.cppreference.com/w/cpp/language/scope"),

            (r'^\s*\}\s*;\s*$',
             "BLOCK END WITH SEMICOLON: Ending a class, struct, or enum definition.",
             "CONCEPT: This closes a class, struct, or enum definition. The semicolon after the closing brace is REQUIRED for these definitions — forgetting it causes confusing compiler errors that often point to the NEXT line of code rather than the actual problem.\n\nThis is one of the most common beginner mistakes in C++. Regular function blocks don't need a semicolon after }}, but class/struct/enum definitions do.",
             "https://en.cppreference.com/w/cpp/language/class"),

            (r'^\s*endl\s*;?\s*$',
             "END LINE: Moving the cursor to the next line and flushing output.",
             "CONCEPT: 'endl' does two things: it inserts a newline character (moves to the next line) AND flushes the output buffer (forces all pending output to be displayed immediately).\n\nFor most purposes, '\\n' is preferred over 'endl' because it only adds a newline without flushing — flushing has a performance cost. Use endl when you specifically need to ensure output appears immediately (like before waiting for user input).",
             "https://en.cppreference.com/w/cpp/io/manip/endl"),
        ]

    def explain_line(self, line: str) -> str:
        """
        High-level summary for the code explorer UI.
        Returns a full educational explanation or a fallback message.
        """
        line = line.strip()
        # Skip purely empty lines
        if not line:
            return "..."

        for pattern, summary, detail, _ in self.rules:
            match = re.search(pattern, line)
            if match:
                try:
                    resolved_summary = summary.format(*match.groups())
                    if detail == "__HEADER_LOOKUP__":
                        header_name = match.group(1).strip()
                        resolved_detail = self._get_header_detail(header_name)
                    else:
                        resolved_detail = detail.format(*match.groups())
                    full_text = f"**{resolved_summary}**\n\n{resolved_detail}"
                    return full_text
                except (IndexError, KeyError):
                    return f"**{summary}**\n\n{detail}"

        # Improved fallback for unsupported lines
        return "This line is recognized as valid C++ code, but Sensei's explanation engine does not yet have a specific rule for it. Try clicking the AI Assistant button on the right panel to ask for a detailed explanation of this line."

    def explain_line_structured(self, line: str) -> dict:
        """
        Structured line explanation returning summary, detail, and reference URL.
        """
        line = line.strip()
        if not line:
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
                    if detail == "__HEADER_LOOKUP__":
                        header_name = match.group(1).strip()
                        header_info = self.header_explanations.get(header_name)
                        if header_info:
                            d = header_info[1]
                            url = header_info[2]
                        else:
                            d = f"CONCEPT: This includes the <{header_name}> library, which provides specific functionality for your program. Including a library gives your code access to pre-written functions, classes, and tools — so you don't have to build everything from scratch.\n\nThe C++ standard library is vast, with hundreds of headers covering input/output, containers, algorithms, strings, memory management, and much more. Each header focuses on a specific area of functionality."
                    else:
                        d = detail.format(*match.groups())
                except (IndexError, KeyError):
                    s = summary
                    d = detail if detail != "__HEADER_LOOKUP__" else "This includes a C++ library header."
                return {
                    "summary": s,
                    "detail": d,
                    "url": url
                }

        return {
            "summary": "Code recognized — detailed rule not yet available",
            "detail": "Sensei's pattern engine does not have a specific rule for this line yet. Use the AI Assistant (click the bot icon on the right) to get a detailed, contextual explanation of any C++ code.",
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
                    if detail == "__HEADER_LOOKUP__":
                        header_name = match.group(1).strip()
                        header_info = self.header_explanations.get(header_name)
                        if header_info:
                            return (header_info[1], header_info[2])
                        return (f"The <{header_name}> library provides specific tools and functions for your C++ program.", url)
                    return (detail.format(*match.groups()), url)
                except (IndexError, KeyError):
                    return (detail, url)
        return None

    def get_options(self, line: str) -> List[str]:
        """UI helper to show if 'More Info' is available."""
        return ['more'] if self.explain_more(line) else []

    def _get_header_detail(self, header_name: str) -> str:
        """Look up header-specific explanation from the dictionary."""
        header_info = self.header_explanations.get(header_name)
        if header_info:
            return header_info[1]
        return f"CONCEPT: This includes the <{header_name}> library, which provides specific functionality for your program. Including a library gives your code access to pre-written functions, classes, and tools — so you don't have to build everything from scratch.\n\nThe C++ standard library is vast, with hundreds of headers covering input/output, containers, algorithms, strings, memory management, and much more. Each header focuses on a specific area of functionality."