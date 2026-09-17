"""The complete online pipeline for one customer conversation turn."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from telesale_agent.core.errors import AgentLoopLimitError, PipelineStageError
from telesale_agent.core.models import (
    ActionResult,
    ActionStatus,
    AgentStep,
    ConversationState,
    Message,
    TurnContext,
    TurnInput,
    TurnResult,
)
from telesale_agent.core.interfaces import (
    Actor,
    CallBriefBuilder,
    Guardrail,
    IdentityResolver,
    Observer,
    Perceiver,
    Persister,
    Planner,
    Retriever,
)


@dataclass(frozen=True, slots=True)
class PipelineStages:
    """Concrete implementation selected for each pipeline stage."""

    perceive: Perceiver
    identity: IdentityResolver
    retrieve: Retriever
    call_brief: CallBriefBuilder
    plan: Planner
    guardrail: Guardrail
    act: Actor
    observe: Observer
    persist: Persister


class AgentHarness:
    """Coordinates preprocessing, context loading, the agent loop, and memory."""

    def __init__(self, stages: PipelineStages, max_agent_steps: int = 4) -> None:
        if max_agent_steps < 1:
            raise ValueError("max_agent_steps must be at least 1")
        self.stages = stages
        self.max_agent_steps = max_agent_steps

    async def run_turn(
        self,
        turn_input: TurnInput,
        state: ConversationState | None = None,
    ) -> TurnResult:
        state = state or ConversationState(conversation_id=turn_input.conversation_id)
        if state.conversation_id != turn_input.conversation_id:
            raise ValueError("state and input must belong to the same conversation")

        context = TurnContext(input=turn_input, state=state)

        # 1. Understand the customer's current message.
        context.perception = await self._run(
            "perceive", self.stages.perceive.perceive, context
        )
        context.pending_intents = list(context.perception.intents)
        state.messages.append(Message("customer", context.perception.transcript))

        # 2. Identify the customer and load data needed by the agent.
        context.identity = await self._run(
            "identity", self.stages.identity.resolve_identity, context
        )
        state.identity = context.identity
        context.retrieved = await self._run(
            "retrieve", self.stages.retrieve.retrieve, context
        )
        context.call_brief = await self._run(
            "call_brief", self.stages.call_brief.build_call_brief, context
        )
        state.call_brief = context.call_brief

        # 3. Repeat Plan -> Guardrail -> Act -> Observe until the agent is done.
        for _ in range(self.max_agent_steps):
            context.plan = await self._run(
                "plan", self.stages.plan.plan, context
            )
            context.policy = await self._run(
                "guardrail", self.stages.guardrail.check, context
            )

            if context.policy.safe_plan is not None:
                context.plan = context.policy.safe_plan

            if context.policy.allowed:
                context.action_result = await self._run(
                    "act", self.stages.act.act, context
                )
            else:
                context.action_result = ActionResult(
                    status=ActionStatus.BLOCKED,
                    error=context.policy.reason or "action blocked by policy",
                )

            context.observation = await self._run(
                "observe", self.stages.observe.observe, context
            )
            context.steps.append(
                AgentStep(
                    plan=context.plan,
                    policy=context.policy,
                    action_result=context.action_result,
                    observation=context.observation,
                )
            )

            if not context.policy.allowed or not context.observation.should_continue:
                break
        else:
            raise AgentLoopLimitError(
                f"agent exceeded {self.max_agent_steps} steps for "
                f"conversation '{turn_input.conversation_id}'"
            )

        if (
            context.call_brief is None
            or context.action_result is None
            or context.observation is None
        ):
            raise RuntimeError("pipeline did not produce all required results")
        response_text = self._response_text(context)
        if response_text:
            state.messages.append(Message("agent", response_text))
        state.turn_number += 1

        # 4. Save the completed turn for future turns and conversations.
        await self._run("persist", self.stages.persist.persist, context)

        return TurnResult(
            conversation_id=turn_input.conversation_id,
            turn_number=state.turn_number,
            response_text=response_text,
            call_brief=context.call_brief,
            action_result=context.action_result,
            observation=context.observation,
            steps=list(context.steps),
            state=state,
        )

    async def _run(
        self,
        stage_name: str,
        operation: Callable[[TurnContext], Awaitable[Any]],
        context: TurnContext,
    ) -> Any:
        try:
            return await operation(context)
        except Exception as error:
            raise PipelineStageError(
                stage_name, context.input.conversation_id, error
            ) from error

    @staticmethod
    def _response_text(context: TurnContext) -> str | None:
        if context.action_result is None:
            return None
        if context.action_result.status is ActionStatus.BLOCKED:
            return None

        value = context.action_result.output.get("response_text")
        if value is not None:
            return str(value)
        return context.plan.response_text if context.plan else None
