import pytest
from brownie import ZERO_ADDRESS


@pytest.fixture(scope="session")
def registry(alice, pm):
    ENSRegistry = pm("ensdomains/ens@0.6.0").ENSRegistry
    return ENSRegistry.deploy({"from": alice})


@pytest.fixture(scope="session")
def registrar(alice, pm, registry, web3):
    FIFSRegistrar = pm("ensdomains/ens@0.6.0").FIFSRegistrar
    registrar = FIFSRegistrar.deploy(registry, web3.ens.namehash("test"), {"from": alice})
    registry.setSubnodeOwner("0x0", web3.ens.labelhash("test"), registrar, {"from": alice})
    return registrar


@pytest.fixture(scope="session")
def reverse_registrar(alice, pm, registry, web3):
    ReverseRegistrar = pm("ensdomains/ens@0.6.0").ReverseRegistrar
    reverse_registrar = ReverseRegistrar.deploy(registry, ZERO_ADDRESS, {"from": alice})

    reverse_label = web3.ens.labelhash("reverse")
    reverse_node = web3.ens.namehash("reverse")
    addr_label = web3.ens.labelhash("addr")

    registry.setSubnodeOwner("0x0", reverse_label, alice, {"from": alice})
    registry.setSubnodeOwner(reverse_node, addr_label, reverse_registrar, {"from": alice})
    return reverse_registrar


@pytest.fixture(scope="session")
def node(alice, Node, registrar, registry, reverse_registrar, web3):
    node = Node.deploy(registry, web3.ens.namehash("node.test"), {"from": alice})
    registrar.register(web3.ens.labelhash("node"), node, {"from": alice})
    return node


@pytest.fixture(scope="session")
def subnode_registrar(alice, SubnodeRegistrar, node, registry):
    subnode_registrar = SubnodeRegistrar.deploy(registry, node, {"from": alice})
    node.grantRole(node.REGISTRAR_ROLE(), subnode_registrar, {"from": alice})
    return subnode_registrar
