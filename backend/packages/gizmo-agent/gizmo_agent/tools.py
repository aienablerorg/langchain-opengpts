from enum import Enum
from typing import Union, List, Optional
import asyncio

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from langchain.pydantic_v1 import BaseModel, Field
from langchain.retrievers import KayAiRetriever, PubMedRetriever, WikipediaRetriever
from langchain.retrievers.you import YouRetriever
from langchain.tools import ArxivQueryRun, DuckDuckGoSearchRun, ShellTool
from langchain.tools.shell.tool import _get_platform
from langchain_experimental.tools import PythonREPLTool
from langchain.tools.retriever import create_retriever_tool
from langchain.tools.tavily_search import TavilyAnswer, TavilySearchResults
from langchain.utilities import ArxivAPIWrapper
from langchain.utilities.tavily_search import TavilySearchAPIWrapper
from langchain.vectorstores.redis import RedisFilter

from gizmo_agent.ingest import vstore
from gizmo_agent.splunk_tool import SplunkTool, SplunkInput
from gizmo_agent.dynatrace_tool import DynatraceTool, DynatraceInput


class DDGInput(BaseModel):
    query: str = Field(description="search query to look up")


class ArxivInput(BaseModel):
    query: str = Field(description="search query to look up")


class PythonREPLInput(BaseModel):
    query: str = Field(description="python command to run")


class AIOpsShellTool(ShellTool):
    def _run(
        self,
        commands: Union[str, List[str]],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Run commands and return final output."""

        if isinstance(commands, str):
            if not commands.startswith("kubectl"):
                commands =  'kubectl ' + commands
        else:
            if not commands[0].startswith("kubectl"):
                commands =  [f'kubectl {i}' for i in commands]
            # commands.insert(0, 'kubectl')

        print(f"commands local testing: {commands}")
        return self.process.run(commands)

    async def _arun(
        self,
        commands: Union[str, List[str]],
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Run commands asynchronously and return final output."""

        if isinstance(commands, str):
            if not commands.startswith("kubectl"):
                commands =  'kubectl ' + commands
        else:
            if not commands[0].startswith("kubectl"):
                commands =  [f'kubectl {i}' for i in commands]
            # commands.insert(0, 'kubectl')

        print(f"commands local testing: {commands}")
        return await asyncio.get_event_loop().run_in_executor(
            None, self.process.run, commands
        )

class KubernetesTool(AIOpsShellTool):
    name: str = "Kubernetes"
    description: str  = f"Run Kubectl get, describe and patch commands on this {_get_platform()} machine."


class ShellInput(BaseModel):
    commands: Union[str, List[str]]  = Field(description="List of shell commands to run")


RETRIEVER_DESCRIPTION = """Can be used to look up information that was uploaded to this assistant.
If the user is referencing particular files, that is often a good hint that information may be here."""


def get_retrieval_tool(assistant_id: str):
    return create_retriever_tool(
        vstore.as_retriever(
            search_kwargs={"filter": RedisFilter.tag("namespace") == assistant_id}
        ),
        "Retriever",
        RETRIEVER_DESCRIPTION,
    )


def _get_duck_duck_go():
    return DuckDuckGoSearchRun(args_schema=DDGInput)


def _get_kubectl():
    return KubernetesTool(args_schema=ShellInput)


def _get_splunk():
    return SplunkTool(args_schema=SplunkInput)


def _get_dynatrace():
    return DynatraceTool(args_schema=DynatraceInput)


def _get_python_repl():
    return PythonREPLTool(args_schema=PythonREPLInput)


def _get_arxiv():
    return ArxivQueryRun(api_wrapper=ArxivAPIWrapper(), args_schema=ArxivInput)


def _get_you_search():
    return create_retriever_tool(
        YouRetriever(n_hits=3, n_snippets_per_hit=3),
        "you_search",
        "Searches for documents using You.com",
    )


def _get_sec_filings():
    return create_retriever_tool(
        KayAiRetriever.create(
            dataset_id="company", data_types=["10-K", "10-Q"], num_contexts=3
        ),
        "sec_filings_search",
        "Search for a query among SEC Filings",
    )


def _get_press_releases():
    return create_retriever_tool(
        KayAiRetriever.create(
            dataset_id="company", data_types=["PressRelease"], num_contexts=6
        ),
        "press_release_search",
        "Search for a query among press releases from US companies",
    )


def _get_pubmed():
    return create_retriever_tool(
        PubMedRetriever(), "pub_med_search", "Search for a query on PubMed"
    )


def _get_wikipedia():
    return create_retriever_tool(
        WikipediaRetriever(), "wikipedia", "Search for a query on Wikipedia"
    )


def _get_tavily():
    tavily_search = TavilySearchAPIWrapper()
    return TavilySearchResults(api_wrapper=tavily_search)


def _get_tavily_answer():
    tavily_search = TavilySearchAPIWrapper()
    return TavilyAnswer(api_wrapper=tavily_search)


class AvailableTools(str, Enum):
    DDG_SEARCH = "DDG Search"
    TAVILY = "Search (Tavily)"
    TAVILY_ANSWER = "Search (short answer, Tavily)"
    RETRIEVAL = "Retrieval"
    ARXIV = "Arxiv"
    YOU_SEARCH = "You.com Search"
    SEC_FILINGS = "SEC Filings (Kay.ai)"
    PRESS_RELEASES = "Press Releases (Kay.ai)"
    PUBMED = "PubMed"
    WIKIPEDIA = "Wikipedia"
    PYTHON_REPL = "Python REPL"
    KUBERNETES = "Kubernetes"
    SPLUNK = "Splunk"
    DYNATRACE = "Dynatrace"


TOOLS = {
    AvailableTools.DDG_SEARCH: _get_duck_duck_go,
    AvailableTools.ARXIV: _get_arxiv,
    AvailableTools.YOU_SEARCH: _get_you_search,
    AvailableTools.SEC_FILINGS: _get_sec_filings,
    AvailableTools.PRESS_RELEASES: _get_press_releases,
    AvailableTools.PUBMED: _get_pubmed,
    AvailableTools.TAVILY: _get_tavily,
    AvailableTools.WIKIPEDIA: _get_wikipedia,
    AvailableTools.TAVILY_ANSWER: _get_tavily_answer,
    AvailableTools.PYTHON_REPL: _get_python_repl,
    AvailableTools.KUBERNETES: _get_kubectl,
    AvailableTools.SPLUNK: _get_splunk,
    AvailableTools.DYNATRACE: _get_dynatrace,
}

TOOL_OPTIONS = {e.value: e.value for e in AvailableTools}

# Check if dependencies and env vars for each tool are available
for k, v in TOOLS.items():
    v()
