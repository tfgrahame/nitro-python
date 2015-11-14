from nitro_py.nitro_py import *
from nitro_py.endpoints import *
import os

def main():
    mixins = ['availability', 'ancestor_titles', 'versions_availability', 'genre_groupings']
    filters = {'entity_type':'clip', 'availability':'available', 'media_type':'audio', 'availability_entity_type':'clip', 'page_size':'100', 'master_brand':'bbc_radio_four','genre':'100005'}
    base = NITRO_LIVE + 'programmes'
    call_nitro(base, mixins, filters)

if __name__ == "__main__":
    main()