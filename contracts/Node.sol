// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;

import {ENS} from "@ensdomains/ens/contracts/ENS.sol";
import {ReverseRegistrar} from "@ensdomains/ens/contracts/ReverseRegistrar.sol";

import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {ERC721Burnable} from "@openzeppelin/contracts/token/ERC721/ERC721Burnable.sol";
import {IERC721Receiver} from "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";

/// @title ENS Node
/// @author Edward Amor
/// @notice A single node in the ENS Directed Acyclic Graph
contract Node is AccessControl, ERC721, ERC721Burnable, IERC721Receiver {
    using SafeERC20 for IERC20;

    event NewResolver(address _resolver);
    event NewReverseResolver(address _resolver);
    event NewTTL(uint64 _ttl);
    event NewRegistration(bytes32 indexed _label, address indexed _owner);
    event ERC20Withdrawn(
        address indexed _token,
        uint256 _amount,
        address indexed _recipient
    );
    event ERC721Withdrawn(
        address indexed _token,
        uint256 _tokenId,
        address indexed _recipient
    );

    // namehash('addr.reverse')
    bytes32 public constant ADDR_REVERSE_NODE =
        0x91d1777781884d03a6757a803996e38de2a42967fb37eeaca72729271025a9e2;

    address public constant ETH_ADDRESS =
        0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE;
    bytes32 public constant REGISTRAR_ROLE = keccak256("REGISTRAR_ROLE");

    ENS public immutable ens;

    bytes32 public baseNode;
    bytes32 public reverseNode;

    constructor(ENS _ens, bytes32 _baseNode)
        ERC721("ENS Mesh Node", "ENS-Mesh-Node")
    {
        ens = _ens;
        baseNode = _baseNode;

        ReverseRegistrar reverseRegistrar = ReverseRegistrar(
            _ens.owner(ADDR_REVERSE_NODE)
        );
        reverseNode = reverseRegistrar.claim(address(this));

        _setupRole(DEFAULT_ADMIN_ROLE, _msgSender());
        _setupRole(REGISTRAR_ROLE, _msgSender());
    }

    /// @dev Enables receiving ETH
    receive() external payable {}

    /**
     * @notice Initialize the contract.
     * @dev This should be called in the same transaction as the creation
     * of the proxy contract.
     * @param _baseNode The ENS node this contract has ownership of
     */
    function initialize(bytes32 _baseNode) external {
        require(baseNode == bytes32(0));
        baseNode = _baseNode;

        ReverseRegistrar reverseRegistrar = ReverseRegistrar(
            ens.owner(ADDR_REVERSE_NODE)
        );
        reverseNode = reverseRegistrar.claim(address(this));

        _setupRole(DEFAULT_ADMIN_ROLE, _msgSender());
        _setupRole(REGISTRAR_ROLE, _msgSender());
    }

    /**
     * @notice Set the resolver for the owned ENS node
     * @param _resolver The address of a resolver contract
     */
    function setResolver(address _resolver)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        ens.setResolver(baseNode, _resolver);
        emit NewResolver(_resolver);
    }

    /**
     */
    function setReverseResolver(address _resolver)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        ens.setResolver(reverseNode, _resolver);
        emit NewReverseResolver(_resolver);
    }

    /**
     * @notice Set the TTL for the owned ENS node
     * @param _ttl The TTL (in seconds)
     */
    function setTTL(uint64 _ttl) external onlyRole(DEFAULT_ADMIN_ROLE) {
        ens.setTTL(baseNode, _ttl);
        emit NewTTL(_ttl);
    }

    /**
     * @notice Register a subnode
     * @dev Only callable by an account with the REGISTRAR_ROLE
     * @param _label The labelhash of the label to register
     * @param _owner The account to give ownership to
     */
    function register(bytes32 _label, address _owner)
        external
        onlyRole(REGISTRAR_ROLE)
    {
        _safeMint(_owner, uint256(_label));
        ens.setSubnodeOwner(baseNode, _label, _owner);
        emit NewRegistration(_label, _owner);
    }

    /**
     * @notice Reclaim ownership of a direct ENS subnode
     * @dev The caller must be the owner of the token representing
     * the ENS node, or an operator, or approved.
     * @param _tokenId The tokenId (uint256(_label)) to reclaim ownership of
     * @param _owner The account to transfer ownership of the subnode to
     */
    function reclaim(uint256 _tokenId, address _owner) external {
        require(_isApprovedOrOwner(_msgSender(), _tokenId));
        ens.setSubnodeOwner(baseNode, bytes32(_tokenId), _owner);
    }

    /// @dev Modifier limiting access to functions to users with specific privileges
    modifier onlyRole(bytes32 _role) {
        require(hasRole(_role, _msgSender()));
        _;
    }

    /// @dev On burning a token also revoke ENS subnode ownership
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId
    ) internal override(ERC721) {
        super._beforeTokenTransfer(from, to, tokenId);
        if (to == address(0)) {
            ens.setSubnodeOwner(baseNode, bytes32(tokenId), to);
        }
    }

    /// @dev Allow the receipt of ERC721 tokens
    function onERC721Received(
        address operator,
        address from,
        uint256 tokenId,
        bytes calldata data
    ) external override returns (bytes4) {
        return type(IERC721Receiver).interfaceId;
    }

    /// @dev Allows the admin to withdraw funds sent to this contract
    function withdrawERC20(IERC20 _token, address payable _recipient)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        if (address(_token) == ETH_ADDRESS) {
            uint256 amount = address(this).balance;
            _recipient.transfer(amount);
            emit ERC20Withdrawn(ETH_ADDRESS, amount, _recipient);
        } else {
            uint256 amount = _token.balanceOf(address(this));
            _token.transfer(_recipient, amount);
            emit ERC20Withdrawn(address(_token), amount, _recipient);
        }
    }

    /// @dev Allows the admin to withdraw ERC721 tokens
    /// CAUTION: If this is a subnode with tokenized ownership of
    /// an ENS node, the admin will be able to transfer the token
    /// representing ownership and, thereby edit subnode ENS records
    function withdrawERC721(
        ERC721 _token,
        uint256 _tokenId,
        address _recipient,
        bytes memory _data
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _token.safeTransferFrom(address(this), _recipient, _tokenId, _data);
        emit ERC721Withdrawn(address(_token), _tokenId, _recipient);
    }
}
