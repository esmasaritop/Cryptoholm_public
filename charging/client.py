import ast
import os
import sys
import time
import yaml
import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional, Callable, Awaitable, Dict, Any
import base64

import aioconsole
import websockets
from ocpp.routing import on, after
from ocpp.v201 import ChargePoint as Cp201, call as call201, call_result as call_result201
from ocpp.v20 import ChargePoint as Cp20, call as call20, call_result as call_result20
from ocpp.v16 import ChargePoint as Cp16, call as call16, call_result as call_result16
from ocpp.v201 import enums as enums201, datatypes as data201
from ocpp.v16 import enums as enums16, datatypes as data16

from websockets import Headers, Subprotocol

import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
from cryptography.x509.oid import NameOID

import argparse
from dns.resolver import resolve, NoAnswer
from dns import rdatatype

logging.basicConfig(level=logging.ERROR)

# ---- Global config (dosyadan yüklenecek) ----
SECURITY_PROFILE = 1
VERSION = 'v2.0.1'
IP = ''
PORT0 = 9000
PORT1 = 9001
PORT2 = 9002
PORT3 = 9003
PORT4 = 9004
PORT5 = 9005
PORT6 = 9006
PORT7 = 9007
AUTH_KEY = ''
VENDOR_NAME = ''
MODEL = ''
SERIAL_NUMBER = ''
URL = None

# Argparse
parser = argparse.ArgumentParser(description="OCPP client")
parser.add_argument('-config_file', type=str, required=False)
parser.add_argument('-server', type=str, required=False)
parser.add_argument('-ports', type=int, required=False, nargs='+')
parser.add_argument('-version', type=str, required=False)
parser.add_argument('-sec_profile', type=int, required=False)
parser.add_argument('-auth_key', type=str, required=False)
parser.add_argument('-vendor_name', type=str, required=False)
parser.add_argument('-model', type=str, required=False)
parser.add_argument('-serial_number', type=str, required=False)
parser.add_argument('-url', type=str, required=False)
args = parser.parse_args()

CONFIG_FILE = args.config_file if args.config_file else 'charging/client_config.yaml'

CERTIFICATE_PATH = None
CERTIFICATE_KEY_PATH = None

SECURITY_CTRL = None
COMM_CTRL = None
CONNECTION_PROFILES = None
CONFIGURATION = None
RECONNECT_TIMES = 0

def _get_current_time() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def modify_config(variable: str, value, component: str = None, index: int = None):
    with open(CONFIG_FILE, 'r') as file:
        config = yaml.safe_load(file)

    if component is not None:
        if component == 'OCPPCommCtrlr':
            config['comm'][variable] = value
        elif component == 'SecurityCtrlr':
            config['security'][variable] = value
    elif index is not None:
        config['profiles'][index]['SP'] = value
    else:
        config[variable] = value

    with open(CONFIG_FILE, 'w') as file:
        yaml.safe_dump(config, file, default_flow_style=False)

def get_server_ipv6_address(url):
    try:
        answer = resolve(url, 'AAAA')
        for rdata in answer.response.answer:
            for record in rdata:
                if record.rdtype == rdatatype.TXT:
                    txt_data = record.strings[0].decode('utf-8')
                    server_data = eval(txt_data)  # (Emülatör içi basit kullanım)
                    return server_data
    except NoAnswer:
        print(f"No records found for {url}")
    except Exception as e:
        print(e)

