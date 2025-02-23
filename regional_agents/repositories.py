from typing import List, Optional

from ormar import MultipleMatches

from users.models import User
from utils.js_parse import load_agents

from .exceptions import RegionalAgentNotFoundException
from .models import RegionalAgents
from .schemas import FilterRegionalAgent, RegionalAgentCreate, RegionalAgentUpdate


class RegionalAgentsRepository:
    """Repository for managing RegionalAgents."""

    @staticmethod
    async def create_regional_agent(
        user: User, regional_agent_create: RegionalAgentCreate
    ) -> RegionalAgents:
        """Creates or updates a regional agent.

        Args:
            user: The user creating the agent.
            regional_agent_create: Data for creating/updating the agent.

        Returns:
            The created/updated RegionalAgents object.

        Raises:
            RegionalAgentNotFoundException: If no agent is found for the given federal subject.
        """
        # Attempt to retrieve an existing regional agent based on the federal subject.
        regional_agent = (
            await RegionalAgentsRepository.get_regional_agent_by_federal_subject(
                regional_agent_create.federal_subject
            )
        )

        if regional_agent is None:
            raise RegionalAgentNotFoundException()

        # Update the existing regional agent.  Note that we are constructing the fio field and adding the user_id.
        regional_agent = await regional_agent.update(
            **regional_agent_create.model_dump(
                exclude={"federal_subject", "fio"}, exclude_none=True
            ),
            fio=f"{user.name} {user.surname} {user.patronymic}",
            user_id=user,
        )

        return regional_agent

    @staticmethod
    async def get_regional_agent_by_user_id(user_id: int) -> Optional[RegionalAgents]:
        """Retrieves a regional agent by user ID.

        Args:
            user_id: The ID of the user.

        Returns:
            The RegionalAgents object, or None if not found.
        """
        return await RegionalAgents.objects.get_or_none(user_id=user_id)

    @staticmethod
    async def get_regional_agent_by_id(
        regional_agent_id: int,
    ) -> Optional[RegionalAgents]:
        """Retrieves a regional agent by its ID.

        Args:
            regional_agent_id: The ID of the regional agent.

        Returns:
            The RegionalAgents object, or None if not found.
        """
        return await RegionalAgents.objects.get_or_none(id=regional_agent_id)

    @staticmethod
    async def update(
        regional_agent: RegionalAgents, agent_update: RegionalAgentUpdate
    ) -> RegionalAgents:
        """Updates a regional agent.

        Args:
            regional_agent: The RegionalAgents object to update.
            agent_update: Data for updating the agent.

        Returns:
            The updated RegionalAgents object.
        """
        # Update the regional agent using the provided data, ignoring any fields that are not set in agent_update.
        return await regional_agent.update(
            **agent_update.model_dump(exclude_unset=True)
        )

    @staticmethod
    async def search_regional_agent(
        filter_regional_agent: FilterRegionalAgent,
    ) -> list[RegionalAgents]:
        """Searches for regional agents based on provided filters.

        Args:
            filter_regional_agent: A FilterRegionalAgent object containing search criteria.

        Returns:
            A list of matching RegionalAgents objects.
        """
        execute = RegionalAgents.objects

        if filter_regional_agent.title is not None:
            execute = execute.filter(title__icontains=filter_regional_agent.title)
        if filter_regional_agent.federal_subject is not None:
            execute = execute.filter(
                federal_subject__icontains=filter_regional_agent.federal_subject
            )

        if filter_regional_agent.fio is not None:
            execute = execute.filter(fio__icontains=filter_regional_agent.fio)

        execute = (
            execute.order_by("id")
            .offset(filter_regional_agent.offset)
            .limit(filter_regional_agent.limit)
        )

        return await execute.all()

    @staticmethod
    async def get_regional_agents_info(
        regional_agents_id: List[int],
    ) -> List[RegionalAgents]:
        """Retrieves regional agents by a list of IDs.

        Args:
            regional_agents_id: A list of regional agent IDs.

        Returns:
            A list of RegionalAgents objects.
        """
        return await RegionalAgents.objects.filter(id__in=regional_agents_id).all()

    @staticmethod
    async def get_user_by_regional_id(regional_agent_id: int) -> Optional[User]:
        """Retrieves the user associated with a regional agent ID.

        Args:
            regional_agent_id: The ID of the regional agent.

        Returns:
            The User object, or None if not found.

        Raises:
            RegionalAgentNotFoundException: If the regional agent is not found.
        """
        regional_agent = await RegionalAgents.objects.select_related(
            "user_id"
        ).get_or_none(id=regional_agent_id)
        if regional_agent is None:
            raise RegionalAgentNotFoundException()
        return regional_agent.user_id

    @staticmethod
    async def get_regional_agent_by_federal_subject(
        subject: str,
    ) -> Optional[RegionalAgents]:
        """Retrieves a regional agent by federal subject. Handles cases with multiple matches.

        Args:
            subject: The federal subject.

        Returns:
            The RegionalAgents object, or None if not found.
        """
        try:
            # Attempt to get the agent; if only one exists, this will succeed.
            if agent := await RegionalAgents.objects.get_or_none(
                federal_subject=subject
            ):
                return agent
        except MultipleMatches:
            # Handle the case where multiple agents exist for the same federal subject - returns the first one.
            return await RegionalAgents.objects.first(federal_subject=subject)

    @staticmethod
    async def first_upload_regional_agents() -> None:
        """Performs the initial upload of regional agents from an external source."""
        agents = load_agents()
        for agent in agents:
            # Check if an agent already exists for this federal subject.
            db_agent = (
                await RegionalAgentsRepository.get_regional_agent_by_federal_subject(
                    agent["name"]
                )
            )
            if db_agent is None:
                # Create a new regional agent if one doesn't exist.
                db_agent = RegionalAgents(
                    fio=agent["chief"],
                    email=agent["email"],
                    title=agent["district"],
                    federal_subject=agent["name"],
                    iso_code=agent["iso_code"],
                    region_emblem_url=agent["region_emblem_url"],
                )
                await db_agent.save()
            elif db_agent.user_id is None:
                # Update an existing agent only if it doesn't have a user associated yet.
                await db_agent.update(
                    fio=agent["chief"],
                    email=agent["email"],
                    title=agent["district"],
                    federal_subject=agent["name"],
                    iso_code=agent["iso_code"],
                    region_emblem_url=agent["region_emblem_url"],
                )

    @staticmethod
    async def get_all_regional_agents() -> List[RegionalAgents]:
        """Retrieves all regional agents, including related user information.

        Returns:
            A list of all RegionalAgents objects.
        """
        return await RegionalAgents.objects.select_related("user_id").all()

    @staticmethod
    async def get_user_email_by_agent_id(agent_id: int) -> Optional[RegionalAgents]:
        """Retrieves a regional agent and its associated user's email by agent ID.

        Args:
            agent_id: The ID of the regional agent.

        Returns:
            The RegionalAgents object, including user information, or None if not found.
        """
        return await RegionalAgents.objects.select_related("user_id").get_or_none(
            id=agent_id
        )
