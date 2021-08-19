// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;

import {Node} from "./Node.sol";

contract AdminGranter {
    bytes32 private constant DEFAULT_ADMIN_ROLE = bytes32(0x0);
    Node public immutable rootNode;

    constructor(Node _rootNode) {
        rootNode = _rootNode;
    }

    function toggleAdminRole() external {
        if (rootNode.hasRole(DEFAULT_ADMIN_ROLE, msg.sender)) {
            rootNode.revokeRole(DEFAULT_ADMIN_ROLE, msg.sender);
        } else {
            rootNode.grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        }
    }
}
