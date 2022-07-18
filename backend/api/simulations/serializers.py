"""
Defines how simulation views interact with simulation models, in addition to:

* gracefully handling unique constraint violations (400 Bad Request)
"""
from typing import Generic, TypeVar

from django.db import IntegrityError
from rest_framework import serializers

from .models import Data, Instance, Parameters, Population, Sample


M = TypeVar("M")


class _SimulationSerializer(serializers.ModelSerializer, Generic[M]):
    """Abstract simulation model serializer that provides common behavior:
    * defines common exposed fields (`id`)
    * handles unique constraint violations as HTTP 400s (Bad Request)
    """

    def save(self, **kwargs):
        """Extend Django's base `ModelSerializer` by returning unique constraint
        violations as HTTP 400s (Bad Request).
        """
        try:
            model: M = super().save(**kwargs)
            return model
        except IntegrityError as error:
            if "unique constraint" in str(error):
                raise serializers.ValidationError(
                    f"Graph already exists with properties {self.initial_data}"
                )
            raise error

    class Meta:
        model = M
        fields = ("id",)
        read_only_fields = ("id",)


class PopulationSerializer(_SimulationSerializer[Population]):
    """Serialization for simulation populations.

    No special behavior.
    """

    class Meta(_SimulationSerializer[Population].Meta):
        model = Population
        fields = (
            *_SimulationSerializer[Population].Meta.fields,
            "name",
            "initialism",
            "description",
        )


class ParametersSerializer(_SimulationSerializer[Parameters]):
    """Serialization for simulation parameters.

    No special behavior.
    """

    class Meta(_SimulationSerializer[Parameters].Meta):
        model = Parameters
        fields = (
            *_SimulationSerializer[Parameters].Meta.fields,
            "time_horizon",
            "r0",
            "sample_size",
        )


class InstanceSerializer(_SimulationSerializer[Instance]):
    """Serialization for viewing/updating simulation instances.

    Only `timestamp_end` may be updated (once an instance has
    finished simulating).
    """

    class Meta(_SimulationSerializer[Instance].Meta):
        model = Instance
        fields = (
            *_SimulationSerializer[Instance].Meta.fields,
            "parameters",
            "timestamp_start",
            "timestamp_end",
        )
        read_only_fields = (
            *_SimulationSerializer[Instance].Meta.fields,
            "parameters",
            "timestamp_start",
        )


class InstanceCreateSerializer(_SimulationSerializer[Instance]):
    """Serialization for listing/creating simulation instances.

    Only `parameters` may be specified; to edit `timestamp_end`
    after an instance has finished simulating, use
    `InstanceSerializer`.
    """

    class Meta(_SimulationSerializer[Instance].Meta):
        model = Instance
        fields = (
            *_SimulationSerializer[Instance].Meta.fields,
            "parameters",
            "timestamp_start",
            "timestamp_end",
        )
        read_only_fields = (
            *_SimulationSerializer[Instance].Meta.fields,
            "timestamp_start",
            "timestamp_end",
        )


class SampleSerializer(_SimulationSerializer[Sample]):
    """Serialization for simulation instance samples.

    No special behavior.
    """

    class Meta(_SimulationSerializer[Sample].Meta):
        model = Sample
        fields = (
            *_SimulationSerializer[Sample].Meta.fields,
            "instance",
            "timestamp_start",
            "timestamp_end",
        )
        read_only_fields = (
            *_SimulationSerializer[Sample].Meta.fields,
            "timestamp_start",
        )


class DataSerializer(_SimulationSerializer[Data]):
    """Serialization for simulation instance sample data.

    No special behavior.
    """

    class Meta(_SimulationSerializer[Data].Meta):
        model = Data
        fields = (
            *_SimulationSerializer[Data].Meta.fields,
            "sample",
            "timestamp",
            "cycle_index",
            "population",
            "population_size",
        )
        read_only_fields = (
            *_SimulationSerializer[Data].Meta.fields,
            "timestamp",
        )
