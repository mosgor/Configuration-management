import unittest
from unittest.mock import mock_open, patch

from visualize_dependency import *


class TestParseXmlConfig(unittest.TestCase):
	@patch("builtins.open", new_callable=mock_open,
		   read_data='<config><visualizer_path>/path/to/visualizer</visualizer_path><package_name>example_pkg</package_name><max_depth>3</max_depth><repository_url>https://github.com/example</repository_url></config>')
	def test_parse_xml_config(self, mock_file):
		config_path = "fake_config.xml"
		expected_config = {
			"visualizer_path": "/path/to/visualizer",
			"package_name": "example_pkg",
			"max_depth": 3,
			"repository_url": "https://github.com/example"
		}
		result = parse_xml_config(config_path)
		self.assertEqual(result, expected_config)


class TestGetDependencies(unittest.TestCase):
	@patch("subprocess.run")
	def test_get_dependencies_success(self, mock_run):
		mock_run.return_value.stdout = "Requires: dep1, dep2"
		package_name = "example_pkg"
		result = get_dependencies(package_name)
		self.assertEqual(result, ["dep1", "dep2"])
		mock_run.assert_called_once_with(["pip", "show", package_name], capture_output=True, text=True, check=True)
	
	@patch("subprocess.run")
	def test_get_dependencies_no_requires(self, mock_run):
		mock_run.return_value.stdout = "Name: example_pkg\nVersion: 1.0.0"
		package_name = "example_pkg"
		result = get_dependencies(package_name)
		self.assertEqual(result, [])
	
	@patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "pip show"))
	def test_get_dependencies_failure(self, mock_run):
		package_name = "example_pkg"
		result = get_dependencies(package_name)
		self.assertEqual(result, [])


class TestBuildDependencyGraph(unittest.TestCase):
	@patch("subprocess.run")
	def test_build_dependency_graph(self, mock_run):
		mock_run.return_value.stdout = "Requires: dep1, dep2"
		
		def mock_get_dependencies(package_name: str):
			if package_name == "example_pkg":
				return ["dep1", "dep2"]
			return []
		
		with patch("visualize_dependency.get_dependencies", mock_get_dependencies):
			result = build_dependency_graph("example_pkg", 2)
		expected_graph = [
			"example_pkg --> dep1",
			"example_pkg --> dep2"
		]
		self.assertEqual(result, expected_graph)


class TestGenerateMermaidScript(unittest.TestCase):
	def test_generate_mermaid_script(self):
		graph = [
			"pkg1 --> pkg2",
			"pkg2 --> pkg3"
		]
		expected_script = "graph TD\n    pkg1 --> pkg2\n    pkg2 --> pkg3\n"
		result = generate_mermaid_script(graph)
		self.assertEqual(result, expected_script)


class TestSaveMermaidScript(unittest.TestCase):
	@patch("builtins.open", new_callable=mock_open)
	def test_save_mermaid_script(self, mock_file):
		script = "graph TD\n    pkg1 --> pkg2"
		output_path = "test_output.mmd"
		save_mermaid_script(script, output_path)
		mock_file.assert_called_once_with(output_path, "w")
		mock_file().write.assert_called_once_with(script)


class TestVisualizeGraph(unittest.TestCase):
	@patch("subprocess.run")
	def test_visualize_graph_success(self, mock_run):
		mock_run.return_value.returncode = 0
		script_path = "test_script.mmd"
		visualizer_path = "/path/to/mermaid_cli"
		visualize_graph(visualizer_path, script_path)
		mock_run.assert_called_once_with(
			f"{visualizer_path} -i {script_path} -o mermaid_graph.png", capture_output=True, shell=True
		)
	
	@patch("subprocess.run")
	def test_visualize_graph_failure(self, mock_run):
		mock_run.return_value.returncode = 1
		mock_run.return_value.stderr = b"Error during generation"
		script_path = "test_script.mmd"
		visualizer_path = "/path/to/mermaid_cli"
		visualize_graph(visualizer_path, script_path)
		mock_run.assert_called_once_with(
			f"{visualizer_path} -i {script_path} -o mermaid_graph.png", capture_output=True, shell=True
		)


if __name__ == '__main__':
	unittest.main()
