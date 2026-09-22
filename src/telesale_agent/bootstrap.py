"""Create a runnable harness by choosing one implementation for each stage."""

import os
from dotenv import load_dotenv

from telesale_agent.core.langgraph_pipeline import LangGraphAgentHarness
from telesale_agent.core.builder import AgentHarnessBuilder

from telesale_agent.adapters.llm.llm_perceive import LLMPerceiver
from telesale_agent.adapters.mock.identity import HintIdentityResolver
from telesale_agent.adapters.mock.retrieve import MockDataRetriever
from telesale_agent.adapters.mock.call_brief import SimpleCallBriefBuilder
from telesale_agent.adapters.llm.llm_planner import LLMPlanner
from telesale_agent.adapters.mock.guardrail import AllowAllGuardrail

from telesale_agent.adapters.mock.act import LocalActor
from telesale_agent.adapters.mock.observe import BasicObserver
from telesale_agent.adapters.mock.persist import InMemoryPersister

def build_default_harness() -> LangGraphAgentHarness:
    """Build a dependency-free harness for local development and tests using Builder."""
    load_dotenv()
    
    return (AgentHarnessBuilder()
        .with_perceiver(LLMPerceiver())
        .with_identity_resolver(HintIdentityResolver())
        .with_retriever(MockDataRetriever())
        .with_call_brief_builder(SimpleCallBriefBuilder())
        .with_planner(LLMPlanner())
        .with_guardrail(AllowAllGuardrail())
        .with_actor(LocalActor())
        .with_observer(BasicObserver())
        .with_persister(InMemoryPersister())
        .build())
