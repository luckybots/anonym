import argparse
import shlex


class CommandParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(add_help=False, formatter_class=argparse.RawTextHelpFormatter)
        self.setup_rules()

    def setup_rules(self):
        command_options = {
            "enable": "Enables the bot for a given group",
            "disable": "Disables the bot for a given group",
            "help": "Print help for the commands",
        }

        self.add_argument('command',
                          choices=command_options.keys(),
                          type = str.lower)

        self.add_argument('--password',
                          type=str,
                          metavar='',
                          help=f'Password to access the bot')
        self.add_argument('--group_id',
                          type=int,
                          metavar='',
                          help='Group id to perform operation on')

        self.usage = f'[command] [parameters]'

    def validate_and_fix_params(self, params):
        pass # Empty for now

    @classmethod
    def unify_whitespace(cls, s):
        # Ws can be obtained using the following code
        #       all_unicode = ''.join(chr(c) for c in range(sys.maxunicode+1))
        #       ws = ''.join(re.findall(r'\s', all_unicode))
        ws = '\t\n\x0b\x0c\r\x1c\x1d\x1e\x1f \x85\xa0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000'
        unified_ws = ' '
        s2 = s.translate(s.maketrans(ws, unified_ws * len(ws)))
        return s2


    def parse_command(self, command):
        # We unify whitespace as shlex can't parse Unicode whitespaces properly
        command = self.unify_whitespace(command)
        # Fix back Telegram autoreplace
        command = command.replace('—', '--')
        args = shlex.split(command)

        return self.parse_args(args)

    def parse_args(self, *args, **kwargs):
        self.error_message = None
        try:
            params = super().parse_args(*args, **kwargs)
            # Make checks for command mandatory params to be set
            self.validate_and_fix_params(params)
            return params
        except Exception as e:
            self.error_message = str(e)

    def error(self, message):
        """
        Overwrite the default parser behaviour in case of error - throws an exception instead of making exit
        """
        message = f'{message}\n*use "help" command to get help*'
        raise Exception(message)

    def format_help(self):
        help = super().format_help()
        # default "optional arguments" name isn't suitable for Toffee as some of these arguments are mandatory for some commands
        help = help.replace("optional arguments", "parameters")
        # in our case "positional arguments" are used to set the command
        help = help.replace("positional arguments", "command")
        return help