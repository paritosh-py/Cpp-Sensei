#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    string s;
    
    cout << "Enter a sentence: ";
    getline(cin, s);

    // Store original
    string original = s;

    // Reverse the string
    string reversed = s;
    reverse(reversed.begin(), reversed.end());

    // Count words
    int words = 0;
    for(int i = 0; i < s.length(); i++){
        if(s[i] == ' ' && s[i+1] != ' ')
            words++;
    }
    words++; // last word

    // Convert to uppercase
    string upper = s;
    for(char &c : upper){
        c = toupper(c);
    }

    cout << "\nOriginal: " << original;
    cout << "\nReversed: " << reversed;
    cout << "\nUppercase: " << upper;
    cout << "\nWord count: " << words << endl;

    // Check palindrome
    if(original == reversed)
        cout << "It's a PALINDROME 🔁";
    else
        cout << "Not a palindrome ❌";

    return 0;
}
