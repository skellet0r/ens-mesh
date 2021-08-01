import pytest


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
def node(alice, Node, registrar, registry, web3):
    node = Node.deploy(registry, web3.ens.namehash("node.test"), {"from": alice})
    registrar.register(web3.ens.labelhash("node"), node, {"from": alice})
    return node
