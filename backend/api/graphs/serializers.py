"""
Defines how graph views interact with graph models, in addition to:

* gracefully handling unique constraint violations (400 Bad Request)
* providing validation for more complicated graphs (e.g. circulant)
"""
import operator

from django.db import IntegrityError
from rest_framework import serializers

from .models import CirculantGraph, CompleteGraph


class _GraphSerializer(serializers.ModelSerializer):
    """Abstract graph serializer that provides common behavior:
    * defines common exposed fields (`id`, `order`)
    * handles unique constraint violations as HTTP 400s (Bad Request)

    This serializer does not expose raw graph data for network traffic speed reasons
    (see: `_GraphDataSerializer`).
    """

    def save(self, **kwargs):
        """Extend Django's base `ModelSerializer` by returning unique constraint
        violations as HTTP 400s (Bad Request).
        """
        try:
            super().save(**kwargs)
        except IntegrityError as error:
            if "unique constraint" in str(error):
                raise serializers.ValidationError(
                    f"Graph already exists with properties {self.initial_data}"
                )
            raise error

    class Meta:
        fields = (
            "id",
            "order",
        )
        read_only_fields = ("id",)


class _GraphDataSerializer(serializers.ModelSerializer):
    """Abstract graph data serializer that defines common exposed fields (`id`, `data`)."""

    class Meta:
        fields = (
            "id",
            "data",
            "order",
        )
        read_only_fields = fields


class CompleteGraphSerializer(_GraphSerializer):
    """Graph serialization for complete graphs.

    No special behavior."""

    class Meta(_GraphSerializer.Meta):
        model = CompleteGraph
        fields = _GraphSerializer.Meta.fields


class CompleteGraphDataSerializer(_GraphDataSerializer):
    """Graph data serialization for complete graphs."""

    class Meta(_GraphDataSerializer.Meta):
        model = CompleteGraph
        fields = _GraphDataSerializer.Meta.fields


class CirculantGraphSerializer(_GraphSerializer):
    """Graph serialization for circulant graphs.

    Validates `jumps` inputs to ensure that it is an array of positive integers that are:
    * distinct
    * increasing
    * <= half of the graph's `order`
    """

    class Meta(_GraphSerializer.Meta):
        model = CirculantGraph
        fields = (*_GraphSerializer.Meta.fields, "jumps")

    def validate_jumps(self, jumps):
        """Validate `jumps` inputs to ensure that it is an array of (positive) integers that are:
        * distinct
        * increasing
        * <= half of the graph's `order`
        """
        if len(set(jumps)) != len(jumps):
            raise serializers.ValidationError(
                "Array of jumps must not contain duplicates", code="jumps_duplicates"
            )

        order = operator.itemgetter("order")(self.initial_data)
        if max(jumps) > self.initial_data["order"] // 2:  # type:ignore
            raise serializers.ValidationError(
                f"Each jump must be less than or equal to half of the order ({order})",
                code="jumps_max_value",
            )

        prev = jumps[0]
        for jump in jumps[1:]:
            if jump < prev:
                raise serializers.ValidationError(
                    "Array of jumps must be in increasing order",
                    code="jumps_decreasing",
                )
            prev = jump

        return jumps


class CirculantGraphDataSerializer(_GraphDataSerializer):
    """Graph data serialization for circulant graphs."""

    class Meta(_GraphDataSerializer.Meta):
        model = CirculantGraph
        fields = (*_GraphDataSerializer.Meta.fields, "jumps")
