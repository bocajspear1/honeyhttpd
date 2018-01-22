# 
# Python module for importing, listing and manipulating modules
#
import os

## Imports a module given by name
#
# @param module_name (string) - The name of the module
# @returns None or module object
#
def import_module(directory, module_name):
    if module_exists(directory, module_name):
        #~ temp = importlib.import_module("modules." + module_name + "." + module_name)
        temp = __import__(directory.replace("/", ".") + "." + module_name, globals(), locals(), ['./' + directory], 0)
            
        module_class = getattr(temp, module_name)

        return module_class
    else:
        return None

## Checks if a module exists and all files are properly
#
# @param module_name (string) - The name of the module
# @returns bool
#
def module_exists(directory, module_name):
		
    if not os.path.exists("./" + directory + "/" + module_name + ".py"):
        return False
    else:
        return True


