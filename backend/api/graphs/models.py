"""Contains models for Graph objects"""

import uuid

from django.contrib.postgres import fields
from django.core import validators
from django.db import models


class _GraphModel(models.Model):
    """All models relating to graphs have a UUID primary key"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Graph(_GraphModel):
    """
    Common properties that all graphs share
    ```
    id: UUID
    data: Blob
    order: int # Positive
    ```
    """

    data = models.BinaryField(editable=False)
    order = models.PositiveIntegerField(validators=[validators.MinValueValidator(1)])
    # owner_id = models.ForeignKey(to=Users, on_delete=models.CASCADE)

    class Meta(_GraphModel.Meta):
        abstract = True
        ordering = ["-order"]


class CirculantGraph(Graph):
    """
    Database representation of the circulant graph

    Properties:
    ```
    order: int        # Positive
    jumps: list[int]  # Positive, distinct, increasing integers
    ```

    Generator: :func:`~abseir.grapher.circulant_graph`
    (https://en.wikipedia.org/wiki/Circulant_graph)
    """

    jumps = fields.ArrayField(
        models.PositiveIntegerField(
            validators=[
                validators.MinValueValidator(1),
            ]
        )
    )

    class Meta(Graph.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["order", "jumps"], name="AK_graph_circulant_properties"
            )
        ]
        db_table = "graphs_circulant"
        ordering = ["-order", "-jumps"]


class CompleteGraph(Graph):
    """
    Database representation of the complete graph

    Properties:
    ```
    order: int  # Positive
    ```

    Generator: :func:`~abseir.grapher.complete_graph`
    (https://en.wikipedia.org/wiki/Complete_graph)
    """

    class Meta(Graph.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["order"], name="AK_graph_complete_properties"
            )
        ]
        db_table = "graphs_complete"
