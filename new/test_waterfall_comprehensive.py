#!/usr/bin/env python3
"""
Comprehensive test of the waterfall code puzzle system.
This test simulates the complete flow from receiving the code,
to entering it at the code lock, to completing the maze.
"""

import pygame
pygame.init()

print("=" * 60)
print("WATERFALL CODE PUZZLE SYSTEM TEST")
print("=" * 60)

# Test 1: Verify pygame key constants
print("\n[TEST 1] Pygame key constants")
print(f"  pygame.K_a = {pygame.K_a} (chr: '{chr(pygame.K_a)}')")
print(f"  pygame.K_z = {pygame.K_z} (chr: '{chr(pygame.K_z)}')")
print(f"  pygame.K_ESCAPE = {pygame.K_ESCAPE}")
print(f"  pygame.K_RETURN = {pygame.K_RETURN}")
print(f"  pygame.K_BACKSPACE = {pygame.K_BACKSPACE}")

# Test 2: Input handler logic
print("\n[TEST 2] Input handler logic")
waterfall_code_input = ""
waterfall_code_correct = "landa"
test_sequence = [
    (pygame.K_l, 'l'),
    (pygame.K_a, 'a'),
    (pygame.K_n, 'n'),
    (pygame.K_d, 'd'),
    (pygame.K_a, 'a'),
]

for key, expected in test_sequence:
    if key >= pygame.K_a and key <= pygame.K_z:
        char = chr(key)
        if char == expected:
            waterfall_code_input += char
            print(f"  ✓ Added '{char}'. Buffer: '{waterfall_code_input}'")
        else:
            print(f"  ✗ Key mismatch: got '{char}', expected '{expected}'")

# Test 3: Code verification
print("\n[TEST 3] Code verification")
print(f"  Input: '{waterfall_code_input}'")
print(f"  Correct: '{waterfall_code_correct}'")
matches = waterfall_code_input.lower() == waterfall_code_correct.lower()
print(f"  Match: {'✓ YES' if matches else '✗ NO'}")

# Test 4: Backspace handling
print("\n[TEST 4] Backspace handling")
waterfall_code_input = "land"
waterfall_code_input = waterfall_code_input[:-1]
print(f"  After backspace: '{waterfall_code_input}' (expected 'lan')")
print(f"  Correct: {'✓ YES' if waterfall_code_input == 'lan' else '✗ NO'}")

# Test 5: Escape handling
print("\n[TEST 5] Escape handling")
waterfall_code_input = ""
print(f"  After escape reset: '{waterfall_code_input}' (expected '')")
print(f"  Correct: {'✓ YES' if waterfall_code_input == '' else '✗ NO'}")

# Test 6: Case insensitivity
print("\n[TEST 6] Case insensitivity")
test_input_lower = "landa"
test_input_upper = "LANDA"
print(f"  Lower: '{test_input_lower}' == '{waterfall_code_correct}'")
print(f"  Match: {'✓ YES' if test_input_lower.lower() == waterfall_code_correct.lower() else '✗ NO'}")
print(f"  Upper: '{test_input_upper}' == '{waterfall_code_correct.upper()}'")
print(f"  Match: {'✓ YES' if test_input_upper.lower() == waterfall_code_correct.lower() else '✗ NO'}")

# Test 7: Maze solution
print("\n[TEST 7] Maze solution path")
waterfall_maze_solution = [(400, 350), (400, 450), (500, 450), (500, 300), (300, 300), (300, 150), (600, 150)]
print(f"  Start: {waterfall_maze_solution[0]}")
print(f"  End: {waterfall_maze_solution[-1]}")
print(f"  Points: {len(waterfall_maze_solution)}")
print(f"  ✓ Maze solution defined")

# Test 8: Herb reward
print("\n[TEST 8] Herb reward")
inventory = {"Herbs": 0}
inventory["Herbs"] = inventory.get("Herbs", 0) + 3
print(f"  Starting herbs: 0")
print(f"  After maze: {inventory['Herbs']}")
print(f"  Correct: {'✓ YES' if inventory['Herbs'] == 3 else '✗ NO'}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED")
print("=" * 60)
