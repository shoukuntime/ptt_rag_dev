from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class ArticleListRequestSerializer(serializers.Serializer):
    author_name = serializers.CharField(help_text="作者名稱", write_only=True, required=False)
    board_name = serializers.CharField(help_text="看板名稱", write_only=True, required=False)
    start_date = serializers.DateField(help_text="起始日期", write_only=True, required=False)
    end_date = serializers.DateField(help_text="結束日期", write_only=True, required=False)
    limit = serializers.IntegerField(help_text="每頁返回的筆數 (預設 50)", write_only=True, default=50, min_value=1)
    offset = serializers.IntegerField(help_text="從第幾筆開始 (預設 0)", write_only=True, required=False, min_value=0)

class QueryRequestSerializer(serializers.Serializer):
    question = serializers.CharField(help_text="查詢內容", required=True, max_length=100, min_length=1)
    top_k = serializers.IntegerField(help_text="控制段落的查詢數量 (預設 3)", default=3, write_only=True, min_value=1, max_value=10)

    answer = serializers.CharField(required=False, read_only=True)
    related_articles = ArticleSerializer(many=True, read_only=True)