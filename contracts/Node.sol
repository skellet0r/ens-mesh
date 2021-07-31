// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;

import {ENS} from "@ensdomains/ens/contracts/ENS.sol";

import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";

contract Node is AccessControl {
    ENS public immutable ens;
    bytes32 public immutable baseNode;

    constructor(ENS _ens, bytes32 _baseNode) {
        ens = _ens;
        baseNode = _baseNode;
        _setupRole(DEFAULT_ADMIN_ROLE, _msgSender());
    }

    function setResolver(address _resolver)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        ens.setResolver(baseNode, _resolver);
    }

    function setTTL(uint64 _ttl) external onlyRole(DEFAULT_ADMIN_ROLE) {
        ens.setTTL(baseNode, _ttl);
    }

    function setSubnodeOwner(bytes32 _label, address _owner)
        external
        onlyRole(REGISTRAR_ROLE)
    {
        ens.setSubnodeOwner(baseNode, _label, _owner);
    }

    modifier onlyRole(bytes32 _role) {
        require(hasRole(_role, _msgSender()));
        _;
    }
}