def load_config() -> bool:
    global VERSION, VENDOR_NAME, MODEL, SERIAL_NUMBER
    global CERTIFICATE_PATH, CERTIFICATE_KEY_PATH
    global URL, IP
    global PORT0, PORT1, PORT2, PORT3, PORT4, PORT5, PORT6, PORT7
    global SECURITY_CTRL, COMM_CTRL, CONNECTION_PROFILES, CONFIGURATION
    global RECONNECT_TIMES

    with open(CONFIG_FILE, "r") as file:
        try:
            content = yaml.safe_load(file)

            if "version" in content:
                VERSION = content["version"]

            if "ip" in content:
                IP = content["ip"]

            if "port0" in content: PORT0 = content["port0"]
            if "port1" in content: PORT1 = content["port1"]
            if "port2" in content: PORT2 = content["port2"]
            if "port3" in content: PORT3 = content["port3"]
            if "port4" in content: PORT4 = content["port4"]
            if "port5" in content: PORT5 = content["port5"]
            if "port6" in content: PORT6 = content["port6"]
            if "port7" in content: PORT7 = content["port7"]

            if 'comm' in content and content['comm'] is not None:
                RECONNECT_TIMES = content['comm']['NetworkProfileConnectionAttempts']

            if 'attempts' in content and content['attempts'] is not None:
                RECONNECT_TIMES = content['attempts']

            if "security" in content:
                if "SecurityProfile" in content["security"]:
                    # sadece v1.6 için kullanılıyor
                    pass
                if 'Identity' in content["security"]:
                    SERIAL_NUMBER = content['security']['Identity']

            try:
                with open(f'./charging/installedCertificates/{SERIAL_NUMBER}/private_key.pem', 'rb') as f:
                    serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
                with open(f'./charging/installedCertificates/{SERIAL_NUMBER}/certificate_{SERIAL_NUMBER}.pem', 'rb') as f:
                    x509.load_pem_x509_certificate(f.read(), default_backend())

                CERTIFICATE_KEY_PATH = f'./charging/installedCertificates/{SERIAL_NUMBER}/private_key.pem'
                CERTIFICATE_PATH = f'./charging/installedCertificates/{SERIAL_NUMBER}/certificate_{SERIAL_NUMBER}.pem'
            except Exception:
                CERTIFICATE_PATH = None
                CERTIFICATE_KEY_PATH = None

            if "vendor_name" in content:
                VENDOR_NAME = content['vendor_name']
            if "model" in content:
                MODEL = content['model']
            if "url" in content:
                URL = content['url']

            # DNS kullanımı (opsiyonel)
            if (args.server is None or args.ports is None) and URL is not None:
                print('Connecting with DNS server to obtain server address...')
                try:
                    server_data = get_server_ipv6_address(URL)
                    if args.server is None:
                        IP = server_data['ip_address']
                        if 'profiles' in content:
                            for profile in content['profiles']:
                                content['profiles'][profile]['ip'] = server_data['ip_address']
                    if args.ports is None:
                        PORT0 = server_data['port0']; PORT1 = server_data['port1']
                        PORT2 = server_data['port2']; PORT3 = server_data['port3']
                        PORT4 = server_data['port4']; PORT5 = server_data['port5']
                        PORT6 = server_data['port6']; PORT7 = server_data['port7']
                except:
                    print("Couldn't obtain data from the DNS server")

            if VERSION in ('v2.0.1', 'v2.0'):
                # Security/Comm kontrol
                if 'security' in content:
                    SECURITY_CTRL = {
                        enums201.SecurityCtrlrVariableName.additional_root_certificate_check.value: content["security"]['AdditionalRootCertificateCheck'],
                        enums201.SecurityCtrlrVariableName.basic_auth_password.value: content["security"]['BasicAuthPassword'],
                        enums201.SecurityCtrlrVariableName.certificate_entries.value: 0,
                        enums201.SecurityCtrlrVariableName.cert_signing_repeat_times.value: content["security"]['CertSigningRepeatTimes'],
                        enums201.SecurityCtrlrVariableName.cert_signing_wait_minimum.value: content["security"]['CertSigningWaitMinimum'],
                        enums201.SecurityCtrlrVariableName.identity.value: content["security"]['Identity'],
                        enums201.SecurityCtrlrVariableName.max_certificate_chain_size.value: 6000,
                        enums201.SecurityCtrlrVariableName.organization_name.value: content["security"]['OrganizationName'],
                        enums201.SecurityCtrlrVariableName.security_profile.value: content["security"]["SecurityProfile"]
                    }

                if 'comm' in content:
                    COMM_CTRL = {
                        enums201.OCPPCommCtrlrVariableName.active_network_profile.value: 0,
                        enums201.OCPPCommCtrlrVariableName.message_timeout.value: content["comm"]['MessageTimeout'],
                        enums201.OCPPCommCtrlrVariableName.file_transfer_protocols.value: ['FTP', 'FTPS', 'HTTP', 'HTTPS', 'SFTP'],
                        enums201.OCPPCommCtrlrVariableName.heartbeat_interval.value: content["comm"]['HeartbeatInterval'],
                        enums201.OCPPCommCtrlrVariableName.network_configuration_priority.value: content["comm"]['NetworkConfigurationPriority'],
                        enums201.OCPPCommCtrlrVariableName.network_profile_connection_attempts.value: content["comm"]['NetworkProfileConnectionAttempts'],
                        enums201.OCPPCommCtrlrVariableName.offline_threshold.value: content["comm"]['OfflineThreshold']
                    }

                # PROFİL LİSTESİ — sade ve sağlam
                if 'profiles' in content:
                    CONNECTION_PROFILES = []
                    for element in content['profiles']:
                        sp = content['profiles'][element]['SP']
                        vers = content['profiles'][element]['ocpp_version']  # 'OCPP201', 'OCPP20' veya 'OCPP16'

                        # Port seçimi
                        port = (
                            PORT0 if (sp == 0 and vers == 'OCPP16') else
                            PORT1 if (sp == 1 and vers == 'OCPP16') else
                            PORT2 if (sp == 2 and vers == 'OCPP16') else
                            PORT3 if (sp == 3 and vers == 'OCPP16') else
                            PORT4 if (sp == 0 and vers != 'OCPP16') else
                            PORT5 if (sp == 1 and vers != 'OCPP16') else
                            PORT6 if (sp == 2 and vers != 'OCPP16') else
                            PORT7
                        )

                        # Basit: her zaman loopback
                        host = "127.0.0.1"
                        scheme = "ws" if sp in (0, 1) else "wss"
                        ocpp_csms_url = f"{scheme}://{host}:{port}/"

                        CONNECTION_PROFILES.append(
                            data201.NetworkConnectionProfileType(
                                ocpp_version=vers,  # 'OCPP201' veya 'OCPP20' bekler
                                ocpp_transport=enums201.OCPPTransportType.json,
                                ocpp_csms_url=ocpp_csms_url,
                                message_timeout=content['profiles'][element]['message_timeout'],
                                security_profile=sp,
                                ocpp_interface=enums201.OCPPInterfaceType.wireless0
                            )
                        )
            else:
                # OCPP 1.6 için
                CONFIGURATION = {
                    enums16.ConfigurationKey.additional_root_certificate_check.value: content["security"]['AdditionalRootCertificateCheck'],
                    enums16.ConfigurationKey.authorization_key.value: content["security"]['BasicAuthPassword'],
                    enums16.ConfigurationKey.cert_signing_repeat_times.value: content["security"]['CertSigningRepeatTimes'],
                    enums16.ConfigurationKey.cert_signing_wait_minimum.value: content["security"]['CertSigningWaitMinimum'],
                    enums16.ConfigurationKey.cpo_name.value: content["security"]['OrganizationName'],
                    enums16.ConfigurationKey.security_profile.value: content["security"]["SecurityProfile"],
                    enums16.ConfigurationKey.heartbeat_interval.value: content['HeartbeatInterval']
                }

        except yaml.YAMLError:
            print('Failed to parse client_config.yaml')
            return False

        return True

