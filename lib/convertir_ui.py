import os

# Folders
ui_folder = "views/forms_ui"  
py_folder = "views/forms_py"  

# Create py_folder if not exists
for file in os.listdir(ui_folder):
    
    # Check if file is a .ui file
    if file.endswith(".ui"):
        
        ui_path = os.path.join(ui_folder, file)
        py_path = os.path.join(py_folder, file.replace(".ui", ".py"))

        # Convert .ui to .py
        os.system(f"pyuic6 -o {py_path} {ui_path}")

        # Print
        print(f"Convertido: {file} -> {py_path}")

# Print
print("Conversión completada.")