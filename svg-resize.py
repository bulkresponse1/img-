import os
import re
import xml.etree.ElementTree as ET

# --- CONFIGURATION ---
current_width = 150.0   # Your original size seen in Chrome
current_height = 150.0
target_width = 110.0    # Your desired layout size
target_height = 110.0

# Calculate the scaling ratio (e.g., 110 / 150 = ~0.733)
scale_x = target_width / current_width
scale_y = target_height / current_height

output_folder = "./resized_images/"
os.makedirs(output_folder, exist_ok=True)

# Regex pattern to find all numbers (including decimals and negatives) in path strings
number_pattern = re.compile(r'[-+]?\d*\.\d+|\d+')

def scale_match(match):
    """Multiplies coordinate numbers by our scaling factor and shortens them."""
    val = float(match.group())
    # Scale it and round heavily to 1 decimal place to shave off KB size
    return f"{round(val * scale_x, 1):g}"

print(f"Shrinking SVG code geometries to {int(target_width)}x{int(target_height)}...")
count = 0

for filename in os.listdir("."):
    if filename.lower().endswith(".svg"):
        try:
            original_path = filename
            out_path = os.path.join(output_folder, filename)
            original_size = os.path.getsize(original_path)
            
            # Parse XML
            tree = ET.parse(original_path)
            root = tree.getroot()
            
            # Force structural dimensions to the new target
            root.set("width", str(int(target_width)))
            root.set("height", str(int(target_height)))
            if "viewBox" in root.attrib:
                root.set("viewBox", f"0 0 {int(target_width)} {int(target_height)}")
            
            # Recursively find all drawing paths and mathematically shrink their coordinates
            for element in root.iter():
                # Update path data string shapes
                if "d" in element.attrib:
                    element.attrib["d"] = number_pattern.sub(scale_match, element.attrib["d"])
                
                # Update standard primitive shapes if they exist
                for attr in ["cx", "cy", "r", "rx", "ry", "x", "y", "width", "height", "x1", "y1", "x2", "y2"]:
                    if attr in element.attrib:
                        try:
                            orig_val = float(element.attrib[attr].replace("px", ""))
                            element.attrib[attr] = f"{round(orig_val * scale_x, 1):g}"
                        except ValueError:
                            pass
            
            # Clean up the namespaces and write out the tight minified file
            ET.register_namespace("", "http://w3.org")
            tree.write(out_path, encoding="utf-8", xml_declaration=False)
            
            new_size = os.path.getsize(out_path)
            print(f"SUCCESS: Optimized {filename} (Size dropped from {original_size} to {new_size} bytes)")
            count += 1
            
        except Exception as e:
            print(f"ERROR processing {filename}: {e}")

print(f"\nDone! Processed {count} SVG(s). Look in: {output_folder}")