def load_certificate():
    global CERTIFICATE_PATH, CERTIFICATE_KEY_PATH
    try:
        with open(CERTIFICATE_PATH, "rb") as f:
            cert_data = f.read()
            x509.load_pem_x509_certificate(cert_data, default_backend())

        with open(CERTIFICATE_KEY_PATH, "rb") as f:
            serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
    except Exception as e:
        print("Reading certicate/key failed:", e)
        CERTIFICATE_PATH = None
        CERTIFICATE_KEY_PATH = None

def configuration():
    with open(CONFIG_FILE, 'r') as file:
        config = yaml.safe_load(file)

    if args.server is not None:
        config['ip'] = args.server
        if 'profiles' in config and config['profiles'] is not None:
            for profile in config['profiles']:
                config['profiles'][profile]['ip'] = args.server
    if args.ports:
        for i, port in enumerate(args.ports):
            config[f'port{i}'] = port
    if args.version is not None:
        config['version'] = args.version
    if args.sec_profile is not None:
        config['security']['SecurityProfile'] = args.sec_profile
    if args.auth_key is not None:
        config['security']['BasicAuthPassword'] = args.auth_key
    if args.vendor_name is not None:
        config['vendor_name'] = args.vendor_name
    if args.model is not None:
        config['model'] = args.model
    if args.serial_number is not None:
        config['security']['Identity'] = args.serial_number
    if args.url is not None:
        config['url'] = args.url

    with open(CONFIG_FILE, 'w') as file:
        yaml.safe_dump(config, file, default_flow_style=False)

def main():
    configuration()
    if not load_config():
        quit(1)

    if VERSION == 'v1.6':
        tries = RECONNECT_TIMES
        while True:
            config = {'vendor_name': VENDOR_NAME, 'model': MODEL, 'serial_number': SERIAL_NUMBER}
            try:
                asyncio.run(launch_client(**config))
            except (ConnectionError, TimeoutError, PermissionError) as e:
                print(f"Failed to connect with security profile {CONFIGURATION['SecurityProfile']}: {e}")
                if tries > 0:
                    tries -= 1
                    print('Reconnecting in 5 seconds...')
                    time.sleep(5)
                    continue
                else:
                    break
            except Exception as e:
                print(f"An unexpected error occurred with security profile {CONFIGURATION['SecurityProfile']}: {e}")
                if tries > 0:
                    tries -= 1
                    print('Reconnecting in 5 seconds...')
                    time.sleep(5)
                    continue
                else:
                    break
    else:
        tries = COMM_CTRL[enums201.OCPPCommCtrlrVariableName.network_profile_connection_attempts.value]
        for profile in COMM_CTRL[enums201.OCPPCommCtrlrVariableName.network_configuration_priority.value]:
            while True:
                config = {'vendor_name': VENDOR_NAME, 'model': MODEL, 'index': profile}
                try:
                    asyncio.run(launch_client(**config))
                except (ConnectionError, TimeoutError, PermissionError) as e:
                    print(f"Failed to connect with security profile {CONNECTION_PROFILES[profile].security_profile}: {e}")
                    if tries > 0:
                        tries -= 1
                        print('Reconnecting in 5 seconds...')
                        time.sleep(5)
                        continue
                    else:
                        tries = COMM_CTRL[enums201.OCPPCommCtrlrVariableName.network_profile_connection_attempts.value]
                        break
                except Exception as e:
                    print(f"An unexpected error occurred with security profile {CONNECTION_PROFILES[profile].security_profile}: {e}")
                    if tries > 0:
                        tries -= 1
                        print('Reconnecting in 5 seconds...')
                        time.sleep(5)
                        continue
                    else:
                        tries = COMM_CTRL[enums201.OCPPCommCtrlrVariableName.network_profile_connection_attempts.value]
                        break

