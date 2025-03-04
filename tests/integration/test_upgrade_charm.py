#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.


import logging
from pathlib import Path

import pytest
import yaml
from helpers import IPAddressWorkaround, check_prometheus_is_ready

logger = logging.getLogger(__name__)

METADATA = yaml.safe_load(Path("./metadata.yaml").read_text())
app_name = METADATA["name"]
resources = {"prometheus-image": METADATA["resources"]["prometheus-image"]["upstream-source"]}

# Please see https://github.com/canonical/prometheus-k8s-operator/issues/197
TIMEOUT = 1000


@pytest.mark.abort_on_fail
async def test_deploy_from_edge_and_upgrade_from_local_path(ops_test, prometheus_charm):
    """Build the charm-under-test and deploy it together with related charms.

    Assert on the unit status before any relations/configurations take place.
    """
    async with IPAddressWorkaround(ops_test):
        logger.debug("deploy charm from charmhub")
        await ops_test.model.deploy(f"ch:{app_name}", application_name=app_name, channel="edge")
        await ops_test.model.wait_for_idle(apps=[app_name], status="active", timeout=TIMEOUT)

        logger.debug("upgrade deployed charm with local charm %s", prometheus_charm)
        await ops_test.model.applications[app_name].refresh(
            path=prometheus_charm, resources=resources
        )
        await ops_test.model.wait_for_idle(apps=[app_name], status="active", timeout=TIMEOUT)
        await check_prometheus_is_ready(ops_test, app_name, 0)
