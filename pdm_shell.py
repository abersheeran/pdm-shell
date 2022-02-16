import argparse
import os

from pdm.cli.commands.base import BaseCommand, Project


class ShellCommand(BaseCommand):
    """Set PATH and PYTHONPATH in the current shell"""

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--memo", help="Print command to execute", action="store_true"
        )

    def handle(self, project: Project, options: argparse.Namespace) -> None:
        """The command handler function.

        :param project: the pdm project instance
        :param options: the parsed Namespace object
        """
        import shellingham

        shell, executeable = shellingham.detect_shell()
        shell = shell.lower()

        if options.memo:
            if shell in ("bash", "zsh", "fish", "csh", "tcsh"):
                self.output("eval $(pdm shell)")
            elif shell == "pwsh":
                self.output("pdm shell | Invoke-Expression")
            else:
                raise NotImplementedError(f"Shell {shell} is not supported")
        else:
            if shell in ("bash", "zsh"):
                self.output(
                    "export PATH=$(pdm info --packages)/bin:$PATH"
                    " && export PYTHONPATH=$(pdm info --packages)/lib:$PYTHONPATH"
                )
            elif shell == "fish":
                self.output(
                    "set -x PATH $(pdm info --packages)/bin $PATH"
                    " && set -x PYTHONPATH $(pdm info --packages)/lib $PYTHONPATH"
                )
            elif shell in ("csh", "tcsh"):
                self.output(
                    "setenv PATH $(pdm info --packages)/bin:$PATH"
                    " && setenv PYTHONPATH $(pdm info --packages)/lib:$PYTHONPATH"
                )
            elif shell == "pwsh":
                split = ";" if os.name == "nt" else ":"
                bin_dir = "Scripts" if os.name == "nt" else "bin"
                self.output(
                    f"Set-Item -Path Env:Path -Value ((Join-Path $(pdm info --packages) '{bin_dir}') + '{split}' + $env:PATH)"
                    f" && Set-Item -Path Env:PYTHONPATH -Value ((Join-Path $(pdm info --packages) 'lib') + '{split}' + $env:PYTHONPATH)"
                )
            else:
                raise NotImplementedError(f"Shell {shell} is not supported")

    def output(self, command: str) -> None:
        print(command, flush=True)


def shell(core):
    core.register_command(ShellCommand, "shell")
