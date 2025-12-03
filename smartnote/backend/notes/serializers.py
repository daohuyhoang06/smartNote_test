import requests
import re
import threading
from rest_framework import serializers
from api_mazii.views import searchWord
from api_mazii.views import searchKanji
from rest_framework.test import APIRequestFactory
from .models import Note, Topic, Voca, VocaTopic, VocaDetail

from django.db import transaction
from notes.tasks import sync_and_generate_exercises_task

class NoteSerializer(serializers.ModelSerializer):
    topics_data = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ['id', 'created_at', 'updated_at', 'topics_data']

    def get_topics_data(self, obj):
        return [
            {
                "title": topic.title,
                # nối tất cả voca trong topic thành 1 string "学校、先生、学生"
                "vocas": ", ".join([vt.voca.word for vt in topic.voca_topics.all()])
            }
            for topic in obj.topics.all()
        ]

class TopicSerializer(serializers.ModelSerializer):
     # nhập vào là string, ví dụ: "学校,先生,学生"
    words = serializers.CharField(required=False, allow_blank=True, write_only=True)
    vocas = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Topic
        fields = ['id', 'title', 'words', 'vocas', 'created_at', 'updated_at']

    def validate(self, attrs):
        note = self.context['request'].user.note
        title = attrs.get('title')

        if Topic.objects.filter(note=note, title=title).exists():
            raise serializers.ValidationError({
                "title": ["Title already exists in this note."]
            })
        
        return attrs


    def get_vocas(self, obj):
        words = [vt.voca.word for vt in obj.voca_topics.all()]
        return "、".join(words) if words else ""

    def _process_vocas(self, topic, words_str):
        if not words_str:
            return []

        factory = APIRequestFactory()
        words = [w.strip() for w in re.split(r"[、,]", words_str) if w.strip()]
        details = []

        for w in words:
            voca, _ = Voca.objects.get_or_create(word=w)
            voca_topic, _ = VocaTopic.objects.get_or_create(topic=topic, voca=voca)

            try:
                request = factory.get(f"/api/search/word/{w}/")
                response = searchWord(request, pk=w)
                if hasattr(response, "status_code") and response.status_code == 200:
                    results = response.data
                    if isinstance(results, list):
                        for item in results[:4]:
                            detail = self._save_voca_detail(voca_topic, item)
                            if detail:   # chỉ append nếu có object
                                details.append(detail)
            except Exception as e:
                print(f"[WARN] Lỗi lấy dữ liệu cho '{w}': {e}")

        return details

    
    def _save_voca_detail(self, voca_topic, item):
        word_text = item.get("word", "")

        has_kanji = bool(re.search(r"[\u4e00-\u9fff]", word_text))
        has_katakana = bool(re.search(r"[\u30A0-\u30FF]", word_text))
        has_hiragana = bool(re.fullmatch(r"[\u3040-\u309F]+", word_text))

        kanji = word_text if has_kanji else ""
        katakana = word_text if has_katakana else ""
        hiragana = word_text if has_hiragana else ""

        # --- Lấy level của từng ký tự kanji ---
        level = None
        if kanji:
            levels = []
            for char in kanji:
                if re.match(r"[\u4e00-\u9fff]", char):
                    try:
                        req = APIRequestFactory().get(f"/api/search/kanji/{char}/")
                        resp = searchKanji(req, pk=char)
                        if hasattr(resp, "status_code") and resp.status_code == 200:
                            data = resp.data
                            if isinstance(data, list) and data:
                                meaning = data[0].get("meaning")
                                if meaning:
                                    lv = meaning.get("level")
                                    if isinstance(lv, list) and lv:
                                        levels.append(lv[0])
                                    elif isinstance(lv, str):
                                        levels.append(lv)
                    except Exception:
                        pass
            if levels:
                order = {"N5": 1, "N4": 2, "N3": 3, "N2": 4, "N1": 5}
                level = max(levels, key=lambda x: order.get(x, 0))

        return VocaDetail.objects.create(
            voca_topic=voca_topic,
            kanji=kanji,
            katakana=katakana,
            hiragana=hiragana,
            phonetic=item.get("phonetic", ""),
            meaning=item.get("short_mean", ""),
            example=str(item.get("examples", {})),
            level=level or "N4",
        )
        

    def create(self, validated_data):
        words = validated_data.pop("words", "")
        user = self.context['request'].user
        note, _ = Note.objects.get_or_create(user=user)
        validated_data['note'] = note

        topic = super().create(validated_data)
        voca_details = self._process_vocas(topic, words)

        # if voca_details:
        #     ids = [d.id for d in voca_details]

        #     def run_after_commit():
        #         sync_and_generate_exercises_task.delay(ids)   # gọi task Celery

        #     transaction.on_commit(run_after_commit)
        return topic


class VocaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voca
        fields = ['id', 'word']

class VocaTopicSerializer(serializers.ModelSerializer):
    # lồng thông tin từ Voca và Topic
    word = VocaSerializer(read_only=True)
    word_id = serializers.PrimaryKeyRelatedField(
        queryset=Voca.objects.all(),
        source="word",
        write_only=True
    )
    topic_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = VocaTopic
        fields = ['id', 'topic_id', 'word', 'word_id']

class VocaDetailSerializer(serializers.ModelSerializer):
    # Lấy trực tiếp từ chữ trong bảng Voca
    word = serializers.CharField(source="voca_topic.voca.word", read_only=True)

    class Meta:
        model = VocaDetail
        fields = ["id", "word", "kanji", "katakana", "hiragana", "phonetic", "meaning", "example", "level", "created_at"]