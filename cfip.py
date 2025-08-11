import random
import time
import json
import requests
import os
import traceback
from aliyun import Api_INTL
from aliyun import Api_CN
import sys
import copy
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import traceback



def load_config():
    """加载环境变量配置，缺失时立即退出"""
    try:
        config = {
            "INTL_DOMAINS": json.loads(os.environ["INTL_DOMAINS"]),
            "INTL_SECRETID": os.environ["INTL_SECRETID"],
            "INTL_SECRETKEY": os.environ["INTL_SECRETKEY"],
            
            "CN_DOMAINS": json.loads(os.environ["CN_DOMAINS"]),
            "CN_SECRETID": os.environ["CN_SECRETID"],
            "CN_SECRETKEY": os.environ["CN_SECRETKEY"],
            
            "IP_API": os.environ["IP_API"],
            "CN":False,
            "INTL":False,
            "V4":False,
            "V6":False,
        }

        REGION =  sys.argv[1]
        if REGION == "ALL":
            config["INTL"] = True
            config["CN"] = True
        elif REGION == "INTL":
            config["INTL"] = True
        elif REGION == "CN":
            config["CN"] = True

        RECORD_TYPE= sys.argv[2]
        if RECORD_TYPE == "ALL":
            config["V4"] = True
            config["V6"] = True
        elif RECORD_TYPE == "V4":
            config["V4"] = True
        elif RECORD_TYPE == "V6":
            config["V6"] = True

        print(f"✅ 环境变量加载成功")
        return config
    except KeyError as e:
        print(f"❌ 加载环境变量异常: {e}")
        sys.exit(1)  # 非零退出码

# 全局配置
CONFIG = load_config()
AFFECT_NUM = 2
TTL = 600
LINES_MAP = {"mobile", "unicom", "telecom", "oversea", "default"}
CARRIRE2LINE_MAP = {"CM": "mobile", "CU": "unicom", "CT": "telecom", "AB": "oversea", "DEF": "default"}

optimized_ips_v4 = {}
optimized_ips_v6 = {}

