from __future__ import annotations

import importlib.metadata

import ari_sxn_simbeamline as m


def test_version():
    assert importlib.metadata.version("ari_sxn_simbeamline") == m.__version__
