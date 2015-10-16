from nitro_py.nitro_py import *
from nitro_py.endpoints import *
from functools import partial
from itertools import count
import os

def main():
    cert = os.environ.get('CERT')
    api_key = os.environ.get('NITRO_E2E_KEY')
    mixins = ['availability', 'ancestor_titles']
    page_size = 100
    entity_type = 'clip'
    filters = {'entity_type':''}
    #partial_get_response = partial(get_response, NITRO_E2E, 'programmes', cert, api_key, mixins, entity_type=entity_type, availability='available', page_size=str(page_size))
    partial_get_response = partial(get_response, NITRO_E2E, 'programmes', cert, api_key, mixins, entity_type=entity_type, availability='available', media_type='audio', availability_entity_type=entity_type, page_size=str(page_size))
    page1 = partial_get_response(page='1')
    page1_xml = infoset(page1)
    pages = pages_total(page1_xml, page_size)
    serialize_entities(page1_xml, entity_type)
    page = count(start=2, step=1)
    for i in range(pages - 1):
        next_page = str(next(page))
        response = partial_get_response(page=next_page)
        with open('nitro.log', 'a') as log:
            log.write(NITRO_E2E + 'programmes' + '?api_key=' + api_key + fmt_mixins(mixins) + '&entity_type=entity_type&availability=available' + '&page=' + next_page + ',' + str(response.status_code) + '\n')
        response_xml = infoset(response)
        serialize_entities(response_xml, entity_type)

if __name__ == "__main__":
    main()