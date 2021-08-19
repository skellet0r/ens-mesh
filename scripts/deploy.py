from brownie import AdminGranter, Node, SubnodeRegistrar, accounts, history, web3
from brownie._config import _get_data_folder
from brownie.network import show_active
from brownie.project import load

DEPLOYER = accounts.load("dev")


_open_projects = {}


def pm(project_id):
    if project_id not in _open_projects:
        path = _get_data_folder().joinpath(f"packages/{project_id}")
        _open_projects[project_id] = load(path, project_id)

    return _open_projects[project_id]


def main():
    publish_source = show_active() in ["mainnet", "kovan"]

    ENSRegistry = pm("ensdomains/ens@0.6.0").ENSRegistry
    FIFSRegistrar = pm("ensdomains/ens@0.6.0").FIFSRegistrar
    ReverseRegistrar = pm("ensdomains/ens@0.6.0").ReverseRegistrar
    PublicResolver = pm("skellet0r/resolvers@0.4.1").PublicResolver

    # deploy the core ENS registry
    registry = ENSRegistry.deploy(
        {"from": DEPLOYER, "priority_fee": "1.1 gwei"}, publish_source=publish_source
    )

    # the default public resolver
    public_resolver = PublicResolver.deploy(
        registry, {"from": DEPLOYER, "priority_fee": "1.1 gwei"}, publish_source=publish_source
    )

    # deploy the test tld registrar
    registrar = FIFSRegistrar.deploy(
        registry,
        web3.ens.namehash("test"),
        {"from": DEPLOYER, "priority_fee": "1.1 gwei"},
        publish_source=publish_source,
    )
    registry.setSubnodeOwner(
        "0x0", web3.ens.labelhash("test"), registrar, {"from": DEPLOYER, "priority_fee": "1.1 gwei"}
    )

    # deploy the reverse registrar, with the default reverse resolver
    reverse_registrar = ReverseRegistrar.deploy(
        registry,
        public_resolver,
        {"from": DEPLOYER, "priority_fee": "1.1 gwei"},
        publish_source=publish_source,
    )
    reverse_label = web3.ens.labelhash("reverse")
    reverse_node = web3.ens.namehash("reverse")
    addr_label = web3.ens.labelhash("addr")

    registry.setSubnodeOwner(
        "0x0", reverse_label, DEPLOYER, {"from": DEPLOYER, "priority_fee": "1.1 gwei"}
    )
    registry.setSubnodeOwner(
        reverse_node, addr_label, reverse_registrar, {"from": DEPLOYER, "priority_fee": "1.1 gwei"}
    )

    # deploy our node
    node = Node.deploy(
        registry,
        web3.ens.namehash("node.test"),
        {"from": DEPLOYER, "priority_fee": "1.1 gwei"},
    )
    registrar.register(
        web3.ens.labelhash("node"), node, {"from": DEPLOYER, "priority_fee": "1.1 gwei"}
    )

    # deploy the subnode registrar
    subnode_registrar = SubnodeRegistrar.deploy(
        registry,
        node,
        {"from": DEPLOYER, "priority_fee": "1.1 gwei"},
    )
    node.grantRole(
        node.REGISTRAR_ROLE(), subnode_registrar, {"from": DEPLOYER, "priority_fee": "1.1 gwei"}
    )

    # deploy dummy admin granter
    if show_active() != "mainnet":
        admin_granter = AdminGranter.deploy(
            node,
            {"from": DEPLOYER, "priority_fee": "1.1 gwei"},
        )
        node.grantRole("0x0", admin_granter, {"from": DEPLOYER, "priority_fee": "1.1 gwei"})

    print(f"Total Gas Used: {sum([tx.gas_used for tx in history]) / 10 ** 9:.5f}")
