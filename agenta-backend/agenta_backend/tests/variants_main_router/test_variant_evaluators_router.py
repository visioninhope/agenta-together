import os
import httpx
import pytest
import asyncio

from agenta_backend.models.db.postgres_engine import db_engine
from agenta_backend.models.api.evaluation_model import EvaluationStatusEnum
from agenta_backend.models.db_models import (
    AppDB,
    TestSetDB,
    AppVariantDB,
    EvaluationDB,
    DeploymentDB,
    EvaluationScenarioDB,
)

from sqlalchemy.future import select
from sqlalchemy.orm import joinedload


# Initialize http client
test_client = httpx.AsyncClient()
timeout = httpx.Timeout(timeout=5, read=None, write=5)

# Set global variables
APP_NAME = "evaluation_in_backend"
ENVIRONMENT = os.environ.get("ENVIRONMENT")
OPEN_AI_KEY = os.environ.get("OPENAI_API_KEY")
if ENVIRONMENT == "development":
    BACKEND_API_HOST = "http://host.docker.internal/api"
elif ENVIRONMENT == "github":
    BACKEND_API_HOST = "http://agenta-backend-test:8000"


@pytest.mark.asyncio
async def test_create_app_from_template(
    app_from_template, fetch_single_prompt_template
):
    payload = app_from_template
    payload["app_name"] = APP_NAME
    payload["template_id"] = fetch_single_prompt_template["id"]

    response = httpx.post(
        f"{BACKEND_API_HOST}/apps/app_and_variant_from_template/", json=payload
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_evaluators_endpoint():
    response = await test_client.get(
        f"{BACKEND_API_HOST}/evaluators/",
        timeout=timeout,
    )
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_create_auto_exact_match_evaluator_config(
    auto_exact_match_evaluator_config,
):
    async with db_engine.get_session() as session:
        result = await session.execute(select(AppDB).filter_by(app_name=APP_NAME))
        app = result.scalars().first()

        payload = auto_exact_match_evaluator_config
        payload["app_id"] = str(app.id)
        payload["settings_values"]["correct_answer_key"] = "correct_answer"

        response = await test_client.post(
            f"{BACKEND_API_HOST}/evaluators/configs/", json=payload, timeout=timeout
        )
        assert response.status_code == 200
        assert response.json()["evaluator_key"] == payload["evaluator_key"]
        assert response.json()["settings_values"] == payload["settings_values"]


@pytest.mark.asyncio
async def test_create_auto_similarity_match_evaluator_config(
    auto_similarity_match_evaluator_config,
):
    async with db_engine.get_session() as session:
        result = await session.execute(select(AppDB).filter_by(app_name=APP_NAME))
        app = result.scalars().first()

        payload = auto_similarity_match_evaluator_config
        payload["app_id"] = str(app.id)
        payload["settings_values"]["correct_answer_key"] = "correct_answer"

        response = await test_client.post(
            f"{BACKEND_API_HOST}/evaluators/configs/", json=payload, timeout=timeout
        )
        assert response.status_code == 200
        assert response.json()["evaluator_key"] == payload["evaluator_key"]
        assert response.json()["settings_values"] == payload["settings_values"]


@pytest.mark.asyncio
async def test_create_auto_regex_test_evaluator_config(
    auto_regex_test_evaluator_config,
):
    async with db_engine.get_session() as session:
        result = await session.execute(select(AppDB).filter_by(app_name=APP_NAME))
        app = result.scalars().first()

        payload = auto_regex_test_evaluator_config
        payload["app_id"] = str(app.id)
        payload["settings_values"]["regex_pattern"] = "^ig\\d{3}$"
        payload["settings_values"]["correct_answer_key"] = "correct_answer"

        response = await test_client.post(
            f"{BACKEND_API_HOST}/evaluators/configs/", json=payload, timeout=timeout
        )
        assert response.status_code == 200
        assert response.json()["evaluator_key"] == payload["evaluator_key"]
        assert response.json()["settings_values"] == payload["settings_values"]


@pytest.mark.asyncio
async def test_create_auto_webhook_test_evaluator_config(
    auto_webhook_test_evaluator_config,
):
    async with db_engine.get_session() as session:
        result = await session.execute(select(AppDB).filter_by(app_name=APP_NAME))
        app = result.scalars().first()

        payload = auto_webhook_test_evaluator_config
        payload["app_id"] = str(app.id)
        payload["settings_values"]["correct_answer_key"] = "correct_answer"

        response = await test_client.post(
            f"{BACKEND_API_HOST}/evaluators/configs/", json=payload, timeout=timeout
        )
        assert response.status_code == 200
        assert response.json()["evaluator_key"] == payload["evaluator_key"]
        assert response.json()["settings_values"] == payload["settings_values"]


@pytest.mark.asyncio
async def test_create_auto_ai_critique_evaluator_config(
    auto_ai_critique_evaluator_config,
):
    async with db_engine.get_session() as session:
        result = await session.execute(select(AppDB).filter_by(app_name=APP_NAME))
        app = result.scalars().first()

        payload = auto_ai_critique_evaluator_config
        payload["app_id"] = str(app.id)
        payload["settings_values"]["correct_answer_key"] = "correct_answer"

        response = await test_client.post(
            f"{BACKEND_API_HOST}/evaluators/configs/", json=payload, timeout=timeout
        )
        assert response.status_code == 200
        assert response.json()["evaluator_key"] == payload["evaluator_key"]
        assert response.json()["settings_values"] == payload["settings_values"]


@pytest.mark.asyncio
async def test_get_evaluator_configs():
    async with db_engine.get_session() as session:
        result = await session.execute(select(AppDB).filter_by(app_name=APP_NAME))
        app = result.scalars().first()

        response = await test_client.get(
            f"{BACKEND_API_HOST}/evaluators/configs/?app_id={str(app.id)}",
            timeout=timeout,
        )
        assert response.status_code == 200
        assert type(response.json()) == list


async def fetch_evaluation_results(evaluation_id):
    response = await test_client.get(
        f"{BACKEND_API_HOST}/evaluations/{evaluation_id}/results/", timeout=timeout
    )
    response_data = response.json()
    print("Response Data: ", response_data)

    assert response.status_code == 200
    assert response_data["evaluation_id"] == evaluation_id


async def wait_for_evaluation_to_finish(evaluation_id):
    max_attempts = 12
    intervals = 5  # seconds
    for _ in range(max_attempts):
        response = await test_client.get(
            f"{BACKEND_API_HOST}/evaluations/{evaluation_id}/status/",
            timeout=timeout,
        )
        response_data = response.json()
        if response_data["status"]["value"] == EvaluationStatusEnum.EVALUATION_FINISHED:
            await fetch_evaluation_results(evaluation_id)
            assert True
            return
        await asyncio.sleep(intervals)

    assert (
        False
    ), f"Evaluation status did not become '{EvaluationStatusEnum.EVALUATION_FINISHED}' within the specified polling time"


async def create_evaluation_with_evaluator(evaluator_config_name):
    # Fetch app, app_variant and testset
    async with db_engine.get_session() as session:
        app_result = await session.execute(select(AppDB).filter_by(app_name=APP_NAME))
        app = app_result.scalars().first()

        app_variant_result = await session.execute(
            select(AppVariantDB).filter_by(app_id=app.id)
        )
        app_variant = app_variant_result.scalars().first()

        testset_result = await session.execute(
            select(TestSetDB).filter_by(app_id=app.id)
        )
        testset = testset_result.scalars().first()

        # Prepare payload
        payload = {
            "app_id": str(app.id),
            "variant_ids": [str(app_variant.id)],
            "evaluators_configs": [],
            "testset_id": str(testset.id),
            "lm_providers_keys": {"OPENAI_API_KEY": OPEN_AI_KEY},
            "rate_limit": {
                "batch_size": 10,
                "max_retries": 3,
                "retry_delay": 3,
                "delay_between_batches": 5,
            },
        }

        # Fetch evaluator configs
        response = await test_client.get(
            f"{BACKEND_API_HOST}/evaluators/configs/?app_id={payload['app_id']}",
            timeout=timeout,
        )
        list_of_configs_ids = []
        evaluator_configs = response.json()
        for evaluator_config in evaluator_configs:
            if evaluator_config["evaluator_key"] == evaluator_config_name:
                list_of_configs_ids.append(evaluator_config["id"])

        # Update payload with list of configs ids
        payload["evaluators_configs"] = list_of_configs_ids

        # Sleep for 10 seconds (to allow the llm app container start completely)
        await asyncio.sleep(10)

        # Make request to create evaluation
        response = await test_client.post(
            f"{BACKEND_API_HOST}/evaluations/", json=payload, timeout=timeout
        )
        response_data = response.json()[0]

        assert response.status_code == 200
        assert response_data["app_id"] == payload["app_id"]
        assert (
            response_data["status"]["value"]
            == EvaluationStatusEnum.EVALUATION_INITIALIZED.value
        )
        assert response_data is not None

        # Wait for evaluation to finish
        evaluation_id = response_data["id"]
        await wait_for_evaluation_to_finish(evaluation_id)


@pytest.mark.asyncio
async def test_create_evaluation_auto_exact_match():
    await create_evaluation_with_evaluator("auto_exact_match_evaluator_config")


@pytest.mark.asyncio
async def test_create_evaluation_auto_similarity_match():
    await create_evaluation_with_evaluator("auto_similarity_match_evaluator_config")


@pytest.mark.asyncio
async def test_create_evaluation_auto_regex_test():
    await create_evaluation_with_evaluator("auto_regex_test_evaluator_config")


@pytest.mark.asyncio
async def test_create_evaluation_auto_webhook_test():
    await create_evaluation_with_evaluator("auto_webhook_test_evaluator_config")


@pytest.mark.asyncio
async def test_create_evaluation_auto_ai_critique():
    await create_evaluation_with_evaluator("auto_ai_critique_evaluator_config")


@pytest.mark.asyncio
async def test_delete_evaluator_config():
    async with db_engine.get_session() as session:
        result = await session.execute(select(AppDB).filter_by(app_name=APP_NAME))
        app = result.scalars().first()

        response = await test_client.get(
            f"{BACKEND_API_HOST}/evaluators/configs/?app_id={str(app.id)}",
            timeout=timeout,
        )
        list_of_deleted_configs = []
        evaluator_configs = response.json()
        for evaluator_config in evaluator_configs:
            response = await test_client.delete(
                f"{BACKEND_API_HOST}/evaluators/configs/{str(evaluator_config['id'])}/",
                timeout=timeout,
            )
            list_of_deleted_configs.append(response.json())

        count_of_deleted_configs = sum(list_of_deleted_configs)
        assert len(evaluator_configs) == count_of_deleted_configs


@pytest.mark.asyncio
async def test_evaluation_scenario_match_evaluation_testset_length():
    async with db_engine.get_session() as session:
        result = await session.execute(
            select(EvaluationDB).options(joinedload(EvaluationDB.testset))
        )
        evaluations = result.scalars().all()

        evaluation = evaluations[0]
        evaluation_scenarios_result = await session.execute(
            select(EvaluationScenarioDB).filter_by(evaluation_id=evaluation.id)
        )
        evaluation_scenarios = evaluation_scenarios_result.scalars().all()

        assert len(evaluation_scenarios) == len(evaluation.testset.csvdata)


@pytest.mark.asyncio
async def test_remove_running_template_app_container():
    import docker

    # Connect to the Docker daemon
    client = docker.from_env()
    async with db_engine.get_session() as session:
        app_result = await session.execute(select(AppDB).filter_by(app_name=APP_NAME))
        app = app_result.scalars().first()

        deployment_result = await session.execute(
            select(DeploymentDB).filter_by(app_id=app.id)
        )
        deployment = deployment_result.scalars().first()

    try:
        # Retrieve container
        container = client.containers.get(deployment.container_name)
        # Stop and remove container
        container.stop()
        container.remove()
        assert True
    except:
        assert False
