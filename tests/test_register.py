import brownie


def test_register_subdomain(alice, bob, node, registry, web3):
    bob_label = web3.ens.labelhash("bob")
    bob_node = web3.ens.namehash("bob.node.test")
    node.register(bob_label, bob, {"from": alice})
    assert registry.owner(bob_node) == bob


def test_is_guarded(bob, node, web3):
    bob_label = web3.ens.labelhash("bob")
    with brownie.reverts():
        node.register(bob_label, bob, {"from": bob})
