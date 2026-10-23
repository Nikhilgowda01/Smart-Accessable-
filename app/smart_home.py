
"""FastAPI routes for the simulated AccessAble smart-home agent."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agent.executor import execute_plan, get_device_states
from agent.planner import create_action_plan
from agent.schemas import ActionPlan

router = APIRouter(prefix="/api/smart-home", tags=["Smart Home"])


class PlanRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class ExecuteRequest(BaseModel):
    plan: ActionPlan


@router.post("/plan")
def plan_smart_home_command(req: PlanRequest):
    try:
        plan = create_action_plan(req.message)
        return {
            "plan": plan.model_dump(),
            "device_states": get_device_states(),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Could not create a safe action plan: {type(exc).__name__}",
        ) from exc


@router.post("/execute")
def execute_smart_home_command(req: ExecuteRequest):
    try:
        # Door-lock confirmation must be handled through a trusted,
        # authenticated confirmation flow before enabling door execution.
        result = execute_plan(req.plan, confirmed_action_ids=set())
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/devices")
def get_smart_home_devices():
    return {"devices": get_device_states()}
