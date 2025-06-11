from rest_framework import serializers
from .models import (
    AnalyseSentiment,
    PredictionPerformance,
    RecommandationFormation,
    OptimisationPlanning
)

class AnalyseSentimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyseSentiment
        fields = '__all__'

class PredictionPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionPerformance
        fields = '__all__'

class RecommandationFormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommandationFormation
        fields = '__all__'

class OptimisationPlanningSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptimisationPlanning
        fields = '__all__'
