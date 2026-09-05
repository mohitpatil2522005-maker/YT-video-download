"""Fix indentation issues in scripts/main.py"""
filepath = r"c:\Users\mohit\Desktop\PROJECTS\YT video download\scripts\main.py"
with open(filepath, "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    stripped = line.strip()
    # Fix the "for q in queries:" line to have exactly 8 spaces
    if "for q in queries:" in stripped and stripped == "for q in queries:":
        lines[i] = "        for q in queries:\n"
        print(f"Fixed line {i+1}: {lines[i].rstrip()}")

with open(filepath, "w") as f:
    f.writelines(lines)

print("Done fixing indentation")
