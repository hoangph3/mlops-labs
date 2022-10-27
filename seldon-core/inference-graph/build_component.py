import os

base_path = "./components_source"
script_file = "./build_image.sh"

components = [
    component_name
    for component_name in os.listdir(base_path)
    if os.path.isdir(os.path.join(base_path, component_name))
]

for component in components:
    os.system("bash {script_file} {component} --no-cache".format(
        script_file=script_file,
        component=component
    ))