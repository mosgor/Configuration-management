import subprocess
import xml.etree.ElementTree as ET
from typing import Dict, List


def parse_xml_config(config_path: str) -> Dict[str, str]:
    """
    Parse the XML configuration file and return the necessary parameters.

    Args:
        config_path (str): Path to the XML configuration file.

    Returns:
        Dict[str, str]: A dictionary containing visualizer path, package name, max depth, and repository URL.
    """
    tree = ET.parse(config_path)
    root = tree.getroot()

    config = {
        "visualizer_path": root.find("visualizer_path").text,
        "package_name": root.find("package_name").text,
        "max_depth": int(root.find("max_depth").text),
        "repository_url": root.find("repository_url").text,
    }
    return config


def get_dependencies(package_name: str) -> List[str]:
    """
    Retrieve immediate package dependencies using pip.

    Args:
        package_name (str): The name of the package to retrieve dependencies for.

    Returns:
        List[str]: A list of dependencies for the given package.
    """
    try:
        result = subprocess.run(
            ["pip", "show", package_name], capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError:
        print(f"Error: Could not fetch dependencies for {package_name}")
        return []

    dependencies = []
    for line in result.stdout.splitlines():
        if line.startswith("Requires"):
            requires_line = line.split(":")[1].strip()  # Strip any extra spaces
            if requires_line:
                dependencies = [dep.strip() for dep in requires_line.split(", ") if dep]
            break
    return dependencies


def build_dependency_graph(package_name: str, max_depth: int) -> List[str]:
    """
    Recursively build the dependency graph for the package using PlantUML format.

    Args:
        package_name (str): The name of the package to build the dependency graph for.
        max_depth (int): The maximum depth of dependencies to traverse.

    Returns:
        List[str]: A list of strings representing the dependency relationships in PlantUML format.
    """
    graph = []
    visited = set()

    def add_dependencies(pkg_name: str, current_depth: int):
        if current_depth > max_depth or pkg_name in visited:
            return
        visited.add(pkg_name)

        dependencies = get_dependencies(pkg_name)
        for dep in dependencies:
            graph.append(f"{pkg_name} --> {dep}")
            add_dependencies(dep, current_depth + 1)

    add_dependencies(package_name, 1)
    return graph


def generate_mermaid_script(graph: List[str]) -> str:
    """
    Generate a Mermaid script based on the dependency graph.

    Args:
        graph (List[str]): The dependency graph as a list of strings.

    Returns:
        str: The generated Mermaid script.
    """
    mermaid_script = "graph TD\n"
    for relation in graph:
        mermaid_script += f"    {relation}\n"
    return mermaid_script


def save_mermaid_script(script: str, output_path: str) -> None:
    """
    Save the Mermaid script to a file.

    Args:
        script (str): The Mermaid script content.
        output_path (str): The file path where the script will be saved.
    """
    with open(output_path, "w") as f:
        f.write(script)


def visualize_graph(visualizer_path: str, script_path: str) -> None:
    """
    Generates mermaid Diagram from script.
    Using mmdc (Mermaid CLI).

    Args:
        script_path (str): path to .mmd file.
        visualizer_path (str): path to visualizer program.
    """
    result = subprocess.run(f"{visualizer_path} -i {script_path} -o mermaid_graph.png", capture_output=True, shell=True)
    if result.returncode == 0:
        print("Diagram saved to mermaid_graph.png")
    else:
        print(f"Error during generation: {result.stderr.decode('utf-8', errors='ignore')}")


def main(config_path: str) -> None:
    """
    Main function to build and visualize the dependency graph for a Python package.

    Args:
        config_path (str): Path to the XML configuration file.
    """
    config = parse_xml_config(config_path)
    package_name = config["package_name"]
    max_depth = config["max_depth"]
    visualizer_path = config["visualizer_path"]

    graph = build_dependency_graph(package_name, max_depth)

    mermaid_script = generate_mermaid_script(graph)

    script_path = "mermaid_script.mmd"
    save_mermaid_script(mermaid_script, script_path)

    visualize_graph(visualizer_path, script_path)


if __name__ == "__main__":
    config_path = "config.xml"  # Path to your XML config file
    main(config_path)
