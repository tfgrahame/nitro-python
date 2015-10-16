from requests import get, put
from requests.auth import HTTPBasicAuth
from lxml import etree
from math import ceil
from nitro_py.endpoints import *
import os

def get_response(endpoint, feed, cert, api_key, mixins=None, **kwargs):
    """Makes an HTTP GET request to an endpoint, optionally with mixins and parameters"""
    headers = {'Accept': 'application/xml'}
    r = get(endpoint + feed + '?api_key=' + api_key + fmt_mixins(mixins) + fmt_kwargs(kwargs), headers=headers, cert=cert)
    if r.status_code == 200:
        return r
    else:
        r.raise_for_status()

def fmt_mixins(mixins):
    """Formats a list of mixin values into a string useable by the API"""
    # mixins = ['ancestor_titles', 'contributions']
    if mixins:
        return "".join(['&mixin=' + mixin for mixin in mixins])
    else:
        return ""

def fmt_kwargs(kwargs):
    """Formats a dict (key:value pairs) into a string useable by the API"""
    # {'entity_type':'clip', 'availability':'available'}
    if kwargs:
        return "".join(['&' + kw + '=' + kwargs[kw] for kw in sorted(kwargs)])
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




