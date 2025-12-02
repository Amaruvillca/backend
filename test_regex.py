import re

def test_regex(pattern, text, name):
    print(f"--- Test: {name} ---")
    print(f"Text: {text}")
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        print(f"Match found: '{match.group(0)}'")
        print(f"Group 1: '{match.group(1)}'")
        print(f"Strip: '{match.group(1).strip()}'")
    else:
        print("No match")
    print()

# Current regex
current_pattern = r'Glosa:(?:[^<]*<[^>]+>)*\s*([^<\n]+)'

# Proposed regex
new_pattern = r'Glosa:(?:<[^>]+>|\s)*([^<\n]+)'

test_cases = [
    ("Plain text", "Glosa: PAY123"),
    ("Bold value", "Glosa: <b>PAY123</b>"),
    ("Table cells", "<td>Glosa:</td><td>PAY123</td>"),
    ("Table cells with span", "<td>Glosa:</td><td><span style='...'>PAY123</span></td>"),
    ("Complex HTML", 'Glosa:</b></span></td><span style="font-size:13px;color:#1f497d;white-space:nowrap">PAY123<br>'),
    ("Value followed by tag", "Glosa: PAY123<br>"),
    ("Empty value", "Glosa: </td>"),
]

print("=== TESTING CURRENT REGEX ===")
for name, text in test_cases:
    test_regex(current_pattern, text, name)

print("\n=== TESTING NEW REGEX ===")
for name, text in test_cases:
    test_regex(new_pattern, text, name)
