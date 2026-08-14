"""Carbon footprint tracking for the model runs, via CodeCarbon.

https://codecarbon.io/ - measures the energy drawn by the CPU, RAM and GPUs of
the machine running the process and converts it to CO2 equivalent using the
carbon intensity of the local grid. Install with:

    pip install codecarbon

Only the open models are measured. `gemini`, `chatgpt` and `amalia` do their
inference on someone else's hardware, so a tracker here would record the cost of
this process idling on an HTTP response and report it as the model's footprint -
worse than reporting nothing, because it looks like a measurement.

Every run appends one row to a single `emissions.csv`, tagged with a
`project_name` that identifies the pipeline, language, model and temperature, so
the document-level and sentence-level footprints of the same model can be
compared directly. Note that a resumed run only measures the requests it
actually issues: answers already on disk cost nothing to reuse.
"""

import logging
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
EMISSIONS_PATH = ROOT / "results" / "emissions"
EMISSIONS_FILE = "emissions.csv"

# Models whose inference is remote: nothing about their footprint is observable
# from this machine.
HOSTED_MODELS = {"gemini", "chatgpt", "amalia"}


def run_name(mode: str, language: str, mid: str, temp: float) -> str:
    """The `project_name` recorded in `emissions.csv` for one run.

    Args:
        mode: Which pipeline is running, e.g. "test" or "sentence_level".
        language: Corpus language.
        mid: Model id.
        temp: Sampling temperature.

    Returns:
        A pipe-separated tag, e.g. `sentence_level|english|qwen3_14b|temp0.3`.
    """
    return f"{mode}|{language}|{mid}|temp{temp}"


@contextmanager
def track_emissions(
    mid: str,
    name: str,
    output_dir: Path = EMISSIONS_PATH,
    measure_power_secs: float = 30.0,
):
    """Measure the energy the enclosed block draws, if `mid` runs locally.

    Never raises on account of the tracking itself: a missing package, an
    unsupported power interface or a failed reading degrades to an untracked run
    with a log line, because losing a multi-hour generation run to a telemetry
    problem is far more costly than losing the measurement. Exceptions from the
    enclosed block itself propagate as usual, and the tracker is still stopped.

    Args:
        mid: Model id, used to decide whether tracking is meaningful.
        name: `project_name` for the row, e.g. from `run_name`.
        output_dir: Directory holding the shared `emissions.csv`.
        measure_power_secs: Sampling period of the power readings.

    Yields:
        The `EmissionsTracker`, or None when the run is not being tracked.
    """
    if mid in HOSTED_MODELS:
        logger.info(f"Emissions tracking skipped: {mid} runs remotely.")
        yield None
        return

    try:
        from codecarbon import EmissionsTracker
    except ImportError:
        logger.warning(
            "codecarbon is not installed, running untracked. "
            "Install it with: pip install codecarbon"
        )
        yield None
        return

    output_dir = Path(output_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        tracker = EmissionsTracker(
            project_name=name,
            output_dir=str(output_dir),
            output_file=EMISSIONS_FILE,
            measure_power_secs=measure_power_secs,
            log_level="warning",
        )
        tracker.start()
    except Exception:
        logger.exception("Could not start the emissions tracker, running untracked.")
        yield None
        return

    logger.info(f"Tracking emissions for {name} -> {output_dir / EMISSIONS_FILE}")
    try:
        yield tracker
    finally:
        try:
            emissions = tracker.stop()
            data = getattr(tracker, "final_emissions_data", None)
            energy = getattr(data, "energy_consumed", None)
            duration = getattr(data, "duration", None)
            logger.info(
                f"{name}: {emissions:.6f} kg CO2eq"
                + (f", {energy:.6f} kWh" if energy is not None else "")
                + (f", {duration:.0f} s" if duration is not None else "")
            )
        except Exception:
            logger.exception("Could not stop the emissions tracker cleanly.")
