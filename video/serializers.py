from rest_framework import serializers
from moviepy.editor import VideoFileClip
import base64
import tempfile
import os

from base64_conversion.conversion import Base64VideoField


class VideoCutSerializer(serializers.Serializer):
    video = Base64VideoField()
    start = serializers.IntegerField()
    end = serializers.IntegerField()

    def validate(self, attrs):
        if attrs['end'] <= attrs['start']:
            raise serializers.ValidationError("The time frame is not correct")
        return attrs

    def cut(self):
        video_file = self.validated_data.get('video')
        start = self.validated_data.get('start')
        end = self.validated_data.get('end')

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_input:
            temp_input.write(video_file.read())
            temp_input.flush()

            clip = VideoFileClip(temp_input.name)

            cut_video = clip.subclip(start, end)

            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_output:
                cut_video.write_videofile(temp_output.name, codec='libx264', audio_codec='aac')

                temp_output.seek(0)
                with open(temp_output.name, 'rb') as output_file:
                    cut_video_base64 = base64.b64encode(output_file.read()).decode('utf-8')

        os.remove(temp_input.name)
        os.remove(temp_output.name)

        return f'data:video/mp4;base64,{cut_video_base64}'


