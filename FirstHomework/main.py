import argparse
import datetime
import json
import os
import tkinter as tk
import tarfile

file_list = []
opened_recently = False

def get_fl():
	return globals()["file_list"]

def execute_command(command: str, log_file: str):
	"""
    Execute a command in the virtual shell.

    :param command: The command to execute
    :type command: str
    :param file_list: A list of files in the virtual file system
    :type file_list: list[str]
    :return: The output of the command
    :rtype: str
    """
	
	command = command.strip()
	
	file_list = globals()["file_list"]
	
	if command.startswith("ls"):
		log(command, log_file)
		return "\n".join(file_list)
	elif command.startswith("cd"):
		name = command[3:]
		new_file_list = []
		found = False
		for file in file_list:
			if file.startswith(name) and file != name:
				found = True
				new_file_list.append(file)
		globals()["file_list"] = new_file_list
		if found:
			log(command + " SUCCEED", log_file)
			return "Changed directory to " + name
		else:
			log(command + " FAILED", log_file)
			return "Directory not found"
	elif command.startswith("exit"):
		log(command, log_file)
		exit()
	elif command.startswith("echo"):
		log(command, log_file)
		return command[5:]  # Return text after "echo "
	elif command.startswith("pwd"):
		log(command, log_file)
		return os.getcwd()  # Print working directory
	elif command.startswith("tree"):
		log(command, log_file)
		path = command[5:]
		res_string = ""
		indent = "  "
		
		def tree(path, indent):
			nonlocal res_string
			path_prefix = path if path.endswith("/") else path + "/"
			printed_dirs = set()
			for file in sorted(globals()["file_list"]):
				if file.startswith(path_prefix):
					relative_path = file[len(path_prefix):]
					if "/" in relative_path:
						# This means it's a directory
						first_dir = relative_path.split("/")[0]
						if first_dir not in printed_dirs:
							res_string += f"{indent}{first_dir}/"
							printed_dirs.add(first_dir)
							# Recursively call tree for the subdirectory
							tree(os.path.join(path, first_dir), indent + "  ")
					else:
						# It's a file, print it
						res_string += f"{indent}{relative_path}"
		
		tree(path, "  ")
		return res_string
	else:
		log(command + " NOT FOUND", log_file)
		return "Command not found"


def log(command: str, log_file: str):
	with open(log_file, "r") as file:
		try:
			current = json.load(file)
		except json.decoder.JSONDecodeError:
			current = {"session_1": []}
			globals()["opened_recently"] = True
	obj = {"command": command, "time": str(datetime.datetime.now())}
	sessions = list(current.keys())
	num_of_session = int(sessions[-1][sessions[-1].find("_")+1:])
	if not opened_recently:
		num_of_session += 1
		current[f"session_{num_of_session}"] = []
		globals()["opened_recently"] = True
	current[f"session_{num_of_session}"].append(obj)
	with open(log_file, "w") as file:
		json.dump(current, file)


def create_gui(start_script: str, log_file: str):
	"""
    Creates the main GUI window for the OS Shell Emulator.

    :param file_list: A list of files in the virtual file system
    :type file_list: list[str]
    :param start_script: Path to the start script
    :type start_script: str
    """
	
	file_list = globals()["file_list"]
	
	root = tk.Tk()
	root.title("OS Shell Emulator")
	
	# Command input
	command_entry = tk.Entry(root, width=50)
	command_entry.pack(pady=10)
	
	# Output area
	output_area = tk.Text(root, height=20, width=80)
	output_area.pack(pady=10)
	
	# Function to handle command submission
	def submit_command():
		command = command_entry.get()
		output = execute_command(command, log_file)
		output_area.insert(tk.END, f"$ {command}\n{output}\n")
		command_entry.delete(0, tk.END)
	
	# Submit button
	submit_button = tk.Button(root, text="Execute", command=submit_command)
	submit_button.pack()
	root.bind("<Return>", lambda event: submit_command())
	
	# Load start script commands
	try:
		with open(start_script, "r") as script_file:
			for line in script_file:
				start_command = line.strip()
				start_output = execute_command(start_command, log_file)
				output_area.insert(tk.END, f"$ {start_command}\n{start_output}\n")
				command_entry.delete(0, tk.END)
	except FileNotFoundError:
		output_area.insert(tk.END, "Start script not found.\n")
	
	root.mainloop()


def main():
	"""Main function to handle command line arguments and start the GUI."""
	
	conf_file = open("configuration.json", 'r')
	configs = json.load(conf_file)
	conf_file.close()
	
	parser = argparse.ArgumentParser(description="OS Shell Emulator")
	parser.add_argument(
		"--vfs", required=False, help="Path to the virtual file system archive", default=configs["vfs"]
	)
	parser.add_argument(
		"--log_file", required=False, help="Path to the log file", default=configs["log"]
	)
	parser.add_argument(
		"--start_script", required=False, help="Path to the start script", default=configs["start"]
	)
	args = parser.parse_args()

	log("SESSION STARTED", args.log_file)
	
	# Load virtual file system
	with tarfile.TarFile(args.vfs, "r") as tar_ref:
		globals()["file_list"] = tar_ref.getnames()
	
	if __name__ == "__main__":
		# Create GUI
		create_gui(args.start_script, args.log_file)


if __name__ == "__main__":
	main()
