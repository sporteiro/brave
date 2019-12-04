from brave.inputs.input import Input
from gi.repository import Gst
import brave.config as config
import brave.exceptions
import time

class ShmClientInput(Input):
    '''
    Allows an an input by receiving from another server via SHM.
    Basically using the `shmsrc` element.
    '''

    def permitted_props(self):
        return {
            **super().permitted_props(),
            'uriAudio': {
                'type': 'str',
            },
            'uriVideo': {
                'type': 'str',
            },
            'volume': {
                'type': 'float',
                'default': 0.8
            },
            'width': {
                'type': 'int'
            },
            'height': {
                'type': 'int'
            },
            'xpos': {
                'type': 'int',
                'default': 0
            },
            'ypos': {
                'type': 'int',
                'default': 0
            },
            'zorder': {
                'type': 'int',
                'default': 1
            }
        }

    def create_elements(self):
        '''
        Creates the pipeline with elements needed to accept a SHM connection.
        '''
        #print(self.uriAudio)
        #print(self.uriVideo)

        # We support ogg and mpeg containers; the right demuxer must be used:
        #demux_element = 'oggdemux' if self.container == 'ogg' else 'tsdemux'
        shm_video_path = self.uriVideo
        shm_audio_path = self.uriAudio
        # We start with tcpclientsrc, and immediately demux it into audio and video.
        #pipeline_string = 'tcpclientsrc name=tcpclientsrc ! %s name=demux ' % demux_element
        pipeline_string = 'shmsrc is-live=true typefind=true do-timestamp=true socket-path=%s ! video/x-raw,format=BGRA,width=1280,height=720,framerate=25/1 ! ' % shm_video_path

        pipeline_string += self.default_video_pipeline_string_end()
        pipeline_string += ' shmsrc socket-path=%s !  audio/x-raw,channels=2,layout=interleaved,rate=48000,format=S16LE ' % shm_audio_path

        pipeline_string += self.default_audio_pipeline_string_end()
        self.create_pipeline_from_string(pipeline_string)
        self.final_video_tee = self.pipeline.get_by_name('final_video_tee')
        self.final_audio_tee = self.pipeline.get_by_name('final_audio_tee')


        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.enable_sync_message_emission()
        self.bus.connect("message", self.on_message)
        self.logger.info('SHM video source ' + self.uriVideo + ' audio source ' +  self.uriAudio)

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            print('EOS')
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            error="Error: %s" % err, debug
            #print("ERROR:" + str(error))
            self.logger.error(debug)
            self.handle_msg(debug)

    def handle_msg(self, msg):
        if msg.find("Control socket has closed") != -1:
            print('Control socket has closed')
            self.pipeline.set_state(Gst.State.PLAYING)
            #time.sleep(.3)
        elif msg.find("Could not open socket"):
            print('Could not open socket')
            self.pipeline.set_state(Gst.State.PLAYING)
        else:
            print('Unknown error' + msg)

