import config
import core

import importlib
import sys
import subprocess

############# admin.py ##############
## commands for bot administrators ##
## by Annika                       ##
#####################################

GIT_COMMAND = 'git pull'

class Module:
    """Represents a module, which may contain several commands
    """
    def __init__(self):
        self.commands = {
            "eval": self.eval, "do": self.do, "sayin": self.do, "load": self.handleModule,
            "loadmodule": self.handleModule, "unload": self.handleModule, "unloadmodule": self.handleModule,
            "hotpatch": self.handleModule, "modules": self.viewModules, "listmodules": self.viewModules,
            "vm": self.viewModules, "restart": self.kill, "kill": self.kill, "update": self.update, "git": self.update
        }

    def eval(self, message):
        """eval: evaluates the given Python expression

        Arguments:
            message {Message} -- the Message object that invoked the command
        """
        if message.sender.isAdmin and message.sender.id in config.sysops:
            expression = config.separator.join(message.arguments[1:])
            try:
                response = str(eval(expression))
            except Exception as err:
              response = str(err)
        else:
            message.respond("Permission denied. This request has been logged.")
            core.log(f"W: admin.eval(): eval permission denied for userid: {message.sender.id}")
            return
        response = "!code " + ("\n" if "\n" not in response else "") + response
        message.respond(response)

    def do(self, message):
        """do: sends the given command to the given room 

        Arguments:
            message {Message} -- the Message object that invoked the command
        """
        if not message.arguments or len(message.arguments) < 3:
            return message.respond(f"Usage: ``{config.commandCharacter}do <room>, <message>``.")
        room = message.connection.getRoomByName(message.arguments[1])
        if room:
            if not message.sender.can("manage", room): 
                return message.respond("Permission denied.")
            command = ",".join(message.arguments[2:]).strip()
            return room.say(command)
        else:
            return message.respond(f"{message.arguments[1]} isn't a room I'm in.")

    def handleModule(self, message):
        """Handles loading, reloading, and hotpatching modules

        Args:
            message (Message): the message that triggered the command
        """
        if not message.sender.isAdmin: return message.respond("Permission denied.")
        if not message.arguments or len(message.arguments) < 2:
            return message.respond(f"Usage: ``{message.arguments[0]} <module>``.")
        module = core.toID(message.arguments[1])
        action = ''
        if 'load' in message.arguments[0]: action = 'load'
        if 'unload' in message.arguments[0]: action = 'unload'
        if 'hotpatch' in message.arguments[0]: action = 'hotpatch'

        if module == __name__ and action == 'unload':
            return message.respond(f"Don't unload the module that provides ``{message.arguments[0]}``.")
        
        responses = []
        if action == 'unload': return message.respond(self.unload(message.connection, module))
        if action == 'load': return message.respond(self.load(message.connection, module))
        if action == 'hotpatch':
            mod = importlib.import_module(module)
            importlib.reload(mod)
            message.connection.commands.update(mod.Module().commands)
            return message.respond(f"Successfully hotpatched the {module} module.")
        return [message.respond(response) for response in responses]
    
    
    def viewModules(self, message):
        """Lists the currently loaded modules

        Args:
            message (Message): the Message object that invoked the command
        """
        return message.respond(f"Modules currently known to be loaded: {', '.join([f'``{module}``' for module in message.connection.modules])}")

    def kill(self, message):
        """Kills the bot process

        Args:
            message (Message): the Message object that invoked the command
        """
        if message.sender.isAdmin:
            message.respond("Killing the bot process....")
            core.log(f"E: admin.kill(): killed by {message.senderName}")
            sys.exit()
            return message.respond("Something went wrong killing the bot process.")
        return message.respond("Permission denied.")
    
    def update(self, message):
        """Pulls latest code from git

        Args:
            message (Message): the Message object that invoked the command
        """
        if not message.sender.isAdmin: return message.respond("Permission denied.")
        output = subprocess.run(GIT_COMMAND.split(), capture_output = True, text = True)
        results = ""
        success = True
        if len(output.stderr) > 0:
            message.respond(f"``{GIT_COMMAND}`` failed!")
            results = output.stdout + output.stderr
            success = False
        else:
            results = output.stdout
        if len(results) > 295 and '\n' not in results: results = f"\n{results}"
        message.respond(f"!code {results}")
        message.respond(
            f"Pulled code! Use ``{config.commandCharacter}hotpatch`` to reload modules." if success 
            else 
            f"``{GIT_COMMAND}`` failed!")

    def load(self, connection, module, force = False):
        """Loads a module

        Args:
            connection (Connection): the Connection object to load the module into
            module (string): the ID of the module to load
            force (bool, optional): whether or not to force-load modules that are already loaded. Defaults to False.

        Returns:
            string: a description of what happened
        """
        if module in connection.modules and not force: 
            return f"The ``{module}`` module is already loaded -- did you mean to hotpatch it?"

        try:
            connection.commands.update(importlib.import_module(module).Module().commands)
            connection.modules.add(module)
            return f"Successfully loaded the ``{module}`` module."
        except Exception as err:
            response = f"Error loading module: {str(err)}."
            core.log(f"I: admin.load(): {response}")
            return response
    

    def __str__(self):
        """String representation of the Module

        Returns:
            string -- representation
        """
        return f"Admin module: helper commands for bot administrators. Commands: {', '.join(self.commands.keys())}"