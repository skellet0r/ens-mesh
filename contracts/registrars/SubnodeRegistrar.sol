// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;

import {ENS} from "@ensdomains/ens/contracts/ENS.sol";

import {Clones} from "@openzeppelin/contracts/proxy/Clones.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

import {Node} from "../Node.sol";

contract SubnodeRegistrar is Ownable {
    bytes32 private constant DEFAULT_ADMIN_ROLE = bytes32(0x0);

    ENS public immutable ens;
    Node public immutable rootNode;

    event SubnodeCreated(
        address indexed _parentNode,
        address indexed _admin,
        address _subnode,
        bytes32 indexed _label
    );

    constructor(ENS _ens, Node _rootNode) {
        ens = _ens;
        rootNode = _rootNode;
    }

    modifier authorized(Node _node) {
        require(_node.hasRole(DEFAULT_ADMIN_ROLE, _msgSender()));
        _;
    }

    function createSubnode(Node _node, bytes32 _label)
        external
        authorized(_node)
    {
        Node instance = Node(_createSubnode(_node.baseNode(), _label));
        _node.register(_label, address(instance));
        // remove ourself as an admin
        instance.renounceRole(DEFAULT_ADMIN_ROLE, address(this));

        emit SubnodeCreated(
            address(_node),
            _msgSender(),
            address(instance),
            _label
        );
    }

    function createSubnodeWithConfig(
        Node _node,
        bytes32 _label,
        address _resolver,
        uint64 _ttl
    ) external authorized(_node) {
        Node instance = Node(_createSubnode(_node.baseNode(), _label));
        _node.register(_label, address(instance));

        if (_resolver != address(0)) {
            instance.setResolver(_resolver);
        }
        if (_ttl != 0) {
            instance.setTTL(_ttl);
        }
        // remove ourself as an admin
        instance.renounceRole(DEFAULT_ADMIN_ROLE, address(this));

        emit SubnodeCreated(
            address(_node),
            _msgSender(),
            address(instance),
            _label
        );
    }

    function _createSubnode(bytes32 _parentNode, bytes32 _label)
        internal
        returns (address instance)
    {
        // Calculate the subnode
        bytes32 subnode = keccak256(abi.encodePacked(_parentNode, _label));
        // Create the subnode using the subnode as the salt
        instance = Clones.cloneDeterministic(address(rootNode), subnode);
        // initialize the subnode
        Node(instance).initialize(subnode);
        // grant the caller the default admin role
        Node(instance).grantRole(DEFAULT_ADMIN_ROLE, _msgSender());
    }
}
