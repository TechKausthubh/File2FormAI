import uuid

from sqlalchemy.exc import IntegrityError

from file2formai.core.errors import ConflictError, ResourceNotFoundError
from file2formai.equipment.models import EquipmentInstance, EquipmentModel
from file2formai.equipment.repository import EquipmentUnitOfWork
from file2formai.equipment.schemas import (
    EquipmentInstanceCreate,
    EquipmentInstanceResponse,
    EquipmentInstanceUpdate,
    EquipmentModelCreate,
    EquipmentModelResponse,
    EquipmentModelUpdate,
)
from file2formai.identity.context import RequestContext, require_org_admin


class EquipmentService:
    def __init__(self, unit_of_work: EquipmentUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def list_models(self, context: RequestContext) -> list[EquipmentModelResponse]:
        models = await self._unit_of_work.equipment.list_models(context.organization_id)
        return [EquipmentModelResponse.model_validate(model) for model in models]

    async def get_model(
        self,
        context: RequestContext,
        equipment_model_id: uuid.UUID,
    ) -> EquipmentModelResponse:
        model = await self._get_model(context.organization_id, equipment_model_id)
        return EquipmentModelResponse.model_validate(model)

    async def create_model(
        self,
        context: RequestContext,
        create: EquipmentModelCreate,
    ) -> EquipmentModelResponse:
        require_org_admin(context)
        model = EquipmentModel(
            organization_id=context.organization_id,
            manufacturer=create.manufacturer,
            model_name=create.model_name,
            description=create.description,
            metadata_=create.metadata,
        )
        self._unit_of_work.equipment.add_model(context.organization_id, model)
        await self._unit_of_work.commit()
        await self._unit_of_work.refresh(model)
        return EquipmentModelResponse.model_validate(model)

    async def update_model(
        self,
        context: RequestContext,
        equipment_model_id: uuid.UUID,
        update: EquipmentModelUpdate,
    ) -> EquipmentModelResponse:
        require_org_admin(context)
        model = await self._get_model(context.organization_id, equipment_model_id)
        values = update.model_dump(exclude_unset=True)
        if "metadata" in values:
            values["metadata_"] = values.pop("metadata")
        for field_name, value in values.items():
            setattr(model, field_name, value)
        await self._unit_of_work.commit()
        await self._unit_of_work.refresh(model)
        return EquipmentModelResponse.model_validate(model)

    async def delete_model(
        self,
        context: RequestContext,
        equipment_model_id: uuid.UUID,
    ) -> None:
        require_org_admin(context)
        model = await self._get_model(context.organization_id, equipment_model_id)
        if await self._unit_of_work.equipment.model_has_instances(
            context.organization_id, equipment_model_id
        ):
            raise ConflictError(
                "Equipment model cannot be deleted while equipment instances reference it"
            )
        await self._unit_of_work.equipment.delete_model(context.organization_id, model)
        await self._unit_of_work.commit()

    async def list_instances(
        self,
        context: RequestContext,
    ) -> list[EquipmentInstanceResponse]:
        instances = await self._unit_of_work.equipment.list_instances(context.organization_id)
        return [EquipmentInstanceResponse.model_validate(instance) for instance in instances]

    async def get_instance(
        self,
        context: RequestContext,
        equipment_instance_id: uuid.UUID,
    ) -> EquipmentInstanceResponse:
        instance = await self._get_instance(context.organization_id, equipment_instance_id)
        return EquipmentInstanceResponse.model_validate(instance)

    async def create_instance(
        self,
        context: RequestContext,
        create: EquipmentInstanceCreate,
    ) -> EquipmentInstanceResponse:
        require_org_admin(context)
        await self._get_model(context.organization_id, create.equipment_model_id)
        instance = EquipmentInstance(
            organization_id=context.organization_id,
            equipment_model_id=create.equipment_model_id,
            serial_number=create.serial_number,
            display_name=create.display_name,
            metadata_=create.metadata,
        )
        self._unit_of_work.equipment.add_instance(context.organization_id, instance)
        await self._commit_instance(instance)
        return EquipmentInstanceResponse.model_validate(instance)

    async def update_instance(
        self,
        context: RequestContext,
        equipment_instance_id: uuid.UUID,
        update: EquipmentInstanceUpdate,
    ) -> EquipmentInstanceResponse:
        require_org_admin(context)
        instance = await self._get_instance(context.organization_id, equipment_instance_id)
        values = update.model_dump(exclude_unset=True)
        if "equipment_model_id" in values:
            await self._get_model(context.organization_id, values["equipment_model_id"])
        if "metadata" in values:
            values["metadata_"] = values.pop("metadata")
        for field_name, value in values.items():
            setattr(instance, field_name, value)
        await self._commit_instance(instance)
        return EquipmentInstanceResponse.model_validate(instance)

    async def delete_instance(
        self,
        context: RequestContext,
        equipment_instance_id: uuid.UUID,
    ) -> None:
        require_org_admin(context)
        instance = await self._get_instance(context.organization_id, equipment_instance_id)
        await self._unit_of_work.equipment.delete_instance(context.organization_id, instance)
        await self._unit_of_work.commit()

    async def _get_model(
        self,
        organization_id: uuid.UUID,
        equipment_model_id: uuid.UUID,
    ) -> EquipmentModel:
        model = await self._unit_of_work.equipment.get_model(organization_id, equipment_model_id)
        if model is None:
            raise ResourceNotFoundError
        return model

    async def _get_instance(
        self,
        organization_id: uuid.UUID,
        equipment_instance_id: uuid.UUID,
    ) -> EquipmentInstance:
        instance = await self._unit_of_work.equipment.get_instance(
            organization_id, equipment_instance_id
        )
        if instance is None:
            raise ResourceNotFoundError
        return instance

    async def _commit_instance(self, instance: EquipmentInstance) -> None:
        try:
            await self._unit_of_work.commit()
        except IntegrityError as error:
            await self._unit_of_work.rollback()
            raise ResourceNotFoundError from error
        await self._unit_of_work.refresh(instance)
