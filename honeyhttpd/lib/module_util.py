# 
# Python module for importing, listing and manipulating modules
#
import os

## Imports a module given by name
#
# @param module_name (string) - The name of the module
# @returns None or module object
#
def import_module(module_name, ):
    if module_exists(module_name):
        #~ temp = importlib.import_module("modules." + module_name + "." + module_name)
        temp = __import__("servers." + module_name, globals(), locals(), ['./servers'], 0)
            
        module_class = getattr(temp, module_name)

        return module_class
    else:
        return None

## Checks if a module exists and all files are properly
#
# @param module_name (string) - The name of the module
# @returns bool
#
def module_exists(module_name):
		
    if not os.path.exists("./servers/" + module_name + ".py"):
        return False
    else:
        return True


