import uuid

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from file2formai.equipment.models import EquipmentInstance, EquipmentModel


class EquipmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_models(self, organization_id: uuid.UUID) -> list[EquipmentModel]:
        statement = (
            select(EquipmentModel)
            .where(EquipmentModel.organization_id == organization_id)
            .order_by(EquipmentModel.created_at, EquipmentModel.id)
        )
        return list((await self._session.scalars(statement)).all())

    async def get_model(
        self,
        organization_id: uuid.UUID,
        equipment_model_id: uuid.UUID,
    ) -> EquipmentModel | None:
        statement = select(EquipmentModel).where(
            EquipmentModel.organization_id == organization_id,
            EquipmentModel.id == equipment_model_id,
        )
        return (await self._session.scalars(statement)).one_or_none()

    def add_model(
        self,
        organization_id: uuid.UUID,
        equipment_model: EquipmentModel,
    ) -> None:
        if equipment_model.organization_id != organization_id:
            raise ValueError("equipment model organization does not match repository scope")
        self._session.add(equipment_model)

    async def model_has_instances(
        self,
        organization_id: uuid.UUID,
        equipment_model_id: uuid.UUID,
    ) -> bool:
        statement = select(
            exists().where(
                EquipmentInstance.organization_id == organization_id,
                EquipmentInstance.equipment_model_id == equipment_model_id,
            )
        )
        return bool(await self._session.scalar(statement))

    async def delete_model(
        self,
        organization_id: uuid.UUID,
        equipment_model: EquipmentModel,
    ) -> None:
        if equipment_model.organization_id != organization_id:
            raise ValueError("equipment model organization does not match repository scope")
        await self._session.delete(equipment_model)

    async def list_instances(self, organization_id: uuid.UUID) -> list[EquipmentInstance]:
        statement = (
            select(EquipmentInstance)
            .where(EquipmentInstance.organization_id == organization_id)
            .order_by(EquipmentInstance.created_at, EquipmentInstance.id)
        )
        return list((await self._session.scalars(statement)).all())

    async def get_instance(
        self,
        organization_id: uuid.UUID,
        equipment_instance_id: uuid.UUID,
    ) -> EquipmentInstance | None:
        statement = select(EquipmentInstance).where(
            EquipmentInstance.organization_id == organization_id,
            EquipmentInstance.id == equipment_instance_id,
        )
        return (await self._session.scalars(statement)).one_or_none()

    def add_instance(
        self,
        organization_id: uuid.UUID,
        equipment_instance: EquipmentInstance,
    ) -> None:
        if equipment_instance.organization_id != organization_id:
            raise ValueError("equipment instance organization does not match repository scope")
        self._session.add(equipment_instance)

    async def delete_instance(
        self,
        organization_id: uuid.UUID,
        equipment_instance: EquipmentInstance,
    ) -> None:
        if equipment_instance.organization_id != organization_id:
            raise ValueError("equipment instance organization does not match repository scope")
        await self._session.delete(equipment_instance)


class EquipmentUnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.equipment = EquipmentRepository(session)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def refresh(self, instance: object) -> None:
        await self.session.refresh(instance)
