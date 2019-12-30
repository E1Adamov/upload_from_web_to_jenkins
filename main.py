#!python3

import os
import queue

import config
from python import global_objects


def main():
    global_objects.q = queue.Queue()

    from python import async_server, helper
    import python.alt_d_data_handler as data_handler

    temp_dir = os.path.join(helper.get_server_location(), config.TEMP)
    helper.clear_dir(temp_dir)

    alt_d_data_handler = data_handler.AltDDataHandler()

    #  this thread will be always alive and waiting for data to be put to the global_objects.q
    alt_d_data_handler.start_jenkins_upload_thread()

    async_server.run()


if __name__ == '__main__':
    main()
