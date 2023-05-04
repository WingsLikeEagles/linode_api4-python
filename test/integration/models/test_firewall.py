import time
import pytest
from linode_api4.objects import Firewall, FirewallDevice


@pytest.fixture(scope="session")
def create_linode(get_client):
    client = get_client
    available_regions = client.regions()
    chosen_region = available_regions[0]
    label = "linode_instance_fw_device"

    linode_instance, password = client.linode.instance_create(
        "g5-standard-4", chosen_region, image="linode/debian9", label=label
    )

    yield linode_instance

    linode_instance.delete()


def test_get_firewall_rules(get_client, create_firewall):
    firewall = get_client.load(Firewall, create_firewall.id)
    rules = firewall.rules

    assert(rules.inbound_policy in ['ACCEPT', 'DROP'])
    assert(rules.outbound_policy in ['ACCEPT', 'DROP'])


def test_update_firewall_rules(get_client, create_firewall):
    firewall = get_client.load(Firewall, create_firewall.id)
    new_rules = {
        "inbound": [
            {
                "action": "ACCEPT",
                "addresses": {
                    "ipv4": ["0.0.0.0/0"],
                    "ipv6": ["ff00::/8"],
                },
                "description": "A really cool firewall rule.",
                "label": "really-cool-firewall-rule",
                "ports": "80",
                "protocol": "TCP",
            }
        ],
        "inbound_policy": "ACCEPT",
        "outbound": [],
        "outbound_policy": "DROP",
    }

    firewall.update_rules(new_rules)

    time.sleep(1)

    firewall = get_client.load(Firewall, create_firewall.id)

    assert(firewall.rules.inbound_policy == 'ACCEPT')
    assert(firewall.rules.outbound_policy == 'DROP')


def test_get_devices(get_client, create_linode, create_firewall):
    linode = create_linode

    firewall_device = create_firewall.device_create(int(linode.id))

    firewall = get_client.load(Firewall, create_firewall.id)

    assert(len(firewall.devices) > 0)


def test_get_device(get_client, create_firewall, create_linode):
    firewall = create_firewall

    print("firewall info:", firewall.id, firewall.devices.first().id)

    firewall_device = get_client.load(FirewallDevice, firewall.devices.first().id, firewall.id)

    assert(firewall_device.entity.label == 'linode_instance_fw_device')
    assert(firewall_device.entity.type == 'linode')
    assert('/v4/linode/instances/' in firewall_device.entity.url)

