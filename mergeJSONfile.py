import os
import json

folder_path = "dbJSON"
merged_data = []
total_elements = 0
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                num_elements = len(data)
                total_elements += num_elements
                merged_data.extend(data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in file {file_path}: {e}")
        except UnicodeDecodeError as e:
            print(f"Error decoding file {file_path}: {e}")
output_file = f"articles_{total_elements}.json"
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(merged_data, file, ensure_ascii=False, indent=4)
print(
    f"All JSON files have been merged into {output_file} with {total_elements} elements"
)
