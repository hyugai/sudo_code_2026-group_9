"""LangGraph orchestrator replacing the custom PipelineStages loop."""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from pydantic import TypeAdapter
from telesale_agent.core.models import (
    TurnContext, AgentStep, TurnInput, ConversationState, TurnResult, Message
)
from telesale_agent.core.interfaces import (
    Perceiver, IdentityResolver, Retriever, CallBriefBuilder,
    Planner, Guardrail, Actor, Observer, Persister
)

class AgentState(TypedDict):
    context: TurnContext

ctx_adapter = TypeAdapter(TurnContext)

def _get_ctx(state: AgentState) -> TurnContext:
    raw_ctx = state["context"]
    if isinstance(raw_ctx, dict):
        return ctx_adapter.validate_python(raw_ctx)
    return raw_ctx

class LangGraphAgentHarness:
    """A wrapper that compiles and runs a LangGraph instead of a custom for-loop."""
    
    def __init__(self,
                 perceive: Perceiver,
                 identity: IdentityResolver,
                 retrieve: Retriever,
                 call_brief: CallBriefBuilder,
                 plan: Planner,
                 guardrail: Guardrail,
                 act: Actor,
                 observe: Observer,
                 persist: Persister,
                 max_steps: int = 5):
        
        self.perceive = perceive
        self.identity = identity
        self.retrieve = retrieve
        self.call_brief = call_brief
        self.plan = plan
        self.guardrail = guardrail
        self.act = act
        self.observe = observe
        self.persist = persist
        self.max_steps = max_steps
        
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        # Define Nodes
        async def node_perceive(state: AgentState):
            ctx = _get_ctx(state)
            ctx.perception = await self.perceive.perceive(ctx)
            ctx.state.messages.append(Message("customer", ctx.perception.transcript))
            return {"context": ctx}

        async def node_identity(state: AgentState):
            ctx = _get_ctx(state)
            ctx.identity = await self.identity.resolve_identity(ctx)
            ctx.state.identity = ctx.identity
            return {"context": ctx}

        async def node_retrieve(state: AgentState):
            ctx = _get_ctx(state)
            ctx.retrieved = await self.retrieve.retrieve(ctx)
            ctx.state.retrieved_data = ctx.retrieved
            return {"context": ctx}

        async def node_call_brief(state: AgentState):
            ctx = _get_ctx(state)
            ctx.call_brief = await self.call_brief.build_call_brief(ctx)
            ctx.state.call_brief = ctx.call_brief
            return {"context": ctx}

        async def node_plan(state: AgentState):
            ctx = _get_ctx(state)
            ctx.plan = await self.plan.plan(ctx)
            return {"context": ctx}

        async def node_guardrail(state: AgentState):
            ctx = _get_ctx(state)
            ctx.policy = await self.guardrail.check(ctx)
            if ctx.policy.safe_plan is not None:
                ctx.plan = ctx.policy.safe_plan
            return {"context": ctx}

        async def node_act(state: AgentState):
            ctx = _get_ctx(state)
            if ctx.policy.allowed:
                ctx.action_result = await self.act.act(ctx)
            return {"context": ctx}

        async def node_observe(state: AgentState):
            ctx = _get_ctx(state)
            if ctx.policy.allowed:
                ctx.observation = await self.observe.observe(ctx)
            
            # Save the step to context history
            if ctx.plan and ctx.policy and ctx.action_result and ctx.observation:
                ctx.steps.append(
                    AgentStep(
                        plan=ctx.plan,
                        policy=ctx.policy,
                        action_result=ctx.action_result,
                        observation=ctx.observation,
                    )
                )
            return {"context": ctx}

        async def node_persist(state: AgentState):
            ctx = _get_ctx(state)
            await self.persist.persist(ctx)
            if ctx.plan and ctx.plan.response_text:
                ctx.state.messages.append(Message("agent", ctx.plan.response_text))
            return {"context": ctx}

        # Add Nodes to Graph
        workflow.add_node("perceive", node_perceive)
        workflow.add_node("identity", node_identity)
        workflow.add_node("retrieve", node_retrieve)
        workflow.add_node("call_brief", node_call_brief)
        workflow.add_node("plan", node_plan)
        workflow.add_node("guardrail", node_guardrail)
        workflow.add_node("act", node_act)
        workflow.add_node("observe", node_observe)
        workflow.add_node("persist", node_persist)

        # Edges
        # Conditional start: If identity is missing, do initialization first
        def route_start(state: AgentState) -> str:
            ctx = _get_ctx(state)
            if not ctx.state.identity:
                return "identity"
            return "perceive"
            
        workflow.add_conditional_edges(
            START,
            route_start,
            {"identity": "identity", "perceive": "perceive"}
        )

        # Initialization phase
        workflow.add_edge("identity", "retrieve")
        workflow.add_edge("retrieve", "perceive")
        
        # Turn loop phase
        workflow.add_edge("perceive", "call_brief")
        workflow.add_edge("call_brief", "plan")
        
        workflow.add_edge("plan", "guardrail")
        workflow.add_edge("guardrail", "act")
        workflow.add_edge("act", "observe")

        # Conditional Edge after observe
        def should_continue(state: AgentState) -> str:
            ctx = _get_ctx(state)
            if not ctx.policy.allowed:
                return "persist"
            # To prevent infinite loops
            if len(ctx.steps) >= self.max_steps:
                return "persist"
            if ctx.observation and ctx.observation.should_continue:
                return "plan"
            return "persist"

        workflow.add_conditional_edges(
            "observe",
            should_continue,
            {"plan": "plan", "persist": "persist"}
        )
        
        workflow.add_edge("persist", END)

        return workflow.compile()
        
    async def run_turn(
        self,
        turn_input: TurnInput,
        state: ConversationState | None = None,
    ) -> TurnResult:
        """Run the graph asynchronously."""
        state = state or ConversationState(conversation_id=turn_input.conversation_id)
        if state.conversation_id != turn_input.conversation_id:
            raise ValueError("state and input must belong to the same conversation")

        context = TurnContext(input=turn_input, state=state)
        
        # Load initialization data into TurnContext if it exists
        if state.identity:
            context.identity = state.identity
        if state.retrieved_data:
            context.retrieved = state.retrieved_data
            
        initial_state = {"context": context}
        
        final_state = await self.graph.ainvoke(initial_state)
        ctx = final_state["context"]
        
        state.turn_number += 1
        return TurnResult(
            conversation_id=state.conversation_id,
            turn_number=state.turn_number,
            response_text=ctx.plan.response_text if ctx.plan else None,
            perception=ctx.perception,
            identity=ctx.identity,
            retrieved=ctx.retrieved,
            call_brief=ctx.call_brief,
            action_result=ctx.action_result,
            observation=ctx.observation,
            steps=ctx.steps,
            state=state,
        )
