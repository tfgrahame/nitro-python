from requests import get, put
from functools import partial
from itertools import count
from requests.auth import HTTPBasicAuth
from lxml import etree
from math import ceil
from nitro_py.endpoints import *
from time import sleep
import os

def get_response(base, mixins, filters, api_key, page):
    """Makes an HTTP GET request to an endpoint"""
    url = base + '?api_key=' + api_key + fmt_mixins(mixins) + fmt_filters(filters) + '&page=' + page
    response = get(url, headers={'Accept': 'application/xml'}, cert=os.environ.get('CERT'))
    with open('nitro.log', 'a') as log:
        log.write(url + ',' + str(response.status_code) + '\n')
    return response

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

def get_resources(infoset, entity_type):
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
    for entity in get_resources(infoset, entity_type):
        data = etree.tostring(entity)
        response = put(url=url + pid(entity) + '.xml', data=data, auth=auth)
        with open('exist.log', 'a') as log:
            log.write(url + pid(entity) + '.xml' + ',' + str(response.status_code) + '\n')

def serialize_entity(entity):
    auth = HTTPBasicAuth(os.environ.get('USER'), os.environ.get('EXIST_PASSWORD'))
    url = 'http://localhost:8080/exist/rest/db/test/' + pid(entity) + '.xml'
    data = etree.tostring(entity)
    response = put(url=url, data=data, auth=auth)
    with open('exist.log', 'a') as log:
            log.write(url + ',' + str(response.status_code) + '\n')

def get_ancestors(entity, entity_type, base, api_key):
    """Given a Nitro entity, get the ancestors and insert them into the entity document"""
    ancestors = etree.Element('ancestors')
    entity.insert(0, ancestors)
    mixins = ['ancestor_titles', 'genre_groupings']
    for ancestor in etree.ElementTree(entity).xpath('/n:' + entity_type + '/n:ancestor_titles/*', namespaces=NSMAP):
        # keep requests to below 100/min
        sleep(1)
        successful = False
        while not successful:
            ancestor_response = get_response(base, mixins, {'pid': ancestor.xpath('n:pid/text()', namespaces=NSMAP)[0]}, api_key, '1')
            if ancestor_response.status_code != 200:
                sleep(10)
            else:
                response_xml = infoset(ancestor_response)
                ancestors.append(response_xml.xpath('/n:nitro/n:results/n:' + etree.QName(ancestor).localname, namespaces=NSMAP)[0])
                successful = True
    return entity

def call_nitro(base, mixins, filters, api_key):
    """Call Nitro, perform all looping etc"""
    partial_get_response = partial(get_response, base, mixins, filters, api_key)
    first_response = partial_get_response(page='1')
    first_response_xml = infoset(first_response)
    for entity in get_resources(first_response_xml, filters['entity_type']):
        entity_with_ancestors = get_ancestors(entity, filters['entity_type'], base, api_key)
        serialize_entity(entity_with_ancestors)
    pages = pages_total(first_response_xml, int(filters['page_size']))
    page = count(start=2, step=1)
    for i in range(pages - 1):
        # keep requests to below 100/min
        sleep(1)
        next_page = str(next(page))
        successful = False
        while not successful:
            response = partial_get_response(page=next_page)
            if response.status_code != 200:
                sleep(10)
            else:
                response_xml = infoset(response)
                for entity in get_resources(first_response_xml, filters['entity_type']):
                    entity_with_ancestors = get_ancestors(entity, filters['entity_type'], base, api_key)
                    serialize_entity(entity_with_ancestors)
                successful = True





