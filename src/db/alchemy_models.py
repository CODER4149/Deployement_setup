from loguru import logger
from .alchemy import Base

try:  # Users/Employee Tables

    deployement_types = Base.classes.deployement_types
    errors = Base.classes.errors
    gateway_setup_schema = Base.classes.gateway_setup_schema
    main_services = Base.classes.main_services
    organization = Base.classes.organization
    service_types = Base.classes.service_types

except Exception as err:
    logger.error("error while creating models - {}".format(err))