# ---- Client Base ----
class ChargePointClientBase:
    reboot = False
    csCert = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def print_message(self, message: str):
        print(f'[{self.id}] {message}')

    def generate_key_pair(self):
        private_key = ec.generate_private_key(ec.SECP256R1())
        os.makedirs(f"./charging/installedCertificates/{SERIAL_NUMBER}", exist_ok=True)
        with open(f"./charging/installedCertificates/{SERIAL_NUMBER}/private_key.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        print("Key pair generated and saved as 'private_key.pem'")

    async def send_heartbeat(self, interval: int = 10):
        if VERSION == 'OCPP201':
            request = call201.HeartbeatPayload()
        elif VERSION == 'OCPP20':
            request = call20.HeartbeatPayload()
        elif VERSION == 'OCPP16':
            request = call16.HeartbeatPayload()
        while True:
            await self.call(request)
            await asyncio.sleep(interval)

    async def send_authorize(self, token: dict[str, str]):
        if VERSION == 'OCPP201':
            return await self.call(call201.AuthorizePayload(id_token=token))
        elif VERSION == 'OCPP20':
            return await self.call(call20.AuthorizePayload(id_token=token))
        elif VERSION == 'OCPP16':
            return await self.call(call16.AuthorizePayload(id_tag=token))

    async def send_status_notification(self, connector_status: str, evse_id: int = 0, connector_id: int = 0):
        content = {
            "timestamp": _get_current_time(),
            "connector_status": connector_status,
            "evse_id": evse_id,
            "connector_id": connector_id
        }
        if VERSION == 'OCPP201':
            return await self.call(call201.StatusNotificationPayload(**content))
        elif VERSION == 'OCPP20':
            return await self.call(call20.StatusNotificationPayload(**content))
        elif VERSION == 'OCPP16':
            return await self.call(call16.StatusNotificationPayload(**content))

    async def send_transaction_event_authorized(self, event_type: str, transaction_id: str, seq_no: int, id_token: dict[str, str]):
        if VERSION == 'OCPP201':
            return await self.call(call201.TransactionEventPayload(
                timestamp=_get_current_time(),
                event_type=event_type,
                seq_no=seq_no,
                transaction_info={'transactionId': transaction_id},
                trigger_reason='Authorized',
                id_token=id_token
            ))
        elif VERSION == 'OCPP20':
            return await self.call(call20.TransactionEventPayload(
                timestamp=_get_current_time(),
                event_type=event_type,
                seq_no=seq_no,
                transaction_data={'transactionId': transaction_id, 'reason': 'Authorized'},
                id_token=id_token
            ))

    async def send_transaction_event_cable_plugged_in(self, event_type: str, transaction_id: str, seq_no: int):
        if VERSION == 'OCPP201':
            return await self.call(call201.TransactionEventPayload(
                timestamp=_get_current_time(),
                event_type=event_type,
                seq_no=seq_no,
                transaction_info={'transactionId': transaction_id},
                trigger_reason='CablePluggedIn'
            ))
        elif VERSION == 'OCPP20':
            return await self.call(call20.TransactionEventPayload(
                timestamp=_get_current_time(),
                event_type=event_type,
                seq_no=seq_no,
                transaction_data={'transactionId': transaction_id, 'reason': 'CablePluggedIn'}
            ))

    async def send_transaction_event_charging_state_changed(self, event_type: str, transaction_id: str, seq_no: int, charging_state: str):
        if VERSION == 'OCPP201':
            return await self.call(call201.TransactionEventPayload(
                timestamp=_get_current_time(),
                event_type=event_type,
                seq_no=seq_no,
                transaction_info={'transactionId': transaction_id, 'chargingState': charging_state},
                trigger_reason='ChargingStateChanged',
            ))
        elif VERSION == 'OCPP20':
            return await self.call(call20.TransactionEventPayload(
                timestamp=_get_current_time(),
                event_type=event_type,
                seq_no=seq_no,
                transaction_data={'transactionId': transaction_id, 'chargingState': charging_state, 'reason': 'ChargingStateChanged'}
            ))

    async def check_reboot(self):
        while True:
            if self.reboot:
                print('Rebooting...')
                await asyncio.sleep(1)
                python = sys.executable
                os.execv(python, [python] + sys.argv)
            elif self.csCert:
                print('Installing CS certificate...')
                await self.send_sign_certificate()
                self.csCert = False
            await asyncio.sleep(1)

    async def send_boot_notification(
        self,
        serial_number: str,
        model: str,
        vendor_name: str,
        SECURITY_PROFILE: int,
        index: int = None,
        async_runnable: Optional[Callable[['ChargePointClientBase'], Awaitable[None]]] = None
    ):
        global VERSION
        if index is not None:
            VERSION = CONNECTION_PROFILES[index].ocpp_version
            COMM_CTRL['ActiveNetworkProfile'] = index
        else:
            VERSION = 'OCPP16'
        try:
            if VERSION == 'OCPP201':
                request = call201.BootNotificationPayload(
                    charging_station={"model": model, "vendor_name": vendor_name, "serial_number": serial_number},
                    reason="PowerUp"
                )
            elif VERSION == 'OCPP20':
                request = call20.BootNotificationPayload(
                    charging_station={"model": model, "vendor_name": vendor_name, "serial_number": serial_number},
                    reason="PowerUp"
                )
            elif VERSION == 'OCPP16':
                request = call16.BootNotificationPayload(
                    charge_point_model=model,
                    charge_point_vendor=vendor_name,
                    charge_point_serial_number=serial_number
                )

            response = await self.call(request)

            if response.status != "Accepted":
                logging.error("Boot failed")
                raise PermissionError("Boot failed: Response status not accepted")

            if VERSION != 'OCPP16':
                SECURITY_CTRL['SecurityProfile'] = CONNECTION_PROFILES[index].security_profile
                COMM_CTRL['ActiveNetworkProfile'] = index
                COMM_CTRL['HeartbeatInterval'] = response.interval
            else:
                CONFIGURATION['SecurityProfile'] = SECURITY_PROFILE

            print(f"Connected successfully with security profile {CONFIGURATION['SecurityProfile'] if VERSION == 'OCPP16' else CONNECTION_PROFILES[index].security_profile}.")

            heartbeat_task = asyncio.create_task(self.send_heartbeat(response.interval))

            if async_runnable is not None:
                await async_runnable(self)
            else:
                self.print_message("Connected to server")

            await heartbeat_task
        except PermissionError:
            raise
        except Exception as e:
            print(e)
            self.print_message("Disconnected from the server")

    async def send_sign_certificate(self):
        print('Getting CS certificate...')
        self.generate_key_pair()
        try:
            with open(f"./charging/installedCertificates/{SERIAL_NUMBER}/private_key.pem", "rb") as key_file:
                private_key = serialization.load_pem_private_key(key_file.read(), password=None, backend=default_backend())
        except Exception as e:
            print(f'There is a problem with CS public/private key: {e}')
            return

        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"AN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Anonymous"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"Anonymous"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'EmuOCPP'),
            x509.NameAttribute(NameOID.COMMON_NAME, SERIAL_NUMBER),
        ])

        csr = x509.CertificateSigningRequestBuilder().subject_name(subject).sign(private_key, hashes.SHA256())
        csr_pem = csr.public_bytes(serialization.Encoding.PEM)

        if VERSION == 'OCPP201':
            request = call201.SignCertificatePayload(csr=csr_pem.decode())
        elif VERSION == 'OCPP20':
            request = call20.SignCertificatePayload(csr=csr_pem.decode())
        elif VERSION == 'OCPP16':
            request = call16.SignCertificatePayload(csr=csr_pem.decode())

        response = await self.call(request)
        print(response)

    @on('CertificateSigned')
    async def on_certificate_signed(self, certificate_chain: str = None, cert: list = None):
        global CERTIFICATE_KEY_PATH, CERTIFICATE_PATH
        if cert is not None:
            certificate_chain = cert[0]

        os.makedirs(f"./charging/installedCertificates/{SERIAL_NUMBER}", exist_ok=True)
        with open(f"./charging/installedCertificates/{SERIAL_NUMBER}/certificate_{SERIAL_NUMBER}.pem", "w") as cert_file:
            cert_file.write(certificate_chain)
        CERTIFICATE_KEY_PATH = f'./charging/installedCertificates/{SERIAL_NUMBER}/private_key.pem'
        CERTIFICATE_PATH = f'./charging/installedCertificates/{SERIAL_NUMBER}/certificate_{SERIAL_NUMBER}.pem'
        if VERSION == 'OCPP201':
            return call_result201.CertificateSignedPayload(status='Accepted')
        elif VERSION == 'OCPP20':
            return call_result20.CertificateSignedPayload(status='Accepted')
        elif VERSION == 'OCPP16':
            return call_result16.CertificateSignedPayload(status='Accepted')

    @on("InstallCertificate")
    async def on_install_certificate(self, certificate_type: str, certificate: str):
        status = 'Accepted'
        if (VERSION != 'OCPP16' and certificate_type == 'CSMSRootCertificate') or (VERSION == 'OCPP16' and certificate_type == 'CentralSystemRootCertificate'):
            try:
                cert = x509.load_pem_x509_certificate(certificate.encode(), default_backend())
                cert.public_key()
                cert.subject
                cert.issuer
                if cert.not_valid_after_utc < datetime.now(timezone.utc):
                    raise ValueError("Certificate has expired.")
                flag = CONFIGURATION['AdditionalRootCertificateCheck'] if VERSION == 'OCPP16' else SECURITY_CTRL['AdditionalRootCertificateCheck']
                if not flag:
                    root_dir = f'./charging/installedCertificates/{SERIAL_NUMBER}/root'
                    os.makedirs(root_dir, exist_ok=True)
                    entries = os.listdir(root_dir)
                    files = [file for file in entries if os.path.isfile(os.path.join(root_dir, file))]
                    with open(os.path.join(root_dir, f'rootCert_{len(files)+1}.pem'), 'w') as cert_file:
                        cert_file.write(certificate)
                else:
                    print('AdditionalRootCertificateCheck=True functionality not implemented')
                    raise Exception
            except (ValueError, InvalidSignature, UnsupportedAlgorithm, Exception) as e:
                print(f"Certificate validation failed: {e}")
                status = 'Rejected'
        else:
            print('Other certificate types not implemented')
            status = 'Rejected'

        if VERSION == 'OCPP201':
            return call_result201.InstallCertificatePayload(status=status)
        elif VERSION == 'OCPP20':
            return call_result20.InstallCertificatePayload(status=status)
        elif VERSION == 'OCPP16':
            return call_result16.InstallCertificatePayload(status=status)

    @on('GetVariables')
    def on_get_variables(self, get_variable_data: data201.GetVariableDataType):
        print(f'Got data retreival petition of {get_variable_data}')
        res = []
        for varData in get_variable_data:
            comp = varData['component']['name']
            var = varData['variable']['name']
            if COMM_CTRL is not None and comp == 'OCPPCommCtrlr':
                if var in COMM_CTRL.keys():
                    res.append(data201.GetVariableResultType(attribute_status='Accepted', component=varData['component'], variable=varData['variable'], attribute_value=str(COMM_CTRL[var])))
                else:
                    res.append(data201.GetVariableResultType(attribute_status='UnknownVariable', component=varData['component'], variable=varData['variable']))
            elif SECURITY_CTRL is not None and comp == 'SecurityCtrlr':
                if var in SECURITY_CTRL.keys():
                    res.append(data201.GetVariableResultType(attribute_status='Accepted', component=varData['component'], variable=varData['variable'], attribute_value=str(SECURITY_CTRL[var])))
                else:
                    res.append(data201.GetVariableResultType(attribute_status='UnknownVariable', component=varData['component'], variable=varData['variable']))
            else:
                res.append(data201.GetVariableResultType(attribute_status='UnknownComponent', component=varData['component'], variable=varData['variable']))

        if VERSION == 'OCPP201':
            return call_result201.GetVariablesPayload(get_variable_result=res)
        elif VERSION == 'OCPP20':
            return call_result20.GetVariablesPayload(get_variable_result=res)

    @on('GetConfiguration')
    def on_get_configuration(self, key: List = None):
        if VERSION == 'OCPP16':
            res = []
            for var in key:
                if var in CONFIGURATION.keys():
                    res.append(data16.KeyValue(key=var, readonly=True, value=str(CONFIGURATION[var])))
            return call_result16.GetConfigurationPayload(configuration_key=res)

    @on('SetNetworkProfile')
    def on_set_profile(self, configuration_slot: str, connection_data: data201.NetworkConnectionProfileType):
        CONNECTION_PROFILES[configuration_slot] = connection_data
        CONNECTION_PROFILES[configuration_slot]['ocpp_version'] = VERSION if CONNECTION_PROFILES[configuration_slot]['ocpp_version'] == 'OCPP20' else 'OCPP16'
        modify_config(variable='profiles', index=configuration_slot, value=connection_data['security_profile'])
        if VERSION == 'OCPP201':
            return call_result201.SetNetworkProfilePayload(status='Accepted')
        elif VERSION == 'OCPP20':
            return call_result20.SetNetworkProfilePayload(status='Accepted')

    @on('SetVariables')
    async def on_set_variables(self, set_variable_data: data201.SetVariableDataType):
        final = []
        for change in set_variable_data:
            try:
                original_value = ast.literal_eval(change['attribute_value'])
            except (ValueError, SyntaxError):
                original_value = change['attribute_value']
            if change['component']['name'] == 'OCPPCommCtrlr':
                if change['variable']['name'] in COMM_CTRL.keys():
                    if change['variable']['name'] == 'NetworkConfigurationPriority':
                        if CONNECTION_PROFILES[original_value[0]].security_profile < CONNECTION_PROFILES[COMM_CTRL['ActiveNetworkProfile']].security_profile:
                            final.append(data201.SetVariableResultType(attribute_status='Rejected', component=change['component'], variable=change['variable']))
                        else:
                            if CONNECTION_PROFILES[original_value[0]].security_profile == 2:
                                entries = os.listdir(f'./charging/installedCertificates/{SERIAL_NUMBER}/root')
                                files = [file for file in entries if os.path.isfile(os.path.join(f'./charging/installedCertificates/{SERIAL_NUMBER}/root', file))]
                                if len(files) < 1:
                                    final.append(data201.SetVariableResultType(attribute_status='Rejected', component=change['component'], variable=change['variable']))
                                else:
                                    COMM_CTRL[change['variable']['name']] = original_value
                                    modify_config(variable=change['variable']['name'], component=change['component']['name'], value=original_value)
                                    final.append(data201.SetVariableResultType(attribute_status='RebootRequired', component=change['component'], variable=change['variable']))
                            elif CONNECTION_PROFILES[original_value[0]].security_profile == 3:
                                try:
                                    load_certificate()
                                except:
                                    pass
                                if not (CERTIFICATE_KEY_PATH is None or CERTIFICATE_PATH is None):
                                    COMM_CTRL[change['variable']['name']] = original_value
                                    modify_config(variable=change['variable']['name'], component=change['component']['name'], value=original_value)
                                    final.append(data201.SetVariableResultType(attribute_status='RebootRequired', component=change['component'], variable=change['variable']))
                                else:
                                    final.append(data201.SetVariableResultType(attribute_status='Rejected', component=change['component'], variable=change['variable']))
                            else:
                                COMM_CTRL[change['variable']['name']] = original_value
                                modify_config(variable=change['variable']['name'], component=change['component']['name'], value=original_value)
                                final.append(data201.SetVariableResultType(attribute_status='RebootRequired', component=change['component'], variable=change['variable']))
                    else:
                        COMM_CTRL[change['variable']['name']] = original_value
                        modify_config(variable=change['variable']['name'], component=change['component']['name'], value=original_value)
                        final.append(data201.SetVariableResultType(attribute_status='Accepted', component=change['component'], variable=change['variable']))
                else:
                    final.append(data201.SetVariableResultType(attribute_status='UnknownVariable', component=change['component'], variable=change['variable']))
            elif change['component']['name'] == 'SecurityCtrlr':
                if change['variable']['name'] in SECURITY_CTRL.keys():
                    SECURITY_CTRL[change['variable']['name']] = original_value
                    modify_config(variable=change['variable']['name'], component=change['component']['name'], value=original_value)
                    final.append(data201.SetVariableResultType(attribute_status='Accepted', component=change['component'], variable=change['variable']))
                else:
                    final.append(data201.SetVariableResultType(attribute_status='UnknownVariable', component=change['component'], variable=change['variable']))
            else:
                final.append(data201.SetVariableResultType(attribute_status='UnknownComponent', component=change['component'], variable=change['variable']))

        if VERSION == 'OCPP201':
            return call_result201.SetVariablesPayload(set_variable_result=final)
        elif VERSION == 'OCPP20':
            return call_result20.SetVariablesPayload(set_variable_result=final)

    @on('ChangeConfiguration')
    def on_change_configuration(self, key: str, value: str):
        print(f'Trying to set {value} in {key}...')
        try:
            original_value = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            original_value = value
        if key == 'SecurityProfile':
            if original_value == 2:
                entries = os.listdir(f'./charging/installedCertificates/{SERIAL_NUMBER}/root')
                files = [file for file in entries if os.path.isfile(os.path.join(f'./charging/installedCertificates/{SERIAL_NUMBER}/root', file))]
            if original_value < CONFIGURATION['SecurityProfile'] or (original_value == 3 and (CERTIFICATE_KEY_PATH is None or CERTIFICATE_PATH is None)) or (original_value == 2 and len(files) < 1):
                return call_result16.ChangeConfigurationPayload(status='Rejected')

        CONFIGURATION[key] = original_value
        modify_config(variable=key, value=original_value, component='SecurityCtrlr')
        self.reboot = True
        return call_result16.ChangeConfigurationPayload(status='Accepted')

    @on('TriggerMessage')
    def on_trigger_message(self, requested_message: str):
        print(f'Trigger message received with reason: {requested_message}')
        if requested_message == 'SignChargingStationCertificate':
            self.csCert = True
        if VERSION == 'OCPP201':
            return call_result201.TriggerMessagePayload(status='Accepted')
        elif VERSION == 'OCPP20':
            return call_result20.TriggerMessagePayload(status='Accepted')

    @on('ExtendedTriggerMessage')
    def on_extended_trigger_message(self, requested_message: str):
        print(f'Extended trigger message received with reason: {requested_message}')
        if requested_message == 'SignChargePointCertificate':
            self.csCert = True
        if VERSION == 'OCPP16':
            return call_result16.ExtendedTriggerMessagePayload(status='Accepted')

    @on('Reset')
    def on_reset(self, type: str):
        print('Setting reboot...')
        self.reboot = True
        if VERSION == 'OCPP201':
            return call_result201.ResetPayload(status='Accepted')
        elif VERSION == 'OCPP20':
            return call_result20.ResetPayload(status='Accepted')

    @on('ReserveNow')
    def on_reserve_now(self, id_tag: str = None, reservation_id: int = None, id_token: Dict = None, id: int = None, reservation: Dict = None, expiry_date_time: str = None):
        if VERSION == 'OCPP201':
            self.print_message(f'Got a new reservation request {id} from {id_token}')
            return call_result201.ReserveNowPayload(status='Accepted')
        elif VERSION == 'OCPP20':
            self.print_message(f'Got a new reservation request {reservation["id"]} from {id_token}')
            return call_result20.ReserveNowPayload(status='Accepted')
        elif VERSION == 'OCPP16':
            self.print_message(f'Got a new reservation request {reservation_id} from token {id_tag}')
            return call_result16.ReserveNowPayload(status='Accepted')

