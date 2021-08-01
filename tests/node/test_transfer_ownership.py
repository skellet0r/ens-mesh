import pytest
from brownie import ZERO_ADDRESS, convert

pytestmark = pytest.mark.usefixtures("mint_alice")


def test_token_transfer_does_not_transfer_ownership_immediately(alice, bob, registry, node, web3):
    alice_label = web3.ens.labelhash("alice")
    alice_node = web3.ens.namehash("alice.node.test")
    node.transferFrom(alice, bob, convert.to_uint(alice_label), {"from": alice})

    assert registry.owner(alice_node) == alice

    node.reclaim(convert.to_uint(alice_label), bob, {"from": bob})

    assert registry.owner(alice_node) == bob


def test_burning_token_removes_ens_node_ownership(alice, registry, node, web3):
    alice_label = web3.ens.labelhash("alice")
    alice_node = web3.ens.namehash("alice.node.test")
    node.burn(convert.to_uint(alice_label), {"from": alice})

    assert registry.owner(alice_node) == ZERO_ADDRESS
