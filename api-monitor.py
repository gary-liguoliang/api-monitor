import datetime
import logging
from time import sleep

import os
import requests
from requests import ConnectionError

logger = logging.getLogger(__name__)


class MonitorJob:
    def __init__(self, url, method, expected_response_code, sleep_time_in_seconds=30):
        self.url = url
        self.method = method
        self.expected_response_code = expected_response_code
        self.sleep_time_in_seconds = sleep_time_in_seconds

    def __repr__(self):
        return 'url %s, expected code: %s' % (self.url, self.expected_response_code)


class HttpResponse:
    def __init__(self, monitor_job, status, content, received_on=None):
        self.received_on = received_on or datetime.datetime.now()
        self.monitor_job = monitor_job
        self.status = status
        self.content = content
        self.is_result_expected = ("OK" if status == monitor_job.expected_response_code else "Error").ljust(5, ' ')

    def __repr__(self):
        return "%s - %s - response code: %s (expected: %s)" % (self.received_on, self.is_result_expected,
                                                               self.status, self.monitor_job.expected_response_code)


class MonitorJobExecutor:
    def __init__(self):
        pass

    def execute_job(self, j):
        try:
            r = requests.request(j.method.lower(), j.url)
            return HttpResponse(j, r.status_code, r.content)
        except ConnectionError as conn_error:
            return HttpResponse(j, 'xxx', conn_error)

class JobScheduler:
    def __init__(self, executor):
        self.executor = executor

    def schedule_job(self, j):
        while True:
            try:
                r = self.executor.execute_job(j)
                logger.info(r)
                sleep(j.sleep_time_in_seconds)
            except Exception as e:
                print("Exception happens: %s" % e)


def setup_log(log_file=None):
    log_file = log_file or os.path.join(os.path.dirname(os.path.realpath(__file__)), "monitor.log")
    log_format = "%(asctime)s [%(name)s] [%(levelname)-5.5s]  %(message)s"
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(console_handler)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(file_handler)


if __name__ == '__main__':
    setup_log()
    job = MonitorJob('https://google.com', 'GET', 200, 5)
    scheduler = JobScheduler(MonitorJobExecutor())
    scheduler.schedule_job(job)
