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


ALL_PARAMETER_OPTIONS = {
    "blank": False,
    "null": True,
}


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

    # Note that `models.PositiveIntegerField` includes 0 in its domain
    # TODO: add simulation-logical validation for each field, prob with `clean()`
    sample_size = models.PositiveIntegerField(
        validators=[validators.MinValueValidator(1)],
        **ALL_PARAMETER_OPTIONS,
    )

    initial_infected_count = models.PositiveIntegerField(**ALL_PARAMETER_OPTIONS)

    cycles_per_day = models.PositiveIntegerField(
        validators=[validators.MinValueValidator(1)], **ALL_PARAMETER_OPTIONS
    )
    time_horizon = models.PositiveIntegerField(**ALL_PARAMETER_OPTIONS)

    exogenous_amount = models.PositiveIntegerField(**ALL_PARAMETER_OPTIONS)
    exogenous_frequency = models.PositiveIntegerField(**ALL_PARAMETER_OPTIONS)

    r0 = models.PositiveIntegerField(**ALL_PARAMETER_OPTIONS)

    time_to_infection_mean = models.PositiveIntegerField(**ALL_PARAMETER_OPTIONS)
    time_to_infection_min = models.PositiveIntegerField(**ALL_PARAMETER_OPTIONS)

    time_to_recovery_mean = models.PositiveIntegerField(**ALL_PARAMETER_OPTIONS)
    time_to_recovery_min = models.PositiveIntegerField(**ALL_PARAMETER_OPTIONS)

    symptoms_probability = models.DecimalField(
        max_digits=9,
        decimal_places=9,
        **ALL_PARAMETER_OPTIONS,
    )
    death_probability = models.DecimalField(
        max_digits=9,
        decimal_places=9,
        **ALL_PARAMETER_OPTIONS,
    )

    test_specificity = models.DecimalField(
        max_digits=9,
        decimal_places=9,
        **ALL_PARAMETER_OPTIONS,
    )
    test_sensitivity = models.DecimalField(
        max_digits=9,
        decimal_places=9,
        **ALL_PARAMETER_OPTIONS,
    )
    test_cost = models.PositiveIntegerField(**ALL_PARAMETER_OPTIONS)
    test_results_delay = models.PositiveIntegerField(**ALL_PARAMETER_OPTIONS)
    test_rate = models.PositiveIntegerField(**ALL_PARAMETER_OPTIONS)

    class Meta:
        ordering = ("id",)
        unique_together = (
            "sample_size",
            "initial_infected_count",
            "cycles_per_day",
            "time_horizon",
            "exogenous_amount",
            "exogenous_frequency",
            "r0",
            "time_to_infection_mean",
            "time_to_infection_min",
            "time_to_recovery_mean",
            "time_to_recovery_min",
            "symptoms_probability",
            "death_probability",
            "test_specificity",
            "test_sensitivity",
            "test_cost",
            "test_results_delay",
            "test_rate",
        )


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
