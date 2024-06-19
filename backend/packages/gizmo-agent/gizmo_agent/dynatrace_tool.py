from typing import Union, List, Optional
import asyncio

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import ShellTool
from langchain.tools.shell.tool import _get_platform

class DynatraceInput(BaseModel):
    resource_name: str = Field(description="Specifies the name of the pod. Names are case-sensitive.")
    namespace_name: str = Field(description="Specifies the name of the namespace where the pod resides. Names are case-sensitive.")


class DynatraceTool(ShellTool):
    name: str = "Dynatrace"
    description: str  = f"Run Kubectl top commands on this {_get_platform()} machine."

    def _run(
        self,
        resource_name: str,
        namespace_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Run commands and return final output."""

        commands =  f"kubectl top pod/{resource_name} -n {namespace_name}"

        print(f"commands local testing: {commands}")
        return self.process.run(commands)

    async def _arun(
        self,
        resource_name: str,
        namespace_name: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Run commands asynchronously and return final output."""

        commands =  f"kubectl top pod/{resource_name} -n {namespace_name}"
        
        print(f"commands local testing: {commands}")
        return await asyncio.get_event_loop().run_in_executor(
            None, self.process.run, commands
        )