class OptimizedIPManager:
    @staticmethod
    def get_optimized_ips():
        """获取优化网络地址"""
        try:
            # # 使用配置中的API链接
            # response = requests.get(
            #     CONFIG["IP_API"],
            #     headers={'Content-Type': 'application/json; charset=utf-8','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
            #     timeout=10
            # )
            
            # if response.status_code != 200:
            #     print(f"❌ IP API响应异常: HTTP {response.status_code}")
            #     return False

            retry_strategy = Retry(
                total=4,  # 总共重试3次（第一次请求不算在内，所以最多4次请求）
                status_forcelist=[400, 429, 500, 502, 503, 504, 522],  # 对这些状态码重试
                allowed_methods=["GET"],  # 只对GET方法重试
                backoff_factor=1,  # 退避因子
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session = requests.Session()
            session.mount("https://", adapter)
            session.mount("http://", adapter)

            # 使用session替换原来的requests.get
            response = session.get(
                CONFIG["IP_API"],
                headers={'Content-Type': 'application/json; charset=utf-8','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
                timeout=10
            )
            print(response)
            data = response.json()
            if not data.get("success"):
                print(f"❌ IP API返回失败状态")
                return

            # response = '{"success":true,"data":{"v4":{"CM":[{"name":"移动","ip":"190.93.247.15","colo":"SJC","latency":52,"speed":295,"uptime":"2025-08-06 12:51:40"},{"name":"移动","ip":"198.41.208.55","colo":"HKG","latency":52,"speed":290,"uptime":"2025-08-06 14:04:47"},{"name":"移动","ip":"198.41.215.246","colo":"LAX","latency":53,"speed":290,"uptime":"2025-08-06 13:13:08"},{"name":"移动","ip":"198.41.209.49","colo":"HKG","latency":51,"speed":265,"uptime":"2025-08-07 10:55:24"},{"name":"移动","ip":"172.64.94.96","colo":"HKG","latency":53,"speed":260,"uptime":"2025-08-06 13:54:24"},{"name":"移动","ip":"104.16.141.58","colo":"LHR","latency":188,"speed":4848,"uptime":"2025-08-08 11:19:09"},{"name":"移动","ip":"104.18.31.216","colo":"LHR","latency":186,"speed":3887,"uptime":"2025-08-08 11:19:09"},{"name":"移动","ip":"104.17.47.88","colo":"SJC","latency":188,"speed":4631,"uptime":"2025-08-08 11:14:38"},{"name":"移动","ip":"172.66.142.234","colo":"LAX","latency":205,"speed":6442,"uptime":"2025-08-08 11:23:43"},{"name":"移动","ip":"104.19.238.28","colo":"LHR","latency":197,"speed":4074,"uptime":"2025-08-08 11:19:09"}],"CU":[{"name":"联通","ip":"172.67.153.97","colo":"FRA","latency":131,"speed":495,"uptime":"2025-08-07 11:31:42"},{"name":"联通","ip":"172.67.103.208","colo":"NRT","latency":56,"speed":330,"uptime":"2025-08-07 11:41:44"},{"name":"联通","ip":"172.67.89.132","colo":"NRT","latency":56,"speed":325,"uptime":"2025-08-07 11:31:44"},{"name":"联通","ip":"172.64.68.28","colo":"NRT","latency":56,"speed":295,"uptime":"2025-08-07 11:41:44"},{"name":"联通","ip":"162.159.245.40","colo":"NRT","latency":57,"speed":295,"uptime":"2025-08-07 11:31:44"},{"name":"联通","ip":"104.16.110.116","colo":"SJC","latency":163,"speed":6438,"uptime":"2025-08-08 11:14:04"},{"name":"联通","ip":"104.19.30.28","colo":"LAX","latency":171,"speed":3605,"uptime":"2025-08-08 11:18:55"},{"name":"联通","ip":"104.18.14.161","colo":"LAX","latency":176,"speed":4169,"uptime":"2025-08-08 11:16:49"},{"name":"联通","ip":"104.18.38.227","colo":"LAX","latency":178,"speed":4408,"uptime":"2025-08-08 11:16:49"},{"name":"联通","ip":"104.19.141.77","colo":"LAX","latency":178,"speed":3673,"uptime":"2025-08-08 11:26:58"}],"CT":[{"name":"电信","ip":"104.18.213.236","colo":"SJC","latency":142,"speed":315,"uptime":"2025-08-07 11:03:55"},{"name":"电信","ip":"104.19.82.251","colo":"SJC","latency":134,"speed":310,"uptime":"2025-08-07 11:33:54"},{"name":"电信","ip":"104.18.195.207","colo":"SJC","latency":133,"speed":310,"uptime":"2025-08-07 11:23:39"},{"name":"电信","ip":"104.19.64.131","colo":"SJC","latency":136,"speed":310,"uptime":"2025-08-07 11:13:55"},{"name":"电信","ip":"104.17.202.190","colo":"SJC","latency":133,"speed":260,"uptime":"2025-08-07 11:23:47"},{"name":"电信","ip":"104.18.37.36","colo":"SJC","latency":178,"speed":3771,"uptime":"2025-08-08 11:13:57"},{"name":"电信","ip":"104.19.45.126","colo":"SJC","latency":179,"speed":3781,"uptime":"2025-08-08 11:25:52"},{"name":"电信","ip":"104.18.30.128","colo":"LAX","latency":178,"speed":3965,"uptime":"2025-08-08 11:26:47"},{"name":"电信","ip":"172.64.153.254","colo":"SJC","latency":179,"speed":5324,"uptime":"2025-08-08 11:13:57"},{"name":"电信","ip":"104.17.45.205","colo":"SJC","latency":180,"speed":2982,"uptime":"2025-08-08 11:25:52"}]},"v6":{"CM":[{"name":"移动","ip":"2606:4700:91bc:b2f3:2aa6:ebad:5790:15e7","colo":"Default","latency":3,"speed":427,"uptime":"2025-08-07 11:39:48"},{"name":"移动","ip":"2606:4700:9ae7:9799:60ca:e531:f35a:f618","colo":"Default","latency":4,"speed":423,"uptime":"2025-08-07 11:39:48"},{"name":"移动","ip":"2606:4700:91bc:a0ba:321d:37b2:a7f1:3978","colo":"Default","latency":3,"speed":418,"uptime":"2025-08-07 11:39:49"},{"name":"移动","ip":"2606:4700:9ae7:e7ed:32fd:cf8:1f49:375f","colo":"Default","latency":4,"speed":415,"uptime":"2025-08-07 11:39:48"},{"name":"移动","ip":"2606:4700:90c5:d2b0:ebac:b7c:e58c:2a65","colo":"Default","latency":4,"speed":412,"uptime":"2025-08-07 11:39:49"},{"name":"移动","ip":"2606:4700:8d9b::5e53:a5f","colo":"SIN","latency":91,"speed":3535,"uptime":"2025-08-08 11:21:19"},{"name":"移动","ip":"2606:4700:9aef::4d5a:3b1c","colo":"SIN","latency":93,"speed":2304,"uptime":"2025-08-08 11:21:19"},{"name":"移动","ip":"2606:4700:8d77::fa9:7881","colo":"SIN","latency":91,"speed":3935,"uptime":"2025-08-08 11:02:48"},{"name":"移动","ip":"2606:4700:8de5::201c:4ea6","colo":"SIN","latency":92,"speed":3701,"uptime":"2025-08-08 11:02:48"},{"name":"移动","ip":"2606:4700:839d::440e:50b4","colo":"SIN","latency":92,"speed":3457,"uptime":"2025-08-08 11:12:09"}],"CU":[{"name":"联通","ip":"2606:4700:91bc:b2f3:2aa6:ebad:5790:15e7","colo":"Default","latency":3,"speed":427,"uptime":"2025-08-07 11:39:48"},{"name":"联通","ip":"2606:4700:9ae7:9799:60ca:e531:f35a:f618","colo":"Default","latency":4,"speed":423,"uptime":"2025-08-07 11:39:48"},{"name":"联通","ip":"2606:4700:91bc:a0ba:321d:37b2:a7f1:3978","colo":"Default","latency":3,"speed":418,"uptime":"2025-08-07 11:39:49"},{"name":"联通","ip":"2606:4700:9ae7:e7ed:32fd:cf8:1f49:375f","colo":"Default","latency":4,"speed":415,"uptime":"2025-08-07 11:39:48"},{"name":"联通","ip":"2606:4700:90c5:d2b0:ebac:b7c:e58c:2a65","colo":"Default","latency":4,"speed":412,"uptime":"2025-08-07 11:39:49"},{"name":"联通","ip":"2606:4700:300b::426b:4fd4","colo":"LAX","latency":171,"speed":3625,"uptime":"2025-08-08 10:59:35"},{"name":"联通","ip":"2606:4700:440e::5ead:4f03","colo":"LAX","latency":168,"speed":3771,"uptime":"2025-08-08 11:06:36"},{"name":"联通","ip":"2606:4700:4401::86b:786","colo":"LAX","latency":173,"speed":3813,"uptime":"2025-08-08 11:13:31"},{"name":"联通","ip":"2606:4700:52::5cf7:251d","colo":"LAX","latency":167,"speed":3762,"uptime":"2025-08-08 10:59:35"},{"name":"联通","ip":"2606:4700:300b::15c9:7175","colo":"LAX","latency":170,"speed":3739,"uptime":"2025-08-08 11:20:45"}],"CT":[{"name":"电信","ip":"2606:4700:91bc:b2f3:2aa6:ebad:5790:15e7","colo":"Default","latency":3,"speed":427,"uptime":"2025-08-07 11:39:48"},{"name":"电信","ip":"2606:4700:9ae7:9799:60ca:e531:f35a:f618","colo":"Default","latency":4,"speed":423,"uptime":"2025-08-07 11:39:48"},{"name":"电信","ip":"2606:4700:91bc:a0ba:321d:37b2:a7f1:3978","colo":"Default","latency":3,"speed":418,"uptime":"2025-08-07 11:39:49"},{"name":"电信","ip":"2606:4700:9ae7:e7ed:32fd:cf8:1f49:375f","colo":"Default","latency":4,"speed":415,"uptime":"2025-08-07 11:39:48"},{"name":"电信","ip":"2606:4700:90c5:d2b0:ebac:b7c:e58c:2a65","colo":"Default","latency":4,"speed":412,"uptime":"2025-08-07 11:39:49"}]}}}'
            # response = '{"success":true,"data":{"v4":{"CM":[{"name":"移动","ip":"172.64.80.111","colo":"Default","latency":228,"speed":640,"uptime":"2025-08-07 12:33:45"},{"name":"移动","ip":"172.67.193.216","colo":"Default","latency":225,"speed":350,"uptime":"2025-08-07 12:40:29"},{"name":"移动","ip":"172.67.203.115","colo":"Default","latency":270,"speed":280,"uptime":"2025-08-07 12:47:33"},{"name":"移动","ip":"198.41.208.186","colo":"HKG","latency":50,"speed":260,"uptime":"2025-08-07 12:40:40"},{"name":"移动","ip":"172.67.251.228","colo":"Default","latency":233,"speed":260,"uptime":"2025-08-07 12:26:54"},{"name":"移动","ip":"104.25.255.28","colo":"LHR","latency":198,"speed":4103,"uptime":"2025-08-08 12:58:10"},{"name":"移动","ip":"104.16.110.227","colo":"LHR","latency":178,"speed":3965,"uptime":"2025-08-08 12:58:10"},{"name":"移动","ip":"104.16.31.142","colo":"SJC","latency":198,"speed":5050,"uptime":"2025-08-08 12:58:41"},{"name":"移动","ip":"104.19.239.178","colo":"LHR","latency":247,"speed":4215,"uptime":"2025-08-08 12:58:41"},{"name":"移动","ip":"104.19.239.194","colo":"LHR","latency":184,"speed":2375,"uptime":"2025-08-08 12:58:10"}],"CU":[{"name":"联通","ip":"172.67.95.127","colo":"NRT","latency":56,"speed":2235,"uptime":"2025-08-07 13:11:40"},{"name":"联通","ip":"172.67.70.123","colo":"NRT","latency":57,"speed":1765,"uptime":"2025-08-07 13:11:40"},{"name":"联通","ip":"162.159.255.114","colo":"NRT","latency":56,"speed":1450,"uptime":"2025-08-07 13:11:40"},{"name":"联通","ip":"172.67.194.117","colo":"FRA","latency":131,"speed":520,"uptime":"2025-08-07 13:01:42"},{"name":"联通","ip":"198.41.208.171","colo":"NRT","latency":56,"speed":340,"uptime":"2025-08-07 13:01:44"},{"name":"联通","ip":"104.18.40.140","colo":"LAX","latency":175,"speed":3752,"uptime":"2025-08-08 13:00:45"},{"name":"联通","ip":"172.64.68.247","colo":"LAX","latency":183,"speed":4555,"uptime":"2025-08-08 12:58:41"},{"name":"联通","ip":"104.18.30.77","colo":"LAX","latency":182,"speed":3673,"uptime":"2025-08-08 12:50:44"},{"name":"联通","ip":"172.64.33.220","colo":"LAX","latency":175,"speed":3811,"uptime":"2025-08-08 12:53:56"},{"name":"联通","ip":"172.64.158.200","colo":"LAX","latency":180,"speed":4881,"uptime":"2025-08-08 12:50:44"}],"CT":[{"name":"电信","ip":"104.17.134.19","colo":"SJC","latency":136,"speed":310,"uptime":"2025-08-07 13:03:48"},{"name":"电信","ip":"104.19.197.11","colo":"SJC","latency":137,"speed":310,"uptime":"2025-08-07 12:53:48"},{"name":"电信","ip":"141.101.120.236","colo":"SEA","latency":146,"speed":310,"uptime":"2025-08-07 12:43:55"},{"name":"电信","ip":"104.18.106.37","colo":"SJC","latency":135,"speed":305,"uptime":"2025-08-07 12:53:33"},{"name":"电信","ip":"162.159.248.42","colo":"LAX","latency":142,"speed":260,"uptime":"2025-08-07 13:03:55"},{"name":"电信","ip":"104.19.141.45","colo":"LAX","latency":188,"speed":4007,"uptime":"2025-08-08 13:01:46"},{"name":"电信","ip":"104.16.94.233","colo":"LAX","latency":181,"speed":3621,"uptime":"2025-08-08 13:01:46"},{"name":"电信","ip":"172.64.158.155","colo":"SJC","latency":178,"speed":3691,"uptime":"2025-08-08 13:01:46"},{"name":"电信","ip":"104.16.158.13","colo":"SJC","latency":188,"speed":1427,"uptime":"2025-08-08 13:01:46"},{"name":"电信","ip":"104.19.253.251","colo":"LAX","latency":189,"speed":2487,"uptime":"2025-08-08 13:01:46"}]},"v6":{"CM":[{"name":"移动","ip":"2606:4700:3010:d6d8:dbca:a72b:4512:7314","colo":"Default","latency":4,"speed":431,"uptime":"2025-08-07 13:09:48"},{"name":"移动","ip":"2606:4700:10:1630:ed2b:2e69:e6d:4d42","colo":"Default","latency":3,"speed":416,"uptime":"2025-08-07 13:09:48"},{"name":"移动","ip":"2606:4700:8d7d:7365:7649:1583:7387:4a91","colo":"Default","latency":3,"speed":406,"uptime":"2025-08-07 13:09:48"},{"name":"移动","ip":"2606:4700:3010:876e:669d:9299:11a9:e323","colo":"Default","latency":3,"speed":397,"uptime":"2025-08-07 13:09:48"},{"name":"移动","ip":"2606:4700:8cad:7992:6a4d:aaf3:28e3:6e3b","colo":"Default","latency":4,"speed":396,"uptime":"2025-08-07 13:09:48"},{"name":"移动","ip":"2606:4700:90cf::721c:3903","colo":"SIN","latency":92,"speed":3617,"uptime":"2025-08-08 13:00:26"},{"name":"移动","ip":"2606:4700:9c6d::21f:2f2","colo":"SIN","latency":93,"speed":3647,"uptime":"2025-08-08 13:00:26"},{"name":"移动","ip":"2606:4700:8d73::22f0:6a45","colo":"SIN","latency":91,"speed":3543,"uptime":"2025-08-08 12:50:27"},{"name":"移动","ip":"2606:4700:8d9d::4541:5ca6","colo":"SIN","latency":93,"speed":2012,"uptime":"2025-08-08 12:41:24"},{"name":"移动","ip":"2606:4700:9b0e::6a81:7afb","colo":"SIN","latency":91,"speed":3569,"uptime":"2025-08-08 12:50:27"}],"CU":[{"name":"联通","ip":"2606:4700:3010:d6d8:dbca:a72b:4512:7314","colo":"Default","latency":4,"speed":431,"uptime":"2025-08-07 13:09:48"},{"name":"联通","ip":"2606:4700:10:1630:ed2b:2e69:e6d:4d42","colo":"Default","latency":3,"speed":416,"uptime":"2025-08-07 13:09:48"},{"name":"联通","ip":"2606:4700:8d7d:7365:7649:1583:7387:4a91","colo":"Default","latency":3,"speed":406,"uptime":"2025-08-07 13:09:48"},{"name":"联通","ip":"2606:4700:3010:876e:669d:9299:11a9:e323","colo":"Default","latency":3,"speed":397,"uptime":"2025-08-07 13:09:48"},{"name":"联通","ip":"2606:4700:8cad:7992:6a4d:aaf3:28e3:6e3b","colo":"Default","latency":4,"speed":396,"uptime":"2025-08-07 13:09:48"},{"name":"联通","ip":"2606:4700:ff00::7c6:2188","colo":"LAX","latency":171,"speed":3753,"uptime":"2025-08-08 13:02:41"},{"name":"联通","ip":"2606:4700:52::10db:c37","colo":"LAX","latency":171,"speed":4280,"uptime":"2025-08-08 12:48:31"},{"name":"联通","ip":"2606:4700:440d::7612:944","colo":"LAX","latency":172,"speed":3656,"uptime":"2025-08-08 12:55:43"},{"name":"联通","ip":"2606:4700:1200::9e4:1d81","colo":"LAX","latency":171,"speed":3579,"uptime":"2025-08-08 12:48:31"},{"name":"联通","ip":"2606:4700:3007::602b:57ff","colo":"LAX","latency":170,"speed":3798,"uptime":"2025-08-08 12:48:31"}],"CT":[{"name":"电信","ip":"2606:4700:3010:d6d8:dbca:a72b:4512:7314","colo":"Default","latency":4,"speed":431,"uptime":"2025-08-07 13:09:48"},{"name":"电信","ip":"2606:4700:10:1630:ed2b:2e69:e6d:4d42","colo":"Default","latency":3,"speed":416,"uptime":"2025-08-07 13:09:48"},{"name":"电信","ip":"2606:4700:8d7d:7365:7649:1583:7387:4a91","colo":"Default","latency":3,"speed":406,"uptime":"2025-08-07 13:09:48"},{"name":"电信","ip":"2606:4700:3010:876e:669d:9299:11a9:e323","colo":"Default","latency":3,"speed":397,"uptime":"2025-08-07 13:09:48"},{"name":"电信","ip":"2606:4700:8cad:7992:6a4d:aaf3:28e3:6e3b","colo":"Default","latency":4,"speed":396,"uptime":"2025-08-07 13:09:48"}]}}}'

            # data = json.loads(response)

            data_root = data.get("data", {})
            if not data_root:
                print(f"❌ IP API返回数据格式异常")
                return

            line_data_v4 = data_root.get("v4", {})
            line_data_v6 = data_root.get("v6", {})
            if line_data_v4 and CONFIG["V4"]:
                for carrier in CARRIRE2LINE_MAP.keys():
                    
                    if carrier in line_data_v4:
                        sorted_ips = sorted(
                            line_data_v4[carrier],
                            key=lambda x: (-x.get("speed", 0), x.get("latency", 999))
                        )
                        optimized_ips_v4[CARRIRE2LINE_MAP[carrier]] = [{"ip": ip["ip"]} for ip in sorted_ips[:3]]
                print(f"✅ 获取到IPV4优化网络地址: {list(optimized_ips_v4.keys())}线路")
                for k, v in optimized_ips_v4.items():
                    print(f"    {k}: {v}") 
                    
            if line_data_v6 and CONFIG["V6"]:
                for carrier in LINES_MAP.keys():
                    if carrier in CARRIRE2LINE_MAP.keys():
                        sorted_ips = sorted(
                            line_data_v6[carrier],
                            key=lambda x: (-x.get("speed", 0), x.get("latency", 999))
                        )
                        optimized_ips_v6[CARRIRE2LINE_MAP[carrier]] = [{"ip": ip["ip"]} for ip in sorted_ips[:3]]
                print(f"✅ 获取到IPV6优化网络地址: {list(optimized_ips_v6.keys())}线路")
                for k, v in optimized_ips_v6.items():
                    print(f"    {k}: {v}")
        except Exception as e:
            print(f"❌ 获取优化网络地址时发生异常: {str(e)}")
            traceback.print_exc()
            return

class DNSUpdater:
    def __init__(self, cloud, record_str, isIntl):
        self.cloud = cloud
        self.record_type = record_str
        self.isIntl = isIntl
        if record_str == "A":
            self.ips = optimized_ips_v4
        elif record_str == "AAAA":
            self.ips = optimized_ips_v6
        print("self.ips", self.ips)

    def _process_records(self, records):
        categorized = {k: [] for k in LINES_MAP}
        for record in records:
            record_line = record.get("line", "")
            if not record_line:
                continue
            for line in LINES_MAP:
                if line == record_line:
                    categorized[line].append({
                        "recordId": record["id"],
                        "value": record["value"]
                    })
        return categorized

    def _handle_dns_change(self, domain, sub_domain, line, current_records, candidate_ips):
        candidate_ips = copy.deepcopy(candidate_ips)


        create_num = AFFECT_NUM - len(current_records)
        
        print(f"✅ 处理线路: {line}, 现有记录: {len(current_records)}, 需要创建: {create_num}")

        used_ips = set(r["value"] for r in current_records)
        new_ips = []
        
        if create_num > 0:
            while create_num > 0 and candidate_ips:
                cf_ip = candidate_ips.pop(random.randint(0, len(candidate_ips)-1))["ip"]
                if cf_ip not in used_ips:
                    new_ips.append(cf_ip)
                    used_ips.add(cf_ip)
                    create_num -= 1
            
            for ip in new_ips:
                ret = self.cloud.create_record(domain, sub_domain, ip, self.record_type, line, TTL)
                if ret.get("statusCode", 1) == 200:
                    print(f"✅ 创建结果: {ret.get('message', '')}")
                else:
                    print(f"❌ 创建记录失败: {ret.get('message', '')}")

        for record in current_records:
            if not candidate_ips:
                break
                
            cf_ip = None
            while candidate_ips:
                candidate = candidate_ips.pop(random.randint(0, len(candidate_ips)-1))
                if candidate["ip"] not in used_ips:
                    cf_ip = candidate["ip"]
                    used_ips.add(cf_ip)
                    break
            
            if cf_ip:
                ret = self.cloud.change_record(domain, record["recordId"], sub_domain, cf_ip, self.record_type, line, TTL)
                if  self.isIntl:
                    if ret.get("statusCode", 1) == 200:
                        print(f"✅ 更新记录: {sub_domain}.{domain} -> {cf_ip}")
                    else:
                        print(f"❌ 更新记录失败: {ret.get('message', '')}")
                else:
                    if ret.get("RequestId"):
                        print(f"✅ 更新记录: {sub_domain}.{domain} -> {cf_ip}")
                    else:
                        print(f"❌ 更新记录失败: {ret.get('message', '')}")

        # self._cleanup_old_records(domain, sub_domain, line_key, current_records, candidate_ips)


    def _cleanup_old_records(self, domain, sub_domain, line_key, current_records, candidate_ips):
        """删除不再需要的 DNS 记录"""

        candidate_ip_set = {ip["ip"] for ip in candidate_ips} if candidate_ips else set()

        for record in current_records:
            if record["value"] not in candidate_ip_set:
                print(f"✅ 删除无效记录: {sub_domain}.{domain} -> {record['value']}")
                ret = self.cloud.delete_record(domain, record["recordId"])
                if ret.get("statusCode", 1) == 200:
                    print(f"✅ 删除成功: {record['value']}")
                else:
                    print(f"❌ 删除失败: {ret.get('message', '未知错误')}")

    def update_dns_records(self):
        if self.isIntl:
            domains = CONFIG["INTL_DOMAINS"]
        else:   
            domains = CONFIG["CN_DOMAINS"]
        try:
            for domain, sub_domains in domains.items():
                print(f"\n✅ 处理域名: {domain}")
                
                for sub_domain, lines in sub_domains.items():
                    print(f"\n✅ 子域名: {sub_domain}, 线路: {', '.join(lines)}")
                    
                    # 获取现有记录
                    ret = self.cloud.get_record(domain, 100, sub_domain, self.record_type)
                    if self.isIntl and ret.get("statusCode", 1) != 200:
                        # 打印ret
                        print(f"❌ 获取记录失败: {ret.get('message', '未知错误')}")
                        continue
                        
                    records = ret.get("data", {}).get("records", [])
                    categorized = self._process_records(records)


                    # 处理每条线路
                    # lines写的都是mobile.unicom.telecom
                    # self.ips是待选择的IP,都是CM.CU.CT
                    # categorized CN是CM.CU.CT,INTL是mobile.unicom.telecom
                    for line in lines:
                        line_ips = self.ips.get(line, [])
                        c_record = categorized.get(line, [])

                        # print("line--",line)
                        # print("categorized--: ",categorized)
                        # print("self.ips--: ",self.ips)
                        # print("crecord--",c_record)
                        # print("line_ips--",line_ips)
                        
                        self._handle_dns_change( domain, sub_domain, line, c_record, line_ips)
                        time.sleep(3)

            return True
        except Exception:
            print(f"❌ 更新DNS时发生异常")
            traceback.print_exc()
            return False

def main():
    print(f"\n✅ 开始DNS更新 {time.strftime('%Y-%m-%d %H:%M:%S')}")
    # cloud_intl = Api_INTL(CONFIG["INTL_SECRETID"], CONFIG["INTL_SECRETKEY"])
    # cloud_intl.create_record("eyesome.net","jp","eyesome.cf.cname.vvhan.com","CNAME","default", 600)

    OptimizedIPManager.get_optimized_ips()

    if CONFIG["INTL"]:
        cloud_intl = Api_INTL(CONFIG["INTL_SECRETID"], CONFIG["INTL_SECRETKEY"])
        print(f"✅ INTL DNS客户端初始化完成")
        if CONFIG["V4"]:
            updater = DNSUpdater(cloud_intl,"A",True)
            success = updater.update_dns_records()
            if success:
                print(f"\n✅ INTL IPV4 更新成功完成! {time.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(3)
        if CONFIG["V6"]:
            updater = DNSUpdater(cloud_intl,"AAAA",True)
            success = updater.update_dns_records()
            if success:
                print(f"\n✅ INTL IPV6 更新成功完成! {time.strftime('%Y-%m-%d %H:%M:%S')}")

    time.sleep(3)
    if CONFIG["CN"]:
        cloud_cn = Api_CN(CONFIG["CN_SECRETID"], CONFIG["CN_SECRETKEY"])
        print(f"✅ CN DNS客户端初始化完成")
        if CONFIG["V4"]:
            updater = DNSUpdater(cloud_cn,"A", False)
            success = updater.update_dns_records()
            if success:
                print(f"\n✅ CN IPV4 更新成功完成! {time.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(3)
        if CONFIG["V6"]:
            updater = DNSUpdater(cloud_cn,"AAAA",False)
            success = updater.update_dns_records()
            if success:
                print(f"\n✅ CN IPV6 更新成功完成! {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()