import brownie
from brownie import ETH_ADDRESS
from brownie_tokens import ERC20


def test_withdraw_erc20(alice, node):
    dummy_token = ERC20()
    dummy_token._mint_for_testing(node, 100 * 10 ** 18, {"from": node})

    node.withdrawERC20(dummy_token, alice, {"from": alice})

    assert dummy_token.balanceOf(alice) == 100 * 10 ** 18


def test_withdraw_eth(alice, node):
    alice.transfer(node, 10 ** 18)

    node.withdrawERC20(ETH_ADDRESS, alice, {"from": alice})

    assert alice.balance() == 100 * 10 ** 18


def test_withdraw_is_guarded(alice, bob, node):
    alice.transfer(node, 10 ** 18)

    with brownie.reverts():
        node.withdrawERC20(ETH_ADDRESS, bob, {"from": bob})


def test_withdraw_erc721(alice, node, pm):
    ERC721Mock = pm("OpenZeppelin/openzeppelin-contracts@3.4.1-solc-0.7").ERC721Mock
    mock = ERC721Mock.deploy("", "", {"from": alice})

    mock.safeMint(node, 0, {"from": alice})
    node.withdrawERC721(mock, 0, alice, b"", {"from": alice})

    assert mock.ownerOf(0) == alice


def test_withdraw_erc721_is_guarded(alice, bob, node, pm):
    ERC721Mock = pm("OpenZeppelin/openzeppelin-contracts@3.4.1-solc-0.7").ERC721Mock
    mock = ERC721Mock.deploy("", "", {"from": alice})

    mock.safeMint(node, 0, {"from": alice})
    with brownie.reverts():
        node.withdrawERC721(mock, 0, bob, b"", {"from": bob})
