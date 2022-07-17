"""Contains models related to running simulations"""

import uuid

from django.core import exceptions
from django.db import models


class _SimulationModel(models.Model):
    """All models relating to simulations have a UUID primary key"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
        ordering = ("id",)


class Population(_SimulationModel):
    """All populations a node may belong to"""

    name = models.CharField(max_length=64, unique=True)
    initialism = models.CharField(max_length=8, unique=True)
    description = models.CharField(max_length=256)

    class Meta:
        ordering = ("name",)


class Parameters(_SimulationModel):
    """List of parameters referenced by simulations"""

    time_horizon = models.PositiveIntegerField()
    r0 = models.IntegerField()

    class Meta:
        ordering = ("id",)
        unique_together = ("time_horizon", "r0")


class Instance(_SimulationModel):
    """A simulation that was ran with defined parameters."""

    parameters = models.ForeignKey(Parameters, on_delete=models.CASCADE)
    timestamp_start = models.DateTimeField(auto_now_add=True, editable=False)
    timestamp_end = models.DateTimeField(null=True)
    cancelled = models.BooleanField(default=False)

    def clean(self):
        if self.timestamp_start >= self.timestamp_end:
            raise exceptions.ValidationError("Start time should be before end time")
        return super().clean()

    class Meta:
        constraints = [
            # https://stackoverflow.com/a/62521555/13789724
            models.CheckConstraint(
                check=models.Q(timestamp_start__lte=models.F("timestamp_end")),
                name="CHK_simulation_instance_timestamp_start_lt_timestamp_end",
            ),
        ]
        ordering = ("id",)


class Sample(_SimulationModel):
    """A single run (sample) of a parent simulation instance"""

    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    timestamp_start = models.DateTimeField(auto_now_add=True, editable=False)
    timestamp_end = models.DateTimeField(null=True)


class Data(_SimulationModel):
    """A single data row of a parent sample"""

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    cycle_index = models.PositiveIntegerField()
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    population_size = models.PositiveIntegerField()

    # TODO: maybe add something (`clean`) to check if `population_size`/`cycle_index` are
    # not bigger than their max size(s)
