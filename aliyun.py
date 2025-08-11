#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Mail: tongdongdong@outlook.com
# Reference: https://help.aliyun.com/document_detail/29776.html?spm=a2c4g.11186623.2.38.3fc33efexrOFkT
# REGION: https://help.aliyun.com/document_detail/198326.html
import json

from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_credentials.client import Client as CredClient
from alibabacloud_credentials.models import Config as CreConfig
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

from aliyunsdkcore import client
from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109 import DeleteDomainRecordRequest
from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109 import AddDomainRecordRequest


rc_format = 'json'


class Api_INTL():
    def __init__(self, ACCESSID, SECRETKEY):
        self.access_key_id = ACCESSID
        self.access_key_secret = SECRETKEY

    def create_client(self) -> Alidns20150109Client:
        try:
            credentialsConfig = CreConfig(
                type='access_key',
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret,
            )
            credentialClient = CredClient(credentialsConfig)
            dnsConfig = open_api_models.Config(credential=credentialClient)
            dnsConfig.endpoint = 'alidns.cn-hongkong.aliyuncs.com'
            return Alidns20150109Client(dnsConfig)
        except Exception as e:
            print(f"Failed to create client: {str(e)}")
            raise

    def del_record(self, domain, record):
        try:
            client = self.create_client()
            request = alidns_20150109_models.DeleteDomainRecordRequest(record_id=record)
            print(f"🚀 Deleting record {record} for domain {domain}")
            result = client.delete_domain_record(request)
            print(f"✅ Record {record} deleted successfully")
            return result.to_map()
        except Exception as e:
            print(f"❌ Failed to delete record {record}: {str(e)}")
            raise

    def get_record(self, domain, length, sub_domain, record_type):
        try:
            client = self.create_client()
            request = alidns_20150109_models.DescribeDomainRecordsRequest(
                domain_name=domain,
                page_size=length,
                rrkey_word=sub_domain,
                type=record_type
            )
            print(f"🚀 Getting records for domain {domain}, subdomain {sub_domain}, type {record_type}")
            result = client.describe_domain_records(request).to_map()
            result['data'] = result.pop('body')['DomainRecords']
            result['data']['records'] = result['data'].pop('Record')
            for record in result['data']['records']:
                record['value'] = record.pop('Value')
                record['id'] = record.pop('RecordId')
                record['line'] = record['Line']
            print(f"✅ Successfully retrieved {len(result['data']['records'])} records")
            return result
        except Exception as e:
            print(f"❌ Failed to get records: {str(e)}")
            raise

    def create_record(self, domain, sub_domain, value, record_type, line, ttl):
        try:
            client = self.create_client()
            request = alidns_20150109_models.AddDomainRecordRequest(
                domain_name=domain,
                rr=sub_domain,
                type=record_type,
                value=value,
                line=line,
                ttl=600
            )
            print(f"🚀 Creating record for domain {domain}, subdomain {sub_domain}, type {record_type}")
            result = client.add_domain_record(request)
            print(f"Record created successfully with ID {result.body.record_id}")
            return result.to_map()
        except Exception as e:
            print(f"❌ Failed to create record: {str(e)}")
            raise

    def change_record(self, domain, record_id, sub_domain, value, record_type, line, ttl):
        try:
            client = self.create_client()
            request = alidns_20150109_models.UpdateDomainRecordRequest(
                record_id=record_id,
                rr=sub_domain,
                type=record_type,
                value=value,
                line=line,
                ttl=ttl
            )
            print(f"🚀 Updating record {record_id} for domain {domain}")
            result = client.update_domain_record(request)
            print(f"✅ Record {record_id} updated successfully")
            return result.to_map()
        except Exception as e:
            print(f"❌ Failed to update record {record_id}: {str(e)}")
            raise


class Api_CN():
    def __init__(self, ACCESSID, SECRETKEY, REGION='cn-hangzhou'):
        self.access_key_id = ACCESSID
        self.access_key_secret = SECRETKEY
        self.region = REGION

    def create_client(self):
        return client.AcsClient(self.access_key_id, self.access_key_secret, self.region)

    def del_record(self, domain, record):
        try:
            client = self.create_client()
            request = DeleteDomainRecordRequest.DeleteDomainRecordRequest()
            request.set_RecordId(record)
            request.set_accept_format(rc_format)
            print(f"🚀 Deleting record {record} for domain {domain}")
            result = client.do_action(request).decode('utf-8')
            result = json.JSONDecoder().decode(result)
            print(f"✅ Record {record} deleted successfully")
            return result
        except Exception as e:
            print(f"❌ Failed to delete record {record}: {str(e)}")
            raise

    def get_record(self, domain, length, sub_domain, record_type):
        try:
            client = self.create_client()
            request = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
            request.set_DomainName(domain)
            request.set_PageSize(length)
            request.set_RRKeyWord(sub_domain)
            request.set_Type(record_type)
            request.set_accept_format(rc_format)
            print(f"🚀 Getting records for domain {domain}, subdomain {sub_domain}, type {record_type}")
            result = client.do_action(request).decode('utf-8')
            result = result.replace('DomainRecords', 'data', 1)\
                          .replace('Record', 'records', 1)\
                          .replace('RecordId', 'id')\
                          .replace('Value', 'value')\
                          .replace('Line', 'line')
            result = json.JSONDecoder().decode(result)
            for record in result['data']['records']:
                record['line'] =record['line']
            print(f"✅ Successfully retrieved {len(result['data']['records'])} records")
            return result
        except Exception as e:
            print(f"❌ Failed to get records: {str(e)}")
            raise

    def create_record(self, domain, sub_domain, value, record_type, line, ttl):
        try:
            client = self.create_client()
            request = AddDomainRecordRequest.AddDomainRecordRequest()
            request.set_DomainName(domain)
            request.set_RR(sub_domain)
            request.set_Line(line)
            request.set_Type(record_type)
            request.set_Value(value)
            request.set_TTL(ttl)
            request.set_accept_format(rc_format)
            print(f"🚀 Creating record for domain {domain}, subdomain {sub_domain}, type {record_type}")
            result = client.do_action(request).decode('utf-8')
            result = json.JSONDecoder().decode(result)
            print(f"✅ Record created successfully with ID {result.get('RecordId', 'unknown')}")
            return result
        except Exception as e:
            print(f"❌ Failed to create record: {str(e)}")
            raise
        
    def change_record(self, domain, record_id, sub_domain, value, record_type, line, ttl):
        try:
            client = self.create_client()
            request = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
            request.set_RR(sub_domain)
            request.set_RecordId(record_id)
            request.set_Line(line)
            request.set_Type(record_type)
            request.set_Value(value)
            request.set_TTL(ttl)
            request.set_accept_format(rc_format)
            print(f"🚀 Updating record {record_id} for domain {domain}")
            result = client.do_action(request).decode('utf-8')
            result = json.JSONDecoder().decode(result)
            print(f"✅ Record {record_id} updated successfully")
            return result
        except Exception as e:
            print(f"❌ Failed to update record {record_id}: {str(e)}")
            raise

