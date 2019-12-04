from brave.inputs.uri import UriInput
from brave.inputs.test_video import TestVideoInput
from brave.inputs.test_audio import TestAudioInput
from brave.inputs.image import ImageInput
from brave.inputs.html import HTMLInput
from brave.inputs.decklink import DecklinkInput
from brave.inputs.tcp_client import TcpClientInput
#sebastian added input for shm
from brave.inputs.shm_client import ShmClientInput
from brave.abstract_collection import AbstractCollection
import brave.exceptions


class InputCollection(AbstractCollection):
    def add(self, **args):
        if 'id' not in args:
            args['id'] = self.get_new_id()

        if 'type' not in args:
            raise brave.exceptions.InvalidConfiguration("Invalid input missing 'type'")
        elif args['type'] == 'uri':
            input = UriInput(**args, collection=self)
        elif args['type'] == 'test_video':
            input = TestVideoInput(**args, collection=self)
        elif args['type'] == 'test_audio':
            input = TestAudioInput(**args, collection=self)
        elif args['type'] == 'image':
            input = ImageInput(**args, collection=self)
        elif args['type'] == 'html':
            input = HTMLInput(**args, collection=self)
        elif args['type'] == 'decklink':
            input = DecklinkInput(**args, collection=self)
        elif args['type'] == 'tcp_client':
            input = TcpClientInput(**args, collection=self)
        #sebastian added input for shm
        elif args['type'] == 'shm_client':
            input = ShmClientInput(**args, collection=self)
        else:
            raise brave.exceptions.InvalidConfiguration(f"Invalid input type '{str(args['type'])}'")

        self._items[args['id']] = input
        return input
