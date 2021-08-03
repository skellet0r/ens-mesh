import brownie
from brownie import ETH_ADDRESS


def test_update_registry(alice, node, registry, reverse_registrar):
    node.setReverseResolver(ETH_ADDRESS, {"from": alice})
    assert registry.resolver(node.reverseNode()) == ETH_ADDRESS


def test_is_guarded(bob, node):
    with brownie.reverts():
        node.setResolver(ETH_ADDRESS, {"from": bob})
