import brownie

DAY = 86400


def test_update_registry(alice, node, registry):
    node.setTTL(DAY, {"from": alice})
    assert registry.ttl(node.baseNode()) == DAY


def test_is_guarded(bob, node):
    with brownie.reverts():
        node.setTTL(DAY, {"from": bob})
