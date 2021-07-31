// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;

import {ENS} from "@ensdomains/ens/contracts/ENS.sol";

contract Node {
    ENS public immutable ens;
    bytes32 public immutable baseNode;

    constructor(ENS _ens, bytes32 _baseNode) {
        ens = _ens;
        baseNode = _baseNode;
    }

    function setResolver(address _resolver) external {
        ens.setResolver(baseNode, _resolver);
    }

    function setTTL(uint64 _ttl) external {
        ens.setTTL(baseNode, _ttl);
    }
}
