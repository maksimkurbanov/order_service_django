from dependency_injector import containers, providers

from src.application.usecases.create_order import CreateOrderUseCase
from src.application.usecases.get_order import GetOrderUseCase
from src.infrastructure.external.capashino import CatalogClient
from src.infrastructure.orm.repositories import (
    DjangoOrderRepository,
    DjangoPaymentRepository,
)
from src.infrastructure.orm.unit_of_work import DjangoUnitOfWork


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.capashino_api_key.from_env("LMS_API_KEY", required=True)
    config.capashino_base_url.from_env("CAPASHINO_URL", required=True)

    order_repo = providers.Factory(DjangoOrderRepository)
    payment_repo = providers.Factory(DjangoPaymentRepository)
    uow = providers.Factory(DjangoUnitOfWork)
    catalog_client = providers.Singleton(
        CatalogClient,
        api_key=config.capashino_api_key,
        base_url=config.capashino_base_url,
    )

    create_order_use_case = providers.Factory(
        CreateOrderUseCase,
        unit_of_work=uow,
        catalog_client=catalog_client,
    )
    get_order_use_case = providers.Factory(
        GetOrderUseCase,
        unit_of_work=uow,
    )
