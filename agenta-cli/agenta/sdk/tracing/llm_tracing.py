import os
from uuid import uuid4

import traceback
from threading import Lock
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from agenta.sdk.tracing.tracing_context import tracing_context
from agenta.sdk.tracing.logger import llm_logger as logging
from agenta.sdk.tracing.tasks_manager import TaskQueue
from agenta.client.backend.client import AsyncAgentaApi
from agenta.client.backend.client import AsyncObservabilityClient
from agenta.client.backend.types.create_span import (
    CreateSpan,
    LlmTokens,
    SpanStatusCode,
)

from bson.objectid import ObjectId

VARIANT_TRACKING_FEATURE_FLAG = False

from agenta.sdk.utils.debug import debug, DEBUG, SHIFT


logging.setLevel("DEBUG")


class SingletonMeta(type):
    """
    Thread-safe implementation of Singleton.
    """

    _instances = {}  # type: ignore

    # We need the lock mechanism to synchronize threads \
    # during the initial access to the Singleton object.
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """
        Ensures that changes to the `__init__` arguments do not affect the
        returned instance.

        Uses a lock to make this method thread-safe. If an instance of the class
        does not already exist, it creates one. Otherwise, it returns the
        existing instance.
        """

        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class Tracing(metaclass=SingletonMeta):
    """The `Tracing` class is an agent for LLM tracing with specific initialization arguments.

    __init__ args:
        host (str): The URL of the backend host
        api_key (str): The API Key of the backend host
        tasks_manager (TaskQueue): The tasks manager dedicated to handling asynchronous tasks
        max_workers (int): The maximum number of workers to run tracing
    """

    def __init__(
        self,
        host: str,
        app_id: str,
        api_key: Optional[str] = None,
        max_workers: Optional[int] = None,
    ):
        self.host = host + "/api"
        self.api_key = api_key if api_key is not None else ""
        self.app_id = app_id
        self.tasks_manager = TaskQueue(
            max_workers if max_workers else 4, logger=logging
        )
        self.baggage = None

    @property
    def client(self) -> AsyncObservabilityClient:
        """Initialize observability async client

        Returns:
            AsyncObservabilityClient: async client
        """

        return AsyncAgentaApi(
            base_url=self.host, api_key=self.api_key, timeout=120  # type: ignore
        ).observability

    ### --- API --- ###

    @debug()
    def get_context(self):
        tracing = tracing_context.get()

        return tracing

    @debug()
    def update_baggage(
        self,
        attributes: Dict[str, Any] = {},
    ):
        if self.baggage is None:
            self.baggage = {}

        for key, value in attributes.items():
            self.baggage[key] = value

    @debug()
    def open_trace(
        self,
        span: Optional[CreateSpan],
        config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        tracing = tracing_context.get()

        tracing.trace_id = self._create_trace_id()

        logging.info(f"Opening trace {tracing.trace_id}")

        if span is not None:
            ### --- TO BE CLEANED --- >>>
            span.environment = (
                self.baggage.get("environment")
                if self.baggage is not None
                else os.environ.get("environment", "unset")
            )

            span.config = (
                self.baggage.get("config")
                if not config and self.baggage is not None
                else None
            )
            if VARIANT_TRACKING_FEATURE_FLAG:
                # TODO: we should get the variant_id and variant_name (and environment) from the config object
                span.variant_id = config.variant_id  # type: ignore
                span.variant_name = (config.variant_name,)  # type: ignore
            ### --- TO BE CLEANED --- <<<

        logging.info(f"Opened  trace {tracing.trace_id}")

    @debug()
    def set_trace_tags(self, tags: List[str]) -> None:
        tracing = tracing_context.get()

        tracing.trace_tags.extend(tags)

    @debug()
    def close_trace(self) -> None:
        """
        Ends the active trace and sends the recorded spans for processing.

        Args:
            parent_span (CreateSpan): The parent span of the trace.

        Raises:
            RuntimeError: If there is no active trace to end.

        Returns:
            None
        """
        tracing = tracing_context.get()

        logging.info(f"Closing trace {tracing.trace_id}")

        trace_id = tracing.trace_id

        if tracing.trace_id is None:
            logging.error("Cannot close trace, no trace to close")
            return

        if not self.api_key:
            logging.error("No API key")
        else:
            self._process_spans()

        self._clear_trace_tags()

        logging.info(f"Closed  trace {trace_id}")

    @debug()
    def open_span(
        self,
        name: str,
        spankind: str,
        input: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> CreateSpan:
        tracing = tracing_context.get()

        span_id = self._create_span_id()

        logging.info(f"Opening span  {span_id} {spankind.upper()}")

        ### --- TO BE CLEANED --- >>>
        span = CreateSpan(
            id=span_id,
            inputs=input,
            name=name,
            app_id=self.app_id,
            config=config,
            spankind=spankind.upper(),
            attributes={},
            status=SpanStatusCode.UNSET.value,
            start_time=datetime.now(timezone.utc),
            outputs=None,
            tags=None,
            user=None,
            end_time=None,
            tokens=None,
            cost=None,
            token_consumption=None,
            parent_span_id=None,
        )

        if tracing.trace_id is None:
            self.open_trace(span, config)
        else:
            span.parent_span_id = tracing.active_span.id  # type: ignore

        tracing.push(span)
        ### --- TO BE CLEANED --- <<<

        logging.info(f"Opened  span  {span_id} {spankind.upper()}")

        return span

    @debug(req=True)
    def set_attributes(
        self,
        attributes: Dict[str, Any] = {},
    ) -> None:
        """
        Set attributes for the active span.

        Args:
            attributes (Dict[str, Any], optional): A dictionary of attributes to set. Defaults to {}.
        """

        tracing = tracing_context.get()

        if tracing.active_span is None:
            logging.error(f"Cannot set attributes ({set(attributes)}), no active span")
            return

        logging.info(
            f"Setting span  {tracing.active_span.id} {tracing.active_span.spankind.upper()} attributes={attributes}"
        )

        for key, value in attributes.items():
            tracing.active_span.attributes[key] = value  # type: ignore

    @debug()
    def set_status(self, status: str) -> None:
        """
        Set status for the active span.

        Args:
            status: Enum ( UNSET, OK, ERROR )
        """
        tracing = tracing_context.get()

        if tracing.active_span is None:
            logging.error(f"Cannot set status ({status}), no active span")
            return

        logging.info(
            f"Setting span  {tracing.active_span.id} {tracing.active_span.spankind.upper()} status={status}"
        )

        tracing.active_span.status = status

    @debug()
    def close_span(self, outputs: Dict[str, Any]) -> None:
        """
        Ends the active span, if it is a parent span, ends the trace too.

        Args:
            outputs (Dict[str, Any]): A dictionary containing the outputs of the span.
                It should have the following keys:
                - "message" (str): The message output of the span.
                - "cost" (Optional[Any]): The cost of the span.
                - "usage" (Optional[Any]): The number of tokens used in the span.

        Raises:
            ValueError: If there is no active span to end.

        Returns:
            None
        """

        tracing = tracing_context.get()

        if tracing.active_span is None:
            logging.error("Cannot close span, no active span")

        span_id = tracing.active_span.id
        spankind = tracing.active_span.spankind

        logging.info(f"Closing span  {span_id} {spankind}")

        ### --- TO BE CLEANED --- >>>
        tracing.active_span.end_time = datetime.now(timezone.utc)

        tracing.active_span.outputs = outputs

        if tracing.active_span.spankind.upper() in [
            "LLM",
            "RETRIEVER",
        ]:  # TODO: Remove this whole part. Setting the cost should be done through set_span_attribute
            self._update_span_cost(tracing.active_span, outputs.get("cost", None))
            self._update_span_tokens(tracing.active_span, outputs.get("usage", None))

        active_span_parent_id = tracing.active_span.parent_span_id

        if active_span_parent_id is not None:
            parent_span = tracing.spans[active_span_parent_id]
            self._update_span_cost(parent_span, tracing.active_span.cost)
            self._update_span_tokens(parent_span, tracing.active_span.tokens)
            tracing.active_span = parent_span
        ### --- TO BE CLEANED --- <<<

        logging.info(f"Closed  span  {span_id} {spankind}")

    def store_locals(self, locals: Dict[str, Any] = {}):
        attributes = {f"locals.{k}": v for k, v in locals.items()}

        self.set_attributes(attributes=attributes)

    def dump_trace(self):
        try:
            trace = dict()

            tracing = tracing_context.get()

            trace["trace_id"] = tracing.trace_id

            for span in tracing.spans.values():
                if span.parent_span_id is None:
                    trace["cost"] = span.cost
                    trace["tokens"] = span.tokens
                    trace["latency"] = (span.end_time - span.start_time).total_seconds()

            spans = self.dump_spans(tracing.tree)

            if spans is not None:
                trace["spans"] = spans

        except Exception as e:
            logging.error(e)
            logging.error(traceback.format_exc())

        return trace

    def dump_spans(self, tree):
        try:
            spans = dict()
            count = dict()

            tracing = tracing_context.get()

            for idx in tree.keys():
                key = tracing.spans[idx].name
                count[key] = count.get(key, 0) + 1

            while len(tree.keys()):
                id, children = tree.popitem(last=False)

                key = tracing.spans[id].name
                # key = tracing.spans[id].attributes["block"] if ("block" in tracing.spans[id].attributes) else tracing.spans[id].name

                span = {
                    "start_time": tracing.spans[id].start_time.isoformat(),
                    "end_time": tracing.spans[id].end_time.isoformat(),
                    "inputs": {k:repr(v) for (k,v) in tracing.spans[id].inputs.items()},
                    "locals": {k.replace("locals.", ""):repr(v) for k,v in tracing.spans[id].attributes.items() if k.startswith("locals.")},
                    "outputs": {k:repr(v) for (k,v) in tracing.spans[id].outputs.items()},
                }

                children_spans = self.dump_spans(children)

                if children_spans:
                    span.update({"spans": children_spans})

                if count[key] > 1:
                    if key not in spans:
                        spans[key] = list()

                    spans[key].append(span)
                else:
                    spans[key] = span

        except Exception as e:
            logging.error(e)
            logging.error(traceback.format_exc())

        return spans

    def flush_spans(self) -> None:
        self.close_trace()

    ### --- Legacy API --- ###

    def start_trace(
        self,
        span: CreateSpan,
        config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:  # Legacy
        self.open_trace(span, config, **kwargs)

    def end_trace(self, parent_span: CreateSpan) -> None:  # Legacy
        self.close_trace()

    def start_span(
        self,
        name: str,
        spankind: str,
        input: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> CreateSpan:  # Legacy
        return self.open_span(name, spankind, input, config, **kwargs)

    def update_span_status(self, _: CreateSpan, status: str) -> None:  # Legacy
        self.update_span_status(status)

    def set_span_attribute(
        self,
        attributes: Dict[str, Any] = {},
    ) -> None:  # Legacy
        self.set_attributes(attributes)

    def end_span(self, outputs: Dict[str, Any]) -> None:  # Legacy
        self.close_span(outputs)

    ### --- Helper Functions --- ###

    def _create_trace_id(self) -> str:
        """Creates a 32HEXDIGL / ObjectId ID for the trace object.

        Returns:
            str: stringify oid of the trace
        """

        # return uuid4().hex
        return str(ObjectId())

    def _clear_trace_tags(self) -> None:
        tracing = tracing_context.get()

        tracing.trace_tags.clear()

    def _create_span_id(self) -> str:
        """Creates a  16HEXDIGL / ObjectId ID for the span object.

        Returns:
            str: stringify oid of the span
        """

        # return uuid4().hex[:16]
        return str(ObjectId())

    def _process_spans(self) -> None:
        tracing = tracing_context.get()

        spans = list(tracing.spans.values())

        logging.info(f"Sending trace {tracing.trace_id} spans={len(spans)} ")

        self.tasks_manager.add_task(
            tracing.trace_id,
            "send-trace",
            # mock_create_traces(
            self.client.create_traces(
                trace=tracing.trace_id, spans=spans  # type: ignore
            ),
            self.client,
        )

        logging.info(f"Sent    trace {tracing.trace_id}")

    def _update_span_cost(self, span: CreateSpan, cost: Optional[float]) -> None:
        if span is not None and cost is not None and isinstance(cost, float):
            if span.cost is None:
                span.cost = cost
            else:
                span.cost += cost

    def _update_span_tokens(self, span: CreateSpan, tokens: Optional[dict]) -> None:
        if isinstance(tokens, LlmTokens):
            tokens = tokens.dict()
        if span is not None and tokens is not None and isinstance(tokens, dict):
            if span.tokens is None:
                span.tokens = LlmTokens(**tokens)
            else:
                span.tokens.prompt_tokens += tokens["prompt_tokens"]
                span.tokens.completion_tokens += tokens["completion_tokens"]
                span.tokens.total_tokens += tokens["total_tokens"]
