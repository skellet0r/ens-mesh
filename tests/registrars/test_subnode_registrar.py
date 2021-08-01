import brownie
from brownie import ETH_ADDRESS, ZERO_ADDRESS
from hexbytes import HexBytes


def test_subnode_is_created(alice, node, subnode_registrar, web3):
    alice_label = web3.ens.labelhash("alice")
    tx = subnode_registrar.createSubnode(node, alice_label, {"from": alice})
    assert len(tx.new_contracts) == 1


def test_subnode_admin_is_creator(alice, Node, node, subnode_registrar, web3):
    alice_label = web3.ens.labelhash("alice")
    tx = subnode_registrar.createSubnode(node, alice_label, {"from": alice})
    new_node = Node.at(tx.new_contracts[0])
    assert new_node.getRoleMemberCount("0x0") == 1
    assert new_node.getRoleMember("0x0", 0) == alice


def test_subnode_constants(alice, Node, node, registry, subnode_registrar, web3):
    alice_label = web3.ens.labelhash("alice")
    tx = subnode_registrar.createSubnode(node, alice_label, {"from": alice})
    new_node = Node.at(tx.new_contracts[0])

    assert new_node.ens() == registry
    assert HexBytes(new_node.baseNode()) == web3.ens.namehash("alice.node.test")

    assert registry.resolver(new_node.baseNode()) == ZERO_ADDRESS
    assert registry.ttl(new_node.baseNode()) == 0


def test_subnode_with_config(alice, Node, node, registry, subnode_registrar, web3):
    alice_label = web3.ens.labelhash("alice")
    tx = subnode_registrar.createSubnodeWithConfig(
        node, alice_label, ETH_ADDRESS, 86400, {"from": alice}
    )
    new_node = Node.at(tx.new_contracts[0])

    assert registry.resolver(new_node.baseNode()) == ETH_ADDRESS
    assert registry.ttl(new_node.baseNode()) == 86400


def test_creating_subnode_event_emitted(alice, node, subnode_registrar, web3):
    alice_label = web3.ens.labelhash("alice")
    tx = subnode_registrar.createSubnode(node, alice_label, {"from": alice})

    assert "SubnodeCreated" in tx.events
    assert tx.events["SubnodeCreated"]["_parentNode"] == node
    assert tx.events["SubnodeCreated"]["_admin"] == alice
    assert tx.events["SubnodeCreated"]["_subnode"] == tx.new_contracts[0]
    assert HexBytes(tx.events["SubnodeCreated"]["_label"]) == HexBytes(alice_label)


def test_is_guarded(bob, node, subnode_registrar, web3):
    alice_label = web3.ens.labelhash("alice")
    with brownie.reverts():
        subnode_registrar.createSubnode(node, alice_label, {"from": bob})
