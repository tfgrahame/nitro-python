from nitro_py.nitro_py import *
from nitro_py.endpoints import *
import os

def main():
    cert = os.environ.get('CERT')
    api_key = os.environ.get('NITRO_E2E_KEY')
    mixins = ['availability', 'ancestor_titles']
    feed = 'programmes'
    filters = {'entity_type':'clip', 'availability':'available', 'media_type':'audio', 'availability_entity_type':'clip', 'page_size':'100'}
    env = NITRO_E2E
    call_nitro(cert, api_key, mixins, feed, filters, env)

if __name__ == "__main__":
    main()