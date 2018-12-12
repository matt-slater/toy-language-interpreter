# toy-language-interpreter
Implementation of an interpreter for a toy language.
Includes a lexer (for detecting invalid tokens), parser (for detecting invalid syntax) and interpreter.

## The Grammar

The language is defined by the following grammar:

Program: Assignment*\
Assignment: Identifier = Exp;\
Exp: Exp + Term | Exp - Term | Term\
Term: Term * Fact  | Fact\
Fact: ( Exp ) | - Fact | + Fact | Literal | Identifier\
Identifier: Letter [Letter | Digit]* \
Letter: a|...|z|A|...|Z|_ \
Literal: 0 | NonZeroDigit Digit* \
NonZeroDigit: 1|...|9 \
Digit: 0|1|...|9 

In order for the grammar to work with a non-backtracking language, I had to eliminate left recursion for the Term and Exp productions like so: 

Exp: Term Exp' \
Exp':  + Term Exp' | - Term Exp' | ϵ \
Term: Fact Term' \
Term': * Fact Term' | ϵ 

## Usage
`python toy-lang.py`

Play around with the language! Here are some sample valid inputs:  
 
```
toy-lang> x = 1;
{x = 1}

toy-lang> a_17 = 22; b______24a = 33; c = a_17 + b______24a;
{'c': 55, 'a_17': 22, 'b______24a': 33}

toy-lang> y = 77; x_22 = (14 - 4) * (y - 3);
{'y': 77, 'x_22': 740} 
```
  
