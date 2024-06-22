from dataclasses import dataclass, field

import cli

from ...models import Path


@dataclass
class GitInterface:
    path: Path = field(default_factory=Path.cwd)
    git_name: str = "Quinten"
    git_email: str = "quinten.roets@gmail.com"
    commit_message: str = "Instantiate new project"

    def clean(self) -> None:
        self.capture_output("add -A")
        self.capture_output("clean -fd")

    def commit(self) -> None:
        self.configure()
        self.capture_output("commit --no-verify -m", self.commit_message)

    def capture_output(self, *args: str | Path | int) -> str:
        git_arg = f"git {args[0]}"
        return cli.capture_output(git_arg, *args[1:], cwd=self.path)

    def configure(self) -> None:
        git_configuration = {"name": self.git_name, "email": self.git_email}
        for attribute, value in git_configuration.items():
            self.capture_output(f"config user.{attribute} {value}")
