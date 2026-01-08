#!/usr/bin/env python3
"""Test the waterfall code puzzle input handler."""

import pygame
pygame.init()

# Set up test keycodes
test_keys = [
    (pygame.K_l, 'l'),
    (pygame.K_a, 'a'),
    (pygame.K_n, 'n'),
    (pygame.K_d, 'd'),
    (pygame.K_a, 'a'),
]

# Simulate the input handler logic
waterfall_code_input = ""
waterfall_code_correct = "landa"

for key, expected_char in test_keys:
    if key >= pygame.K_a and key <= pygame.K_z:
        char = chr(key)
        if char == expected_char:
            waterfall_code_input += char
            print(f"✓ Key {key} -> '{char}' added. Input: '{waterfall_code_input}'")
        else:
            print(f"✗ Key {key} -> '{char}' but expected '{expected_char}'")
    else:
        print(f"✗ Key {key} is not a-z")

# Test the comparison
print(f"\nFinal input: '{waterfall_code_input}'")
print(f"Expected: '{waterfall_code_correct}'")
print(f"Match: {waterfall_code_input.lower() == waterfall_code_correct.lower()}")
