from rest_framework import serializers
from .models import Word, Kanji, Example


class KanjiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kanji
        fields = '__all__'


class ExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Example
        fields = ['id', 'transcription', 'content', 'mean']


class WordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Word
        fields = '__all__'