def ChargePointClientFactory(version):
    if version == "v2.0.1":
        class ChargePointClient(Cp201, ChargePointClientBase):
            pass
        return ChargePointClient
    elif version == "v2.0":
        class ChargePointClient(Cp20, ChargePointClientBase):
            pass
        return ChargePointClient
    elif version == "v1.6":
        class ChargePointClient(Cp16, ChargePointClientBase):
            pass
        return ChargePointClient
    else:
        raise ValueError("Unsupported OCPP version")

def create_basic_auth64(cb_id: str, auth_key: bytes):
    if len(auth_key) > 0:
        token = (cb_id + ':').encode() + auth_key
        return base64.b64encode(token).decode()
    print("no authentication")
    return ""

# ---- Bağlantı ----
async def launch_client(
    vendor_name: str = 'Vendor',
    model: str = 'Model',
    index: int = None,
    serial_number: str = None,
    async_runnable: Optional[Callable[[ChargePointClientBase], Awaitable[None]]] = None
):
    global VERSION

    # Subprotocol
    if index is not None:
        if CONNECTION_PROFILES[index].ocpp_version == 'OCPP201':
            vers = "ocpp2.0.1"; VERSION = 'OCPP201'
        elif CONNECTION_PROFILES[index].ocpp_version == 'OCPP20':
            vers = "ocpp2.0"; VERSION = 'OCPP20'
        elif CONNECTION_PROFILES[index].ocpp_version == "OCPP16":
            vers = "ocpp1.6"; VERSION = 'OCPP16'
        else:
            vers = "ocpp2.0.1"; VERSION = 'OCPP201'
    else:
        vers = "ocpp1.6"; VERSION = 'OCPP16'

    headers = None
    expected_fqdn = None

    # Basic auth
    if VERSION == 'OCPP16':
        if CONFIGURATION.get('AuthorizationKey'):
            credentials = create_basic_auth64(serial_number, bytes(CONFIGURATION['AuthorizationKey'], 'utf-8'))
    else:
        if SECURITY_CTRL.get('BasicAuthPassword'):
            raw = f"{SECURITY_CTRL['Identity']}:{SECURITY_CTRL['BasicAuthPassword']}"
            credentials = base64.b64encode(raw.encode('utf-8')).decode('utf-8')

    # Security profile
    if VERSION == 'OCPP16':
        secProf = CONFIGURATION['SecurityProfile']
    else:
        secProf = CONNECTION_PROFILES[index].security_profile

    if secProf in (1, 2):
        headers = Headers({"Authorization": f'Basic {credentials}'})
    else:
        headers = None

    # Adres
    if VERSION == 'OCPP16':
        if secProf == 0:
            addr = f"ws://{IP}:{PORT0}/{serial_number}"
            sslC = None
        elif secProf == 1:
            addr = f"ws://{IP}:{PORT1}/{serial_number}"
            sslC = None
        elif secProf == 2:
            addr = f"wss://{IP}:{PORT2}/{serial_number}"
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            path = f"./charging/installedCertificates/{serial_number}/root/."
            for filename in os.listdir(path):
                full_path = os.path.join(path, filename)
                context.load_verify_locations(cafile=full_path)
            context.verify_mode = ssl.CERT_REQUIRED
            expected_fqdn = "emuocpp.com"
            context.check_hostname = True
            sslC = context
        elif secProf == 3:
            addr = f"wss://{IP}:{PORT3}/{serial_number}"
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            path = f"./charging/installedCertificates/{serial_number}/root/."
            for filename in os.listdir(path):
                full_path = os.path.join(path, filename)
                context.load_verify_locations(cafile=full_path)
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_cert_chain(certfile=CERTIFICATE_PATH, keyfile=CERTIFICATE_KEY_PATH)
            expected_fqdn = "emuocpp.com"
            sslC = context
    else:
        # 2.0/2.0.1 — doğrudan profilden URL
        addr = f"{CONNECTION_PROFILES[index].ocpp_csms_url}{SECURITY_CTRL['Identity']}"
        sslC = None
        if secProf in (2, 3):
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            path = f"./charging/installedCertificates/{SECURITY_CTRL['Identity']}/root/."
            for filename in os.listdir(path):
                full_path = os.path.join(path, filename)
                context.load_verify_locations(cafile=full_path)
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = True
            expected_fqdn = "emuocpp.com"
            if secProf == 3:
                context.load_cert_chain(certfile=CERTIFICATE_PATH, keyfile=CERTIFICATE_KEY_PATH)
            sslC = context

    # Bağlan
    async with websockets.connect(
        addr,
        subprotocols=[Subprotocol(vers)],
        extra_headers=headers,
        server_hostname=expected_fqdn,
        ssl=sslC
    ) as ws:
        ChargePointClient = ChargePointClientFactory(VERSION if VERSION != 'OCPP201' else 'v2.0.1')
        cp = ChargePointClient(serial_number if index is None else SECURITY_CTRL['Identity'], ws)

        try:
            boot_notification_args = (
                serial_number if index is None else SECURITY_CTRL['Identity'],
                model,
                vendor_name,
                secProf,
                index,
                async_runnable
            )
            await asyncio.gather(
                cp.start(),
                cp.send_boot_notification(*boot_notification_args),
                cp.check_reboot()
            )
        except websockets.exceptions.ConnectionClosed:
            print(f"[{SECURITY_CTRL['Identity'] if VERSION != 'OCPP16' else SERIAL_NUMBER}] Connection was forcefully closed by the server")
            raise ConnectionError('Connection lost with server')

async def wait_for_button_press(message: str):
    await aioconsole.ainput(f'\n{message} | Press any key to continue...\n')

if __name__ == "__main__":
    main()
