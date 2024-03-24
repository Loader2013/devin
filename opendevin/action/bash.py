from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import ExecutableAction

if TYPE_CHECKING:
    from opendevin.controller import AgentController
    from opendevin.observation import CmdOutputObservation


@dataclass
class CmdRunAction(ExecutableAction):
    command: str
    background: bool = False

    def run(self, controller: "AgentController") -> "CmdOutputObservation":
        return controller.command_manager.run_command(self.command, self.background)


@dataclass
class CmdKillAction(ExecutableAction):
    id: int

    def run(self, controller: "AgentController") -> "CmdOutputObservation":
        return controller.command_manager.kill_command(self.id)
