import time
import re
import logging
from ..command import Command, ResultValue, ResultValueState

logger = logging.getLogger(__name__)

class ServingCellCommand(Command):
    """
    Checks Serving Cell information
    """

    def __init__(self):
        super().__init__("Serving Cell", "Serving Cell Information")

    def poll(self, serial_port):

        # Send the Serving Cell query
        logger.debug("Polling ServingCell...")
        serial_port.write("AT+QENG=\"Servingcell\"\r\n".encode("utf-8"))

        # Wait for the response to be written
        time.sleep(0.5)

        # Read the response content
        cmd_result = self.receive(serial_port, multi_result=True)

        # Clear the results
        self.results = []
        
        if not cmd_result[0]:
            logger.warn("No response to ServingCell query")
            # No results to work with
            return

        for result_line in cmd_result[1]:

            # Process the result line for any status details
            status_matches = re.match(r'\+QENG:\s?"servingcell","(.*)"', result_line)
            if status_matches is not None:
                self.results.append(ResultValue("status", "UE Status", "Overall UE Status", status_matches.group(1)))

            # Process the result line for any technology details
            tech_matches = re.search(r'"(LTE|NR5G-NSA|WCDMA)",(.*)', result_line)

            if tech_matches is None:
                continue

            if tech_matches.group(1) == 'NR5G-NSA':
                # Process NR5G group
                nr_params = tech_matches.group(2).split(",")
                if len(nr_params) >= 6:
                    self.results.append(ResultValue("nr_nsa_mcc", "5GNR-NSA MCC", "5G Mobile Country Code", nr_params[0]))
                    self.results.append(ResultValue("nr_nsa_mnc", "5GNR-NSA MNC", "5G Mobile Network Code", nr_params[1]))
                    self.results.append(ResultValue("nr_nsa_pcid", "5GNR-NSA PhyCell ID", "5G Physical Cell ID", nr_params[2]))
                    self.results.append(ResultValue("nr_nsa_rsrp", "5GNR-NSA RSRP", "5G Signal Power (dBmW)", nr_params[3]))
                    self.results.append(ResultValue("nr_nsa_sinr", "5GNR-NSA SINR", "5G Signal:Noise+Intrf. Ratio", nr_params[4]))
                    self.results.append(ResultValue("nr_nsa_rsrq", "5GNR-NSA RSRQ", "5G Signal Quality (dBmW)", nr_params[5]))

            elif tech_matches.group(1) == 'LTE':
                # Process LTE group
                lte_params = tech_matches.group(2).split(",")
                if len(lte_params) >= 14:
                    self.results.append(ResultValue("lte_dup_type", "LTE Duplex", "LTE Duplex Mode", lte_params[0]))
                    self.results.append(ResultValue("lte_mcc", "LTE MCC", "LTE Mobile Country Code", lte_params[1]))
                    self.results.append(ResultValue("lte_mnc", "LTE MNC", "LTE Mobile Network Code", lte_params[2]))
                    self.results.append(ResultValue("lte_cid", "LTE Cell ID", "LTE Cell ID", lte_params[3]))
                    self.results.append(ResultValue("lte_pcid", "LTE PhyCell ID", "LTE Physical Cell ID", lte_params[4]))
                    self.results.append(ResultValue("lte_earfcn", "LTE EARFCN", "LTE E-UTRA Absolute Radio Frequency Channel Number", lte_params[5]))
                    self.results.append(ResultValue("lte_freq_band_ind", "LTE Freq. Band Index", "LTE Frequency Band Index", lte_params[6]))
                    self.results.append(ResultValue("lte_ul_bw", "LTE Upstream BW", "LTE Upstream Bandwidth", lte_params[7]))
                    self.results.append(ResultValue("lte_dl_bw", "LTE Downstream BW", "LTE Downstream Bandwidth", lte_params[8]))
                    self.results.append(ResultValue("lte_tac", "LTE TAC", "LTE Tracking Area Code", lte_params[9]))
                    self.results.append(ResultValue("lte_rsrp", "LTE RSRP", "LTE Signal Power (dBmW)", lte_params[10]))
                    self.results.append(ResultValue("lte_rsrq", "LTE RSRQ", "LTE Signal Quality (dB)", lte_params[11]))
                    self.results.append(ResultValue("lte_rssi", "LTE RSSI", "LTE Signal Strength (dBm)", lte_params[12]))
                    self.results.append(ResultValue("lte_sinr", "LTE SINR", "LTE Signal:Noise+Intrf. Ratio", lte_params[13]))
                    # self.results.append(ResultValue("lte_cqi", "LTE CQI", "LTE Channel Quality Indicator", lte_params[14]))
                    # self.results.append(ResultValue("lte_tx_power", "LTE TX Power", "LTE Transmit Power (dBmW)", lte_params[15]))

            elif tech_matches.group(1) == 'WCDMA':
                # Process UMTS group
                wcdma_params = tech_matches.group(2).split(",")
                if len(wcdma_params) >= 12:
                    self.results.append(ResultValue("wcdma_mcc", "WCDMA MCC", "WCDMA Mobile Country Code", wcdma_params[0]))
                    self.results.append(ResultValue("wcdma_mnc", "WCDMA MNC", "WCDMA Mobile Network Code", wcdma_params[1]))
                    self.results.append(ResultValue("wcdma_lac", "WCDMA LAC", "WCDMA Location Area Code", wcdma_params[2]))
                    self.results.append(ResultValue("wcdma_cid", "WCDMA Cell ID", "WCDMA Cell ID", wcdma_params[3]))
                    self.results.append(ResultValue("wcdma_uarfcn", "WCDMA UARFCN", "WCDMA UTRA Absolute Radio Frequency Channel Number", wcdma_params[4]))
                    self.results.append(ResultValue("wcdma_psc", "WCDMA PSC", "WCDMA Primary Scrambling Code", wcdma_params[5]))
                    self.results.append(ResultValue("wcdma_rac", "WCDMA RAC", "WCDMA Routing Area Code", wcdma_params[6]))
                    self.results.append(ResultValue("wcdma_rscp", "WCDMA RSCP", "WCDMA Received Signal Code Power", wcdma_params[7]))
                    self.results.append(ResultValue("wcdma_ecio", "WCDMA ECIO", "WCDMA Energy/chip : Interference Ratio", wcdma_params[8]))
                    self.results.append(ResultValue("wcdma_phy_ch", "WCDMA Physical Channel", "WCDMA Physical Channel", wcdma_params[9]))
                    self.results.append(ResultValue("wcdma_sf", "WCDMA SF", "WCDMA Spreading Factor", wcdma_params[10]))
                    self.results.append(ResultValue("wcdma_slot", "WCDMA Slot", "WCDMA Slot ID", wcdma_params[11]))
                    # self.results.append(ResultValue("wcdma_speech_code", "WCDMA Speech Code", "WCDMA Speech Code", wcdma_params[12]))
                    # self.results.append(ResultValue("wcdma_com_mode", "WCDMA Compression", "WCDMA Compression On/Off", wcdma_params[13]))
                    
        self.last_update = time.time()