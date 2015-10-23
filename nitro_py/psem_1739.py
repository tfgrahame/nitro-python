from nitro_py.nitro_py import *
from nitro_py.endpoints import *
import os

def main():
    mixins = ['availability', 'ancestor_titles', 'versions_availability']
    filters = {'entity_type':'clip', 'availability':'available', 'media_type':'audio', 'availability_entity_type':'clip', 'page_size':'100'}
    base = NITRO_E2E + 'programmes'
    call_nitro(base, mixins, filters)

if __name__ == "__main__":
    main()