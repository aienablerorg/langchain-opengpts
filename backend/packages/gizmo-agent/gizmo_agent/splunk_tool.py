from typing import Union, List, Optional
import asyncio

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import ShellTool
from langchain.tools.shell.tool import _get_platform

class SplunkInput(BaseModel):
    resource_name: Union[str, List[str]] = Field(description="Specifies the name of the deployment or pod. Names are case-sensitive.")
    resource_type: str = Field(description="Specifies the type of the resource. Names are case-sensitive. For example  deployment or pod")


class SplunkTool(ShellTool):
    name: str = "Splunk"
    description: str  = f"Useful for retrieving logs of deployment and pods on this {_get_platform()} machine."

    def _run(
        self,
        resource_name: Union[str, List[str]],
        resource_type: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Run commands and return final output."""

        commands = ""
        if isinstance(resource_name, str):
            commands =  f"kubectl logs {resource_type}/{resource_name} -n default"
        else:
        # if not commands[0].startswith("kubectl"):
            commands =  [f"kubectl logs {resource_type}/{i} -n default" for i in resource_name]
            # commands.insert(0, 'kubectl')

        print(f"commands local testing: {commands}")
        return self.process.run(commands)

    async def _arun(
        self,
        resource_name: Union[str, List[str]],
        resource_type: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Run commands asynchronously and return final output."""

        commands = ""
        if isinstance(resource_name, str):
            commands =  f"kubectl logs {resource_type}/{resource_name} -n default"
        else:
        # if not commands[0].startswith("kubectl"):
            commands =  [f"kubectl logs {resource_type}/{i} -n default" for i in resource_name]
            # commands.insert(0, 'kubectl')

        print(f"commands local testing: {commands}")
        return await asyncio.get_event_loop().run_in_executor(
            None, self.process.run, commands
        )
