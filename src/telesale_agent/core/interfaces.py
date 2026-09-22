"""Core interfaces for the telesale agent pipeline.

This module defines the Ports (Protocols) that the core AgentHarness interacts with.
Implementations (Adapters) must satisfy these protocols.
"""

from typing import Protocol

from telesale_agent.core.models import (
    ActionPlan,
    ActionResult,
    CallBrief,
    CustomerIdentity,
    Observation,
    Perception,
    PolicyDecision,
    RetrievedContext,
    TurnContext,
)


class Perceiver(Protocol):
    async def perceive(self, context: TurnContext) -> Perception: ...


class IdentityResolver(Protocol):
    async def resolve_identity(self, context: TurnContext) -> CustomerIdentity: ...


class Retriever(Protocol):
    async def retrieve(self, context: TurnContext) -> RetrievedContext: ...


class CallBriefBuilder(Protocol):
    async def build_call_brief(self, context: TurnContext) -> CallBrief: ...


class Planner(Protocol):
    async def plan(self, context: TurnContext) -> ActionPlan: ...


class Guardrail(Protocol):
    async def check(self, context: TurnContext) -> PolicyDecision: ...


class Actor(Protocol):
    async def act(self, context: TurnContext) -> ActionResult: ...


class Observer(Protocol):
    async def observe(self, context: TurnContext) -> Observation: ...


class Persister(Protocol):
    async def persist(self, context: TurnContext) -> None: ...
