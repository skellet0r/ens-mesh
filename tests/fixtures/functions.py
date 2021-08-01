import pytest


@pytest.fixture
def mint_alice(alice, node, web3):
    alice_label = web3.ens.labelhash("alice")
    node.register(alice_label, alice, {"from": alice})


@pytest.fixture
def mint_bob(alice, bob, node, web3):
    bob_label = web3.ens.labelhash("bob")
    node.register(bob_label, bob, {"from": alice})
