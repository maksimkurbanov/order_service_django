from dependency_injector import containers, providers

from src.application.usecases.create_order import CreateOrderUseCase
from src.application.usecases.get_order import GetOrderUseCase
from src.application.usecases.process_inbox import ProcessInboxUseCase
from src.application.usecases.process_outbox import ProcessOutboxUseCase
from src.application.usecases.process_payment_callback import (
    ProcessPaymentCallbackUseCase,
)
from src.application.usecases.write_to_inbox import WriteToInboxUseCase
from src.infrastructure.external.capashino import (
    CatalogClient,
    PaymentClient,
    NotificationClient,
)
from src.infrastructure.external.kafka_consumer import KafkaConsumer
from src.infrastructure.external.kafka_producer import KafkaProducer
from src.infrastructure.orm.repositories import (
    DjangoOrderRepository,
    DjangoPaymentRepository,
    DjangoOutboxRepository,
    DjangoInboxRepository,
)
from src.infrastructure.orm.unit_of_work import DjangoUnitOfWork


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.capashino_api_key.from_env("LMS_API_KEY", required=True)
    config.capashino_base_url.from_env("CAPASHINO_URL", required=True)
    config.callback_base_url.from_env("CALLBACK_URL", required=True)
    config.outbox_max_retries.from_env("OUTBOX_MAX_RETRIES", required=True)
    config.kafka_bootstrap_servers.from_env("KAFKA_BOOTSTRAP_SERVERS", required=True)
    config.kafka_outbox_topic.from_env("KAFKA_OUTBOX_TOPIC", required=True)
    config.kafka_inbox_topic.from_env("KAFKA_INBOX_TOPIC", required=True)

    order_repo = providers.Singleton(DjangoOrderRepository)
    payment_repo = providers.Singleton(DjangoPaymentRepository)
    outbox_repo = providers.Singleton(DjangoOutboxRepository)
    inbox_repo = providers.Singleton(DjangoInboxRepository)

    uow = providers.Factory(
        DjangoUnitOfWork,
        order_repo=order_repo,
        payment_repo=payment_repo,
        outbox_repo=outbox_repo,
        inbox_repo=inbox_repo,
    )
    catalog_client = providers.Singleton(
        CatalogClient,
        api_key=config.capashino_api_key,
        base_url=config.capashino_base_url,
    )
    payment_client = providers.Singleton(
        PaymentClient,
        api_key=config.capashino_api_key,
        base_url=config.capashino_base_url,
        callback_base_url=config.callback_base_url,
    )
    notification_client = providers.Singleton(
        NotificationClient,
        api_key=config.capashino_api_key,
        base_url=config.capashino_base_url,
    )
    kafka_producer = providers.Singleton(
        KafkaProducer,
        bootstrap_servers=config.kafka_bootstrap_servers,
        topic=config.kafka_outbox_topic,
    )
    kafka_consumer = providers.Singleton(
        KafkaConsumer,
        bootstrap_servers=config.kafka_bootstrap_servers,
        topic=config.kafka_inbox_topic,
        group_id="inbox-consumer",
    )

    create_order_use_case = providers.Factory(
        CreateOrderUseCase,
        unit_of_work=uow,
        catalog_client=catalog_client,
        payment_client=payment_client,
    )
    get_order_use_case = providers.Factory(
        GetOrderUseCase,
        unit_of_work=uow,
    )
    process_payment_callback_use_case = providers.Factory(
        ProcessPaymentCallbackUseCase,
        unit_of_work=uow,
    )
    process_outbox_use_case = providers.Factory(
        ProcessOutboxUseCase,
        unit_of_work=uow,
        event_publisher=kafka_producer,
        notification_service=notification_client,
        max_retries=config.outbox_max_retries,
    )
    write_to_inbox_use_case = providers.Factory(
        WriteToInboxUseCase,
        unit_of_work=uow,
        consumer=kafka_consumer,
    )
    process_inbox_use_case = providers.Factory(ProcessInboxUseCase, unit_of_work=uow)
