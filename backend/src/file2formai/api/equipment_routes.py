import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from file2formai.api.dependencies import get_equipment_service, get_request_context
from file2formai.equipment.schemas import (
    EquipmentInstanceCreate,
    EquipmentInstanceResponse,
    EquipmentInstanceUpdate,
    EquipmentModelCreate,
    EquipmentModelResponse,
    EquipmentModelUpdate,
)
from file2formai.equipment.service import EquipmentService
from file2formai.identity.context import RequestContext

router = APIRouter(prefix="/api/v1", tags=["equipment"])

ContextDependency = Annotated[RequestContext, Depends(get_request_context)]
EquipmentServiceDependency = Annotated[EquipmentService, Depends(get_equipment_service)]


@router.get("/equipment-models", response_model=list[EquipmentModelResponse])
async def list_equipment_models(
    context: ContextDependency,
    service: EquipmentServiceDependency,
) -> list[EquipmentModelResponse]:
    return await service.list_models(context)


@router.post(
    "/equipment-models",
    response_model=EquipmentModelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_equipment_model(
    create: EquipmentModelCreate,
    context: ContextDependency,
    service: EquipmentServiceDependency,
) -> EquipmentModelResponse:
    return await service.create_model(context, create)


@router.get("/equipment-models/{equipment_model_id}", response_model=EquipmentModelResponse)
async def get_equipment_model(
    equipment_model_id: uuid.UUID,
    context: ContextDependency,
    service: EquipmentServiceDependency,
) -> EquipmentModelResponse:
    return await service.get_model(context, equipment_model_id)


@router.patch("/equipment-models/{equipment_model_id}", response_model=EquipmentModelResponse)
async def update_equipment_model(
    equipment_model_id: uuid.UUID,
    update: EquipmentModelUpdate,
    context: ContextDependency,
    service: EquipmentServiceDependency,
) -> EquipmentModelResponse:
    return await service.update_model(context, equipment_model_id, update)


@router.delete(
    "/equipment-models/{equipment_model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_equipment_model(
    equipment_model_id: uuid.UUID,
    context: ContextDependency,
    service: EquipmentServiceDependency,
) -> Response:
    await service.delete_model(context, equipment_model_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/equipment-instances", response_model=list[EquipmentInstanceResponse])
async def list_equipment_instances(
    context: ContextDependency,
    service: EquipmentServiceDependency,
) -> list[EquipmentInstanceResponse]:
    return await service.list_instances(context)


@router.post(
    "/equipment-instances",
    response_model=EquipmentInstanceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_equipment_instance(
    create: EquipmentInstanceCreate,
    context: ContextDependency,
    service: EquipmentServiceDependency,
) -> EquipmentInstanceResponse:
    return await service.create_instance(context, create)


@router.get(
    "/equipment-instances/{equipment_instance_id}",
    response_model=EquipmentInstanceResponse,
)
async def get_equipment_instance(
    equipment_instance_id: uuid.UUID,
    context: ContextDependency,
    service: EquipmentServiceDependency,
) -> EquipmentInstanceResponse:
    return await service.get_instance(context, equipment_instance_id)


@router.patch(
    "/equipment-instances/{equipment_instance_id}",
    response_model=EquipmentInstanceResponse,
)
async def update_equipment_instance(
    equipment_instance_id: uuid.UUID,
    update: EquipmentInstanceUpdate,
    context: ContextDependency,
    service: EquipmentServiceDependency,
) -> EquipmentInstanceResponse:
    return await service.update_instance(context, equipment_instance_id, update)


@router.delete(
    "/equipment-instances/{equipment_instance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_equipment_instance(
    equipment_instance_id: uuid.UUID,
    context: ContextDependency,
    service: EquipmentServiceDependency,
) -> Response:
    await service.delete_instance(context, equipment_instance_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
