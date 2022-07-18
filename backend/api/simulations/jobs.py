"""
Asynchronous jobs for views/serializers to start running under
specific circumstances.
"""

from datetime import datetime
import threading
import time
from typing import Callable
from pytz import utc

from .models import Instance, Parameters, Sample
from .serializers import InstanceSerializer, SampleSerializer


class InstanceSamples:
    def __init__(
        self,
        total_sample_count: int,
        instance: Instance,
        instance_serializer: InstanceSerializer,
    ):
        self.instance = instance
        self.instance_serializer = instance_serializer
        self.sample_statuses: dict[str, bool] = {}
        self.samples_complete = 0
        self.total_sample_count = total_sample_count

    def complete_sample(self, sample: Sample):
        self.samples_complete += 1
        self.sample_statuses[sample.id] = True

        if self.samples_complete == self.total_sample_count:
            self.complete()

    def complete(self):
        self.instance_serializer.update(
            self.instance, {"timestamp_end": datetime.now(utc)}
        )


def simulate_instance(instance: Instance, serializer: InstanceSerializer):
    """Generates `sample` threads based on inputted simulation parameters,
    and updates the `timestamp_end` upon all `sample`s finishing.
    """

    parameters: Parameters = instance.parameters
    sample_size = parameters.sample_size

    samples = InstanceSamples(sample_size, instance, serializer)

    def sample_callback():
        samples.complete_sample(sample)

    # Generate samples as defined by `sample_size`
    for idx in range(sample_size):
        # Save new sample to database
        sample_serializer = SampleSerializer(data={"instance": instance.id})
        sample_serializer.is_valid(raise_exception=True)
        sample = sample_serializer.save()

        samples.sample_statuses[sample.id] = False

        # Start thread to run sample simulation
        sample_thread = threading.Thread(
            target=simulate_sample,
            args=[
                sample,
                sample_serializer,
                sample_callback,
            ],
        )
        sample_thread.start()


def simulate_sample(sample: Sample, serializer: SampleSerializer, callback: Callable):
    time.sleep(5)

    # Update `sample.timestamp_end` upon sample simulation completion
    serializer.update(sample, {"timestamp_end": datetime.now(utc)})

    callback()
