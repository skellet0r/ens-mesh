// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;

import {ENS} from "@ensdomains/ens/contracts/ENS.sol";

import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {Initializable} from "@openzeppelin/contracts/proxy/Initializable.sol";

contract Node is AccessControl, ERC721, Initializable {
    bytes32 public constant REGISTRAR_ROLE = keccak256("REGISTRAR_ROLE");

    ENS public immutable ens;

    bytes32 public baseNode;

    constructor(ENS _ens, bytes32 _baseNode)
        ERC721("ENS Mesh Node", "ENS-Mesh-Node")
    {
        ens = _ens;
        initialize(_baseNode);
    }

    function initialize(bytes32 _baseNode) external initializer {
        baseNode = _baseNode;
        _setupRole(DEFAULT_ADMIN_ROLE, _msgSender());
        _setupRole(REGISTRAR_ROLE, _msgSender());
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
