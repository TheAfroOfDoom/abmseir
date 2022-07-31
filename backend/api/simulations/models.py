"""Contains models related to running simulations"""

import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core import exceptions, validators
from django.db import models


class _SimulationModel(models.Model):
    """All models relating to simulations have a UUID primary key

    Also defines their `__hash__` method based on their uniquely-identifying
    primary key `id`
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __hash__(self):
        return hash(self.id)

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
    """List of defined parameter configurations referenced by
    simulation instances
    """

    # Fields may be null to indicate old parameter-rows not containing
    # newly added parameters, but all parameters must be provided by new
    # `Instance` requests
    #
    # e.g., if you add a new parameter `custom_param`, all old `Parameters`
    # rows will not have that value defined (prior simulation instances did
    # not utilize it), so it will be `null`; all new instances must specify
    # it though
    time_horizon = models.PositiveIntegerField(blank=False, null=True)
    r0 = models.IntegerField(blank=False, null=True)
    sample_size = models.PositiveIntegerField(
        blank=False,
        null=True,
        validators=[validators.MinValueValidator(1)],
    )

    class Meta:
        ordering = ("id",)
        unique_together = ("time_horizon", "r0", "sample_size")


class Instance(_SimulationModel):
    """A simulation that was ran with defined parameters."""

    parameters = models.ForeignKey(Parameters, on_delete=models.CASCADE)
    timestamp_start = models.DateTimeField(auto_now_add=True, editable=False)
    timestamp_end = models.DateTimeField(null=True)
    cancelled = models.BooleanField(default=False)

    graph_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    graph_id = models.UUIDField()
    graph = GenericForeignKey("graph_type", "graph_id")

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
