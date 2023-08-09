import os
from time import sleep

from src.db.alchemy import SessionLocal, engine
from loguru import logger
from utils.deployement_handler import Deployment_Setup

if __name__ == '__main__':
    db = SessionLocal()
    rdb = engine.raw_connection()
    Integration_handler_ = Deployment_Setup(db, rdb)
    try:
        sleep_timer = int(os.getenv("SLEEP_TIMER")) if os.getenv("SLEEP_TIMER") else 5
    except Exception as err:
        logger.error("Error in sleep timer - {}".format(err))
        sleep_timer = 120
    while True:
        logger.debug("========Started Check the data =======")
        Integration_handler_.service_deployement_handler()
        # Integration_handler_.check_ip_status("10.129.2.24")
        sleep(sleep_timer)
    logger.info("Started main")