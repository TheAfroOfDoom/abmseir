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


MAX_RUNNING_SAMPLES = 2


class InstanceSamples:
    """Tracks which samples of a simulation `Instance` have completed
    running and which samples still need to be ran.
    """

    def __init__(self, instance: Instance, instance_serializer: InstanceSerializer):
        self.instance = instance
        self.instance_serializer = instance_serializer
        self.samples_complete: set[Sample] = set()
        self.samples_running: set[Sample] = set()
        self.queue: set[SampleSerializer] = set()

        parameters: Parameters = self.instance.parameters
        self.total: int = parameters.sample_size

        self._generate_samples()

    def _generate_samples(self):
        for idx in range(self.total):
            # Create new sample serializer
            sample_serializer = SampleSerializer(data={"instance": self.instance.id})
            sample_serializer.is_valid(raise_exception=True)

            # Track samples to be ran
            self.queue.add(sample_serializer)

            # Start a maximum of `MAX_RUNNING_SAMPLES` sample threads
            if idx < MAX_RUNNING_SAMPLES:
                self.run_sample()

    def run_sample(self):
        # TODO: re-use thread instead of creating new one? unsure (pros/cons)
        sample_serializer = self.queue.pop()
        sample = (
            sample_serializer.save()
        )  # Save new sample to database when we start running it

        def sample_callback():
            """Runs upon sample completion"""
            self.complete_sample(sample)

        # Start thread to run sample simulation
        sample_thread = threading.Thread(
            target=simulate,
            args=[
                sample,
                sample_serializer,
                sample_callback,
            ],
        )
        sample_thread.start()
        self.samples_running.add(sample)

    def complete_sample(self, sample: Sample):
        """Mark a `Sample` as complete by moving it from the
        incomplete set to the complete set

        Runs `self.complete()` if all `Sample`s have complewed
        """
        self.samples_running.remove(sample)
        self.samples_complete.add(sample)

        if len(self.samples_complete) == self.total:
            self.complete()
        elif len(self.queue) > 0:
            self.run_sample()

    def complete(self):
        self.instance_serializer.update(
            self.instance, {"timestamp_end": datetime.now(utc)}
        )


def simulate_instance(instance: Instance, serializer: InstanceSerializer):
    """Generates `sample` threads based on inputted simulation parameters,
    and updates the `timestamp_end` upon all `sample`s finishing.
    """

    InstanceSamples(instance, serializer)


def simulate(sample: Sample, serializer: SampleSerializer, callback: Callable):
    time.sleep(5)

    # Update `sample.timestamp_end` upon sample simulation completion
    serializer.update(sample, {"timestamp_end": datetime.now(utc)})

    callback()
