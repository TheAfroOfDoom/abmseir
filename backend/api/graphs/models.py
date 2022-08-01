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

    def __str__(self):
        """Converts print output of Graph models from e.g. `"Complete ..."` to `"Complete graph ..."`"""
        return (
            super()
            .__str__()
            .replace(self.__class__.__name__, f"{self.__class__.__name__} graph")
        )

    class Meta(_GraphModel.Meta):
        abstract = True
        ordering = ["-order"]


class Circulant(Graph):
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
        ordering = ["-order", "-jumps"]


class Complete(Graph):
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
