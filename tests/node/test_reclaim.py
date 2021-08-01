import brownie
import pytest
from brownie import ETH_ADDRESS, convert

pytestmark = pytest.mark.usefixtures("mint_bob")


def test_reclaiming_subnode_ownership(bob, node, registry, web3):
    bob_label = web3.ens.labelhash("bob")
    bob_node = web3.ens.namehash("bob.node.test")

    registry.setOwner(bob_node, ETH_ADDRESS, {"from": bob})
    assert registry.owner(bob_node) == ETH_ADDRESS

    node.reclaim(convert.to_uint(bob_label), bob, {"from": bob})
    assert registry.owner(bob_node) == bob


def test_is_guarded(alice, bob, node, registry, web3):
    bob_label = web3.ens.labelhash("bob")
    bob_node = web3.ens.namehash("bob.node.test")

    registry.setOwner(bob_node, ETH_ADDRESS, {"from": bob})
    assert registry.owner(bob_node) == ETH_ADDRESS

    with brownie.reverts():
        node.reclaim(convert.to_uint(bob_label), bob, {"from": alice})
