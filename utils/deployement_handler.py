import json
import os
from datetime import datetime, timedelta
from http.client import HTTPException

import psycopg2.extras
from sqlalchemy.orm import Session
from loguru import logger
from src.db.alchemy_models import *
import requests
import paramiko


class Deployment_Setup:
    """
    integration_handler
    """

    def __init__(
            self,
            db: Session,
            rdb: Session
    ):
        self.integration_group = None
        self.integration_name = None
        self.last_data_id = 0
        self.limit = 0
        self.response = None
        self.db = db
        self.rdb = rdb
        self.url = None
        self.headers = {'Content-Type': 'application/json',
                        "TAGID-ACCESS-KEY": os.getenv('TAGID_ACCESS_KEY'),
                        "TAGID-SECRET-KEY": os.getenv('TAGID-SECRET-KEY'),
                        }
        self.scanned_data = None
        self.interation_submit_url = None
        self.url_submit_res_data = None
        self.bx_ids = []
        self.integration_data_url = None
        self.integration_Awl_submit_data_url_outward = "https://boxupdate.awlworldwide.com/ethnicity_s3/api/get-picking-sub-flag"
        self.integration_Awl_submit_data_url_inward = "https://track.awlworldwide.com/v1/Rfidboxin.php"
        self.vender_code = os.getenv('VENDER_CODE') if os.getenv('VENDER_CODE') else "su-ven"
        self.wh_code = [os.getenv('WH_CODE') if os.getenv('WH_CODE') else "H01"]
        self.cookies = {
            'PHPSESSID': 'lni1cfjct0m535jck8ucph8sqf',
        }
        self.cur = self.rdb.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        self.ip = "10.129.2.24"
        self.username = "smartiam"
        self.password = "iam@123"
        self.path = ""
        self.orgaanizatioon_name = "Gateway Services"
        self.git_url = ""
        self.git_url_path = ""
        self.deploye_type_name = "service-file"
        self.panel_id = 0

    def get_query_response(self, query):
        try:
            self.cur.execute(f"""

                                                           {query}
                                                        """)
            res_stock_transfer_ids = self.cur.fetchall()
            if len(res_stock_transfer_ids) != 0:
                logger.debug(f"stock_transfer_ids found qty {len(res_stock_transfer_ids)}")
                return {"data": res_stock_transfer_ids, "message": "Data Found", "status_code": 200}
            else:
                logger.debug(f"stock_transfer_ids not found")
                return {"data": [], "message": "Data Not Found", "status_code": 404}
        except Exception as e:
            logger.debug(f"{e}")
            return {"data": [], "message": f"{e}", "status_code": 500}

    def check_ip_status(self, ip):
        try:
            response = os.system("ping -c 1 " + self.ip)
            if response == 0:
                return {"data": [], "message": "Data Found", "status_code": 200}
            else:
                return {"data": [], "message": "Data Found", "status_code": 400}

        except Exception as e:
            logger.debug(f"{e}")
            return {"data": [], "message": "Data Found", "status_code": 500}

    def ssh_to_the_gateway(self, cmd):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, username=self.username, password=self.password)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            lines = stdout.readlines()
            print(lines)
            stdin, stdout, stderr = ssh.exec_command("pwd")
            lines = stdout.readlines()
            ssh.close()
            return {"data": {"ssh_obj": lines}, "message": "Data Found", "status_code": 200}
        except Exception as e:
            logger.debug(f"{e}")
            return {"data": [], "message": "Data Found", "status_code": 500}

    def service_deployement_handler(self):
        try:

            q = f"""
               select gateway_setup_schema.ip,
                       gateway_setup_schema.username,
                       gateway_setup_schema.password,
                       o.o_name,
                       st.git_url,
                       dt.deploye_type_name,
                       gateway_setup_schema.panel_id
                from gateway_setup_schema
                         join service_types st on gateway_setup_schema.ip_id = st.ip_id
                         join organization o on st.o_id = o.o_id
                         join deployement_types dt on gateway_setup_schema.is_deleted = dt.is_deleted
                    and st.deploye_type = dt.deploye_type_id
                    and o.is_deleted = st.is_deleted and gateway_setup_schema.is_deleted = o.is_deleted
                    and gateway_setup_schema.is_active = 1 and gateway_setup_schema.is_deleted = 0
            """

            res = self.get_query_response(q)
            if res.get("status_code") == 200:
                for i in res.get("data"):
                    self.ip = i.get("ip")
                    self.username = i.get("username")
                    self.password = i.get("password")
                    self.orgaanizatioon_name = i.get("o_name")
                    self.git_url_path = i.get("git_url").split(".git")[0].split("/")[-1]
                    self.git_url = i.get("git_url")
                    self.deploye_type_name = i.get("deploye_type_name")
                    self.panel_id = i.get("panel_id")

                    check_ip_res = self.check_ip_status(self.ip)
                    if check_ip_res.get("status_code") != 200:
                        logger.debug(f"<===================================================>")
                        logger.debug(f"Ping ip Failed")
                        continue
                    logger.debug(f"<===================================================>")
                    logger.debug(f"Ping Successfully | IP {self.ip}")
                    get_path = self.ssh_to_the_gateway(f"pwd")
                    if get_path.get("status_code") != 200:
                        logger.debug(f"<===================================================>")
                        logger.debug(f"Organization Create Dir Failed")
                        continue
                    logger.debug(f"<===================================================>")
                    logger.debug(f"Organization Create Dir Success")
                    self.path = get_path.get("data").get("ssh_obj")[0].strip()
                    get_path = self.ssh_to_the_gateway(f"mkdir {self.path}/{self.orgaanizatioon_name}")
                    if get_path.get("status_code") != 200:
                        logger.debug(f"<===================================================>")
                        logger.debug(f"Organization Create Dir Failed")
                        continue
                    logger.debug(f"<===================================================>")
                    logger.debug(f"Organization Create Dir Success")
                    get_path = self.ssh_to_the_gateway(f"cd {self.path}/{self.orgaanizatioon_name}")
                    if get_path.get("status_code") != 200:
                        logger.debug(f"<===================================================>")
                        logger.debug(f"get_path Failed")
                        continue
                    logger.debug(f"<===================================================>")
                    logger.debug(f"get path After CREATE dir  {self.orgaanizatioon_name} Success")
                    get_path = self.ssh_to_the_gateway(
                        f"git clone {i.get('git_url')} {self.path}/{self.orgaanizatioon_name}/{self.git_url_path}")
                    if get_path.get("status_code") != 200:
                        logger.debug(f"<===================================================>")
                        logger.debug(f"GIt Clone Failed")
                        continue
                    logger.debug(f"<===================================================>")
                    logger.debug(f"GIt Clone Success")
                    get_path = self.ssh_to_the_gateway(f"cd {self.path}/{self.git_url_path}")
                    if get_path.get("status_code") != 200:
                        logger.debug(f"<===================================================>")
                        logger.debug(f"get_path Failed")
                        continue
                    get_path = self.ssh_to_the_gateway(f"docker-compose ps | grep -E 'postgres|redis_db|grafana'")
                    if get_path.get("status_code") != 200:
                        get_path = self.ssh_to_the_gateway(
                            f"sudo {self.path}/{self.orgaanizatioon_name}/{self.git_url_path}/docker-compose up -d")
                        if get_path.get("status_code") != 200:
                            logger.debug(f"<===================================================>")
                            logger.debug(f"Docker Compose Failed ")
                            continue
                    get_path = self.ssh_to_the_gateway(f"sudo {self.path}/{self.orgaanizatioon_name}/{self.git_url_path}/docker-compose ps | grep -E 'postgres|redis_db|grafana'")
                    if get_path.get("status_code") != 200:
                        logger.debug(f"<===================================================>")
                        logger.debug(f"Docker Compose Failed Services Not Found")
                        continue
                    logger.debug(f"Docker Compose Success Services Found")
                    if self.deploye_type_name == "docker-container":
                        logger.debug(f"<===================================================>")
                        logger.debug(f"Proccessing through docker-container Deployement Type")
                        pass
                    elif self.deploye_type_name == "service-file":
                        logger.debug(f"<===================================================>")
                        logger.debug(f"Proccessing through service-file Deployement Type")

                        get_path = self.ssh_to_the_gateway(
                            f"sudo {self.path}/{self.orgaanizatioon_name}/{self.git_url_path}/docker-compose up -d")
                        get_path = self.ssh_to_the_gateway(
                            f"cd  {self.path}/{self.orgaanizatioon_name}/{self.git_url_path} && python3 -m venv venv")
                        get_path = self.ssh_to_the_gateway(
                            f"cd  {self.path}/{self.orgaanizatioon_name}/{self.git_url_path} && source venv/bin/activate")
                        get_path = self.ssh_to_the_gateway(
                            f"cd  {self.path}/{self.orgaanizatioon_name}/{self.git_url_path} && pip3 install -r requirements.txt")
                        get_path = self.ssh_to_the_gateway(
                            f"cd  {self.path}/{self.orgaanizatioon_name}/{self.git_url_path} && touch {self.git_url_path}.service")


                        # create_venv = self.ssh_to_the_gateway_use_multiple_cmds(
                        #     [f"cd {self.path}/{self.git_url_path}", "python3 -m venv venv", "source venv/bin/activate",
                        #      "pip3 install -r requirements.txt"])
                        if get_path.get("status_code") != 200:
                            logger.debug(f"<===================================================>")
                            logger.debug(f"Create venv Failed")
                            continue
                        logger.debug(f"<===================================================>")
                        logger.debug(f"Create venv Success")
                        self.create_service_file()
                        logger.debug(f"<===================================================>")
                        logger.debug(f"Source venv Success")
















            else:
                return {"data": [], "message": "Data Not Found", "status_code": 404}

        except Exception as e:
            logger.debug(f"{e}")
            return {"data": [], "message": "Data Found", "status_code": 500}

    def ssh_to_the_gateway_use_multiple_cmds(self, cmd):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, username=self.username, password=self.password)
            lines = []
            for i in cmd:
                stdin, stdout, stderr = ssh.exec_command(i)
                # create .service file

                lines = stdout.readlines()
                print(lines)
            ssh.close()
            return {"data": {"ssh_obj": lines}, "message": "Data Found", "status_code": 200 if len(lines) != 0 else 400}
        except Exception as e:
            logger.debug(f"{e}")
            return {"data": [], "message": "Data Found", "status_code": 500}

    def create_service_file(self):
        try:
            #  dir is exist

            #  dir is exist
            # create .service file and # Reference
            # # https://github.com/torfsen/python-systemd-tutorial
            #
            # [Unit]
            # Description=Trial Theft Identity
            # After=docker.service docker.socket
            # [Service]
            # # Command to execute when the service is started
            # User=pi
            # Group=pi
            # WorkingDirectory=/home/pi/tagid-trial-theft-identity/tagid-trial-theft-identity
            # ExecStart=/usr/bin/python3  /home/pi/tagid-trial-theft-identity/tagid-trial-theft-identity/main.py
            # Environment="base_url=https://apiv3.tagid.smart-iam.com/kohinoor-prod/admin-api/trial_room_txn"
            # Environment="config_db_path= /app/config"
            # Environment="DECODING_LOGIC=1"
            # Environment="POSTGRES_DB=trial-room"
            # Environment="POSTGRES_PASSWORD=Smartiam1s3v3r1"
            # Environment="POSTGRES_PORT=5432"
            # Environment="POSTGRES_SERVER=127.0.0.1"
            # Environment="POSTGRES_USER=postgres"
            # Environment="PROM_METRICS_PORT=8201"
            # Environment="PYTHONUNBUFFERED=1"
            # Environment="TZ=Asia/Kolkata"
            # Environment="YOUR_EPC_UPDATE_TIMER=10"
            # Environment="reader_id=1"
            # Environment="reader_name=theft-detection-reader"
            # Environment="store_id=1"
            # Environment="panel_id=1"
            # Environment="YOUR_CLOUD_PUSH_TIMER=600"
            # Environment="YOUR_EPC_UPDATE_TIMER=600"
            #
            #
            # [Install]
            # WantedBy=default.target

            q = f"""
            
                select rv.variable_name, rv.value,rv.ip_id
                from  requirement_variables rv join gateway_setup_schema gsc on rv.ip_id = gsc.ip_id and
                gsc.is_deleted = rv.is_deleted
                where gsc.is_deleted = 0 and gsc.ip = '{self.ip}'
            """
            get_data = self.get_query_response(q)
            if get_data.get("status_code") != 200:
                logger.debug(f"<===================================================>")
                logger.debug(f"Data Not Found fopr Requirement Variables")
                return {"data": [], "message": "Data Not Found", "status_code": 404}
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, username=self.username, password=self.password)

            lines = []
            # for i, command in enumerate(cmd):

            # stdin, stdout, stderr = ssh.exec_command("ls")
            # output = stdout.readlines()
            # lines.append(output)

            # Create a .service file for each command
            with open(f"{self.git_url_path}.service", "w") as f:
                f.write(f"[Unit]\n")
                f.write(f"Description={self.git_url_path}\n")
                f.write(f"After=docker.service docker.socket\n")
                f.write(f"[Service]\n")
                f.write(f"# Command to execute when the service is started\n")
                f.write(f"User=pi\n")
                f.write(f"Group=pi\n")
                f.write(f"WorkingDirectory={self.path}/{self.orgaanizatioon_name}/{self.git_url_path}\n")
                f.write(f"ExecStart={self.path}/{self.orgaanizatioon_name}/{self.git_url_path}/venv/bin/python3  {self.path}/{self.orgaanizatioon_name}/{self.git_url_path}/main.py\n")
                f.write(
                    f"Environment=\"base_url=https://apiv3.tagid.smart-iam.com/kohinoor-prod/admin-api/trial_room_txn\"\n")
                f.write(f"Environment=\"config_db_path= /app/config\"\n")
                f.write(f"Environment=\"DECODING_LOGIC=1\"\n")
                f.write(f"Environment=\"POSTGRES_DB=trial-room\"\n")
                f.write(f"Environment=\"POSTGRES_PASSWORD=Smartiam1s3v3r1\"\n")
                f.write(f"Environment=\"POSTGRES_PORT=5432\"\n")
                f.write(f"Environment=\"POSTGRES_SERVER=\"{self.ip}\"\n")

                f.write(f"Environment=\"POSTGRES_USER=1\"\n")
                f.write(f"Environment=\"PROM_METRICS_PORT=trial-room\"\n")
                f.write(f"Environment=\"PYTHONUNBUFFERED=Smartiam1s3v3r1\"\n")
                f.write(f"Environment=\"POSTGRES_PORT=5432\"\n")
                f.write(f"Environment=\"TZ=\"{self.ip}\"\n")

                f.write(f"Environment=\"YOUR_EPC_UPDATE_TIMER=1\"\n")
                f.write(f"Environment=\"reader_id=trial-room\"\n")
                f.write(f"Environment=\"reader_name=Smartiam1s3v3r1\"\n")
                f.write(f"Environment=\"store_id=5432\"\n")
                f.write(f"Environment=\"panel_id={self.panel_id}\n")

                f.write(f"Environment=\"YOUR_CLOUD_PUSH_TIMER=600\"\n")
                f.write(f"Environment=\"YOUR_EPC_UPDATE_TIMER=600\"\n")

            stdin, stdout, stderr = ssh.exec_command(f"sudo cp smartiam@10.129.2.209:/home/smartiam/Desktop/Amol/my_diagrams/Deployement_setup/{self.git_url_path}.service  pi@10.129.2.239:{self.path}/{self.orgaanizatioon_name}/{self.git_url_path}/")
            output = stdout.readlines()
            lines.append(output)
            stdin, stdout, stderr = ssh.exec_command(f"sudo systemctl restart {self.git_url_path}.service ")
            output = stdout.readlines()
            lines.append(output)

            ssh.close()
            return {"data": [], "message": "Data Found", "status_code": 200}
        except Exception as e:
            logger.debug(f"{e}")
            return {"data": [], "message": "Data Found", "status_code": 500}
