from nitro_py.nitro_py import *
from nitro_py.endpoints import *
import os

def main():
    mixins = ['availability', 'ancestor_titles', 'versions_availability', 'genre_groupings']
    filters = {'entity_type':'clip', 'availability':'available', 'media_type':'audio', 'availability_entity_type':'clip', 'page_size':'100'}
    base = NITRO_E2E + 'programmes'
    api_key = os.environ.get('NITRO_E2E_KEY')
    call_nitro(base, mixins, filters, api_key)

if __name__ == "__main__":
    main()