import brownie
from brownie import ETH_ADDRESS


def test_update_registry(alice, node, registry):
    node.setResolver(ETH_ADDRESS, {"from": alice})
    assert registry.resolver(node.baseNode()) == ETH_ADDRESS


def test_is_guarded(bob, node):
    with brownie.reverts():
        node.setResolver(ETH_ADDRESS, {"from": bob})
