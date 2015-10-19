from requests import get, put
from functools import partial
from itertools import count
from requests.auth import HTTPBasicAuth
from lxml import etree
from math import ceil
from nitro_py.endpoints import *
import os

def get_response(url, cert, page):
    """Makes an HTTP GET request to an endpoint"""
    headers = {'Accept': 'application/xml'}
    return get(url, headers=headers, cert=cert)

def fmt_mixins(mixins):
    """Formats a list of mixin values into a string useable by the API"""
    # mixins = ['ancestor_titles', 'contributions']
    if mixins:
        return "".join(['&mixin=' + mixin for mixin in mixins])
    else:
        return ""

def fmt_filters(filters):
    """Formats a dict (key:value pairs) into a string useable by the API"""
    # {'entity_type':'clip', 'availability':'available'}
    if filters:
        return "".join(['&' + filter + '=' + filters[filter] for filter in sorted(filters)])
    else:
        return ""

NSMAP = {'n': 'http://www.bbc.co.uk/nitro/'}

def infoset(response):
    """Parse the bytestream of a requests object into an ElementTree object"""
    return etree.XML(response.content)

def results_total(infoset):
    """Return the number of results from the Nitro query"""
    return int(infoset.xpath('/n:nitro/n:results/@total', namespaces=NSMAP)[0])

def pages_total(infoset, page_size):
    """Return the expected number of pages"""
    return ceil(float(results_total(infoset)) / page_size)

def resources(infoset, entity_type):
    """Generate a series of Nitro resources from a given Nitro XML response"""
    for entity in infoset.xpath('/n:nitro/n:results/n:' + entity_type, namespaces=NSMAP):
        yield entity

def pid(infoset):
    """Return the pid of a Nitro entity"""
    # Since the infoset in this case is Element, xpath() operates on the context node
    return infoset.xpath('n:pid/text()', namespaces=NSMAP)[0]

def serialize_entities(infoset, entity_type):
    """Makes an HTTP PUT request to a local instance of eXist"""
    auth = HTTPBasicAuth(os.environ.get('USER'), os.environ.get('EXIST_PASSWORD'))
    url = 'http://localhost:8080/exist/rest/db/test/'
    for entity in resources(infoset, entity_type):
        data = etree.tostring(entity)
        response = put(url=url + pid(entity) + '.xml', data=data, auth=auth)
        with open('exist.log', 'a') as log:
            log.write(url + pid(entity) + '.xml' + ',' + str(response.status_code) + '\n')

def log_nitro(url, page, response):
    with open('nitro.log', 'a') as log:
        log.write(url + '&page=' + page + ',' + str(response.status_code) + '\n')

def call_nitro(cert, api_key, mixins, feed, filters, env):
    """Call Nitro, perform all looping etc"""
    url = env + feed + '?api_key=' + api_key + fmt_mixins(mixins) + fmt_filters(filters)
    partial_get_response = partial(get_response, url, cert)
    page1 = partial_get_response(page='1')
    log_nitro(url, '1', page1)
    page1_xml = infoset(page1)
    pages = pages_total(page1_xml, int(filters['page_size']))
    serialize_entities(page1_xml, filters['entity_type'])
    page = count(start=2, step=1)
    for i in range(pages - 1):
        next_page = str(next(page))
        response = partial_get_response(page=next_page)
        log_nitro(url, next_page, response)
        response_xml = infoset(response)
        serialize_entities(response_xml, filters['entity_type'])






