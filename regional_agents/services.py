from typing import List, Optional

from users.exceptions import UserNotFoundException
from users.models import AgentStatusEnum, User, UserRoleEnum

from .exceptions import (
    RegionalAgentNotFoundException,
    UserNotAgentException,
    UserNotApprovedException,
)
from .models import RegionalAgents
from .repositories import RegionalAgentsRepository
from .schemas import FilterRegionalAgent, RegionalAgentCreate, RegionalAgentUpdate


class RegionalAgentsService:
    """Service layer for managing regional agents."""

    def __init__(self) -> None:
        self.repository = RegionalAgentsRepository()

    async def create_regional_agent(
        self, user: User, regional_agent_create: RegionalAgentCreate
    ) -> RegionalAgents:
        """Creates a regional agent.

        Args:
            user: The user creating the agent.
            regional_agent_create: Data for creating the agent.

        Returns:
            The created RegionalAgents object.

        Raises:
            UserNotAgentException: If the user is not an agent.
            UserNotApprovedException: If the user is not approved.
        """
        if user.role != UserRoleEnum.AGENT.value:
            raise UserNotAgentException()
        if user.status != AgentStatusEnum.APPROVED.value:
            raise UserNotApprovedException()

        return await self.repository.create_regional_agent(user, regional_agent_create)

    async def get_regional_agent_by_user_id(self, user_id: int) -> RegionalAgents:
        """Retrieves a regional agent by user ID.

        Args:
            user_id: The ID of the user.

        Returns:
            The RegionalAgents object.

        Raises:
            RegionalAgentNotFoundException: If no regional agent is found for the given user ID.
        """
        regional_agent = await self.repository.get_regional_agent_by_user_id(user_id)
        if regional_agent is None:
            raise RegionalAgentNotFoundException()
        return regional_agent

    async def update(
        self, user: User, agent_update: RegionalAgentUpdate
    ) -> RegionalAgents:
        """Updates a regional agent.

        Args:
            user: The user updating the agent.
            agent_update: Data for updating the agent.

        Returns:
            The updated RegionalAgents object.

        Raises:
            RegionalAgentNotFoundException: If no regional agent is found for the given user ID.

        """
        regional_agent = await self.repository.get_regional_agent_by_user_id(user.id)
        if regional_agent is None:
            raise RegionalAgentNotFoundException()
        regional_agent = await self.repository.update(regional_agent, agent_update)
        return regional_agent

    async def search_regional_agent(
        self, filter_regional_agent: FilterRegionalAgent
    ) -> list[RegionalAgents]:
        """Searches for regional agents based on provided filters.

        Args:
            filter_regional_agent: A FilterRegionalAgent object containing search criteria.

        Returns:
            A list of matching RegionalAgents objects.
        """
        return await self.repository.search_regional_agent(filter_regional_agent)

    async def get_regional_agents_info(
        self, regional_agents_id: List[int]
    ) -> List[RegionalAgents]:
        """Retrieves regional agents by a list of IDs.

        Args:
            regional_agents_id: A list of regional agent IDs.

        Returns:
            A list of RegionalAgents objects.
        """
        return await self.repository.get_regional_agents_info(regional_agents_id)

    async def get_user_by_regional_id(self, regional_agent_id: int) -> Optional[User]:
        """Retrieves the user associated with a regional agent ID.

        Args:
            regional_agent_id: The ID of the regional agent.

        Returns:
            The User object.

        Raises:
            UserNotFoundException: If no user is found for the given regional agent ID.
        """
        user = await self.repository.get_user_by_regional_id(regional_agent_id)
        if user is None:
            raise UserNotFoundException(regional_agent_id)
        return user

    async def get_regional_agent_by_federal_subject(
        self, subject: str
    ) -> RegionalAgents:
        """Retrieves a regional agent by federal subject.

        Args:
            subject: The federal subject.

        Returns:
            The RegionalAgents object.

        Raises:
            RegionalAgentNotFoundException: If no regional agent is found for the given federal subject.
        """
        regional_agent = await self.repository.get_regional_agent_by_federal_subject(
            subject
        )
        if regional_agent is None:
            raise RegionalAgentNotFoundException()
        return regional_agent

    async def first_upload_regional_agents(self) -> None:
        """Performs the initial upload of regional agents from an external source."""
        await self.repository.first_upload_regional_agents()

    async def get_all_regional_agents(self) -> List[RegionalAgents]:
        """Retrieves all regional agents.

        Returns:
            A list of all RegionalAgents objects.
        """
        return await self.repository.get_all_regional_agents()

    async def get_user_email_by_agent_id(self, agent_id: int) -> Optional[str]:
        """Retrieves the email of the user associated with a regional agent ID.

        Args:
            agent_id: The ID of the regional agent.

        Returns:
            The email address of the associated user, or None if not found.
        """
        agent = await self.repository.get_user_email_by_agent_id(agent_id)
        if agent and agent.user_id:
            return agent.user_id.email
        return None
