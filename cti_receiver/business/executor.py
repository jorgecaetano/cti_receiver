from datetime import datetime
from json import loads
from queue import Queue
from threading import Thread, Condition
from typing import Dict, Callable, AnyStr

from cti_receiver.libs.database.mongo_connection import get_mongo_connection


class ProcessCommand(Thread):
    """
    Responsavel por processar eventos do FreeSwitch
    """

    def __init__(self):
        super().__init__()
        self.__condition = Condition()
        self.__queue = Queue()

        self.__events = {
            'CHANNEL_HANGUP_COMPLETE': self.process_channel_hangup_complete
        }

    def run(self):
        queue = self.__queue
        while True:
            try:
                with self.__condition:
                    self.__condition.wait()

                while not queue.empty():
                    try:
                        item = queue.get(False)
                        if item:
                            event = self.normalize_event(item)
                            routine: Callable = self.__events.get(event['CTI-Event-Name'])
                            if routine:
                                routine(event)
                    except Exception as err:
                        print(err)
            except Exception as err:
                print(err)

    def enqueue(self, channel, method, properties, body):
        queue = self.__queue
        with self.__condition:
            queue.put(body)
            self.__condition.notify_all()

    @staticmethod
    def normalize_event(event: AnyStr) -> Dict:
        buffer = loads(event.decode()) if isinstance(event, bytes) else loads(event)
        buffer['CTI-Event-Name'] = (buffer.get('CC-Action') or buffer.get('Event-Subclass') or buffer['Event-Name']).upper()
        buffer['CTI-Event-Date'] = datetime.fromtimestamp(int(buffer['Event-Date-Timestamp']) / 1000000)
        return buffer

    @staticmethod
    def process_channel_hangup_complete(event: Dict):
        process_id = event.get('variable_PROCESS_ID')
        if not process_id:
            return
        destination = event.get('variable_DESTINATION')
        call_id = event.get('variable_CALL_ID')
        start = datetime.fromtimestamp(int(event.get('variable_start_uepoch', '0')) / 1000000)
        end = datetime.fromtimestamp(int(event.get('variable_end_uepoch', '0')) / 1000000)
        answer = datetime.fromtimestamp(int(event['variable_answer_uepoch']) / 1000000) if event.get('variable_answer_epoch', '0') != '0' else None
        bill_seconds = int(event.get('variable_billsec', '0'))
        total_seconds = int(event.get('variable_duration', '0'))
        hangup_cause = event.get('Hangup-Cause', 'UNSPECIFIED')

        calls_details_db = get_mongo_connection('dialer', 'calls_details')
        calls_details_db.insert_one({
            'process_id': process_id,
            'destination': destination,
            'call_id': call_id,
            'start': start,
            'end': end,
            'answer': answer,
            'total_seconds': total_seconds,
            'bill_seconds': bill_seconds,
            'hangup_cause': hangup_cause
        })
