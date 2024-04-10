import pytest

import caproto as ca
from caproto.sync import client as sync

from caproto.tests import conftest
from caproto.tests.conftest import default_setup_module as setup_module  # noqa
from caproto.tests.conftest import default_teardown_module as teardown_module  # noqa

try:
    import numpy
except ImportError:
    # Used in pytest.mark.skipif() below.
    numpy = None


ioc_example_to_info = {"ARI_SXN_SimBeamline.Caproto_servers.Mirror_section":
                       dict(group_cls='AriM1Mirror',
                            kwargs={},
                            marks=[pytest.mark.skipif(numpy is None, reason="Requires numpy")],)
                       }


@pytest.mark.flaky(reruns=2, reruns_delay=2)
@pytest.mark.parametrize(
    "module_name",
    [pytest.param(name, marks=info["marks"])
     for name, info in ioc_example_to_info.items()
     ]
)
@pytest.mark.parametrize('async_lib', ['curio', 'trio', 'asyncio'])
def test_ioc_examples(request, module_name, async_lib):
    from caproto.server import PvpropertyReadOnlyData
    info = conftest.run_example_ioc_by_name(
        module_name, async_lib=async_lib, request=request
    )

    put_values = [
        (PvpropertyReadOnlyData, None),
        (ca.ChannelNumeric, [1]),
        (ca.ChannelString, ['USD']),
        (ca.ChannelChar, 'USD'),
        (ca.ChannelByte, b'USD'),
        (ca.ChannelEnum, [0]),
    ]

    skip_pvs = [('ophyd', ':exit')]

    def find_put_value(pv, channeldata):
        """Determine value to write to pv"""
        for skip_ioc, skip_suffix in skip_pvs:
            if skip_ioc in module_name:
                if pv.endswith(skip_suffix):
                    return None

        for put_class, put_value in put_values:
            if isinstance(channeldata, put_class):
                return put_value
        else:
            raise Exception('Failed to set default value for channeldata:'
                            f'{channeldata.__class__}')

    for pv, channeldata in info.pvdb.items():
        value = find_put_value(pv, channeldata)
        if value is None:
            print(f'Skipping write to {pv}')
            continue

        print(f'Writing {value} to {pv}')
        sync.write(pv, value, timeout=15)

        value = sync.read(pv, timeout=15)
        print(f'Read {pv} = {value}')
