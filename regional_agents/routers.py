from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query

from regional_agents.models import RegionalAgents
from regional_agents.schemas import (
    FilterRegionalAgent,
    RegionalAgentCreate,
    RegionalAgentResponse,
    RegionalAgentResponseWithUser,
    RegionalAgentUpdate,
)
from regional_agents.services import RegionalAgentsService
from users.models import User
from users.schemas import UserResponse
from users.services import UserService

regional_agents_router = APIRouter(tags=["regional agent"], prefix="/agent")


@regional_agents_router.post("/create")
async def create_regional_agent(
    current_user: Annotated[User, Depends(UserService().get_current_user)],
    new_regional_agent: RegionalAgentCreate,
) -> RegionalAgentResponse:
    regional_agent = await RegionalAgentsService().create_regional_agent(
        current_user, new_regional_agent
    )
    return RegionalAgentResponse(**regional_agent.model_dump())


@regional_agents_router.get("/all")
async def get_regional_agents() -> List[RegionalAgentResponseWithUser]:
    return [
        RegionalAgentResponseWithUser(**agent.model_dump())
        for agent in await RegionalAgentsService().get_all_regional_agents()
    ]


@regional_agents_router.get("/{agent_id}/email")
async def get_user_email_by_agent_id(agent_id: int) -> Optional[str]:
    return await RegionalAgentsService().get_user_email_by_agent_id(agent_id)


@regional_agents_router.get("/{user_id}")
async def get_regional_agent_by_user_id(user_id: int) -> RegionalAgentResponse:
    regional_agent = await RegionalAgentsService().get_regional_agent_by_user_id(
        user_id
    )
    return RegionalAgentResponse(**regional_agent.model_dump())


@regional_agents_router.put("/update")
async def update_regional_agent(
    current_user: Annotated[User, Depends(UserService().get_current_user)],
    new_regional_agent: RegionalAgentUpdate,
) -> RegionalAgentResponse:
    updated_regional_agent = await RegionalAgentsService().update(
        current_user, new_regional_agent
    )
    return RegionalAgentResponse(**updated_regional_agent.model_dump())


@regional_agents_router.post("/search")
async def search_regional_agent(
    # current_user: Annotated[User, Depends(UserService().get_current_user)],
    filter_regional_agent: FilterRegionalAgent,
) -> List[RegionalAgentResponse]:
    res = []
    for agent in await RegionalAgentsService().search_regional_agent(
        filter_regional_agent
    ):
        res.append(RegionalAgentResponse(**agent.model_dump()))
    return res


@regional_agents_router.post("/info")
async def get_regional_agents_info(
    regional_agents_id: List[int],
) -> List[RegionalAgentResponse]:
    return [
        RegionalAgentResponse(**agent.model_dump())
        for agent in await RegionalAgentsService().get_regional_agents_info(
            regional_agents_id
        )
    ]


@regional_agents_router.post("/{agent_id}")
async def get_user_by_regional_id(agent_id: int) -> UserResponse:
    user = await RegionalAgentsService().get_user_by_regional_id(agent_id)
    return UserResponse(**user.model_dump())


@regional_agents_router.post("/info/subject")
async def get_regional_agent_by_federal_subject(
    federal_subject: str,
) -> RegionalAgentResponse:
    regional_agent = (
        await RegionalAgentsService().get_regional_agent_by_federal_subject(
            federal_subject
        )
    )
    return RegionalAgentResponse(**regional_agent.model_dump())
