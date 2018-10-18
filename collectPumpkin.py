"""
Collect pumpkin can be considered as a sample of OEP-8 smart contract
"""
from boa.interop.System.Storage import GetContext, Get, Put, Delete
from boa.interop.System.Runtime import CheckWitness, Notify
from boa.interop.System.Action import RegisterAction
from boa.builtins import ToScriptHash, concat
# from mycontracts.libs.SafeCheck import Require, RequireScriptHash, RequireWitness


"""
https://github.com/tonyclarking/python-template/blob/master/libs/Utils.py
"""
def Revert():
    """
    Revert the transaction. The opcodes of this function is `09f7f6f5f4f3f2f1f000f0`,
    but it will be changed to `ffffffffffffffffffffff` since opcode THROW doesn't
    work, so, revert by calling unused opcode.
    """
    raise Exception(0xF1F1F2F2F3F3F4F4)


"""
https://github.com/tonyclarking/python-template/blob/master/libs/SafeCheck.py
"""
def Require(condition):
    """
	If condition is not satisfied, return false
	:param condition: required condition
	:return: True or false
	"""
    if not condition:
        Revert()
    return True

def RequireScriptHash(key):
    """
    Checks the bytearray parameter is script hash or not. Script Hash
    length should be equal to 20.
    :param key: bytearray parameter to check script hash format.
    :return: True if script hash or revert the transaction.
    """
    Require(len(key) == 20)
    return True

def RequireWitness(witness):
    """
	Checks the transaction sender is equal to the witness. If not
	satisfying, revert the transaction.
	:param witness: required transaction sender
	:return: True if transaction sender or revert the transaction.
	"""
    Require(CheckWitness(witness))
    return True


"""
collect pumpkin smart contract
"""

TransferEvent = RegisterAction("transfer", "fromAcct", "toAcct", "tokenId", "amount")
ApprovalEvent = RegisterAction("approval", "owner", "spender", "tokenId", "amount")

# modify to the admin address
admin = ToScriptHash('AQf4Mzu1YJrhz9f3aRkkwSm9n3qhXGSh4p')

# TOKEN_ID1 is used to identify different tokens, to help store the token name, token symbol and balance
# TOKEN_ID1 = bytearray('b\x01')
# TOKEN_ID2 = bytearray('b\x02')
# TOKEN_ID3 = bytearray('b\x03')
# TOKEN_ID4 = bytearray('b\x04')
# TOKEN_ID5 = bytearray('b\x05')
# TOKEN_ID6 = bytearray('b\x06')
# TOKEN_ID7 = bytearray('b\x07')
# TOKEN_ID8 = bytearray('b\x08')

# TOKEN_ID_LIST = [TOKEN_ID1, TOKEN_ID2, TOKEN_ID3, TOKEN_ID4, TOKEN_ID5, TOKEN_ID6, TOKEN_ID7, TOKEN_ID8]
TOKEN_ID_LIST = [b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07', b'\x08']

# TOKEN_ID1 + NAME --- to store the name of the TOKEN_ID1 token
NAME = 'name'
# TOKEN_ID1 + SYMBOL --- to store the symbol of the TOKEN_ID1 token
SYMBOL = 'symbol'
# TOKEN_ID1+ BALANCE + address --- to store the balance of address in terms of the TOKEN_ID1 token
BALANCE = 'balance'
# TOKEN_ID1 + TOTAL_SUPPLY  --- to store the total supply of the TOKEN_ID1 token
TOTAL_SUPPLY = 'totalsupply'
# TOKEN_ID1 + APPROVE + owner + spender -- to store the approved TOKEN_ID1 amount to the spender by the owner
APPROVE = 'approve'
# INITED --- to store "TRUE" in order to make sure this contract can only be deployed once
INITED = 'Initialized'


def Main(operation, args):
    if operation == "name":
        if len(args) != 1:
            return False
        tokenId = args[0]
        return name(tokenId)
    if operation == "symbol":
        if len(args) != 1:
            return False
        tokenId = args[0]
        return symbol(tokenId)
    if operation == "totalSupply":
        if len(args) != 1:
            return False
        tokenId = args[0]
        return totalSupply(tokenId)
    if operation == "balanceOf":
        if len(args) != 2:
            return False
        account = args[0]
        tokenId = args[1]
        return balanceOf(account, tokenId)
    if operation == "transfer":
        if len(args) != 4:
            return False
        fromAcct = args[0]
        toAcct = args[1]
        tokenId = args[2]
        amount = args[3]
        return transfer(fromAcct, toAcct, tokenId, amount)
    if operation == "transferMulti":
        return transferMulti(args)
    if operation == "approve":
        if len(args) != 4:
            return False
        owner = args[0]
        spender = args[1]
        tokenId = args[2]
        amount = args[3]
        return approve(owner, spender, tokenId, amount)
    if operation == "approveMulti":
        return approveMulti(args)
    if operation == "allowance":
        if len(args) != 3:
            return False
        owner = args[0]
        spender = args[1]
        tokenId = args[2]
        return allowance(owner, spender, tokenId)
    if operation == "transferFrom":
        if len(args) != 5:
            return False
        spender = args[0]
        fromAcct = args[1]
        toAcct = args[2]
        tokenId = args[3]
        amount = args[4]
        return transferFrom(spender, fromAcct, toAcct, tokenId, amount)
    if operation == "transferFromMulti":
        return transferFromMulti(args)
    if operation == "compound":
        if len(args) != 1:
            return False
        account = args[0]
        return compound(account)
    ############ For testing usage only starts ############
    if operation == "init":
        if len(args) != 0:
            return False
        return init()

    ############ For testing usage only ends ############
    return False


def name(tokenId):
    """
    :param tokenId: helps to format name key = tokenId + NAME
    :return: name of the token with tokenId
    """
    return Get(GetContext(), concatkey(tokenId, NAME))


def symbol(tokenId):
    """
    :param tokenId: helps to format symbol key = tokenId + SYMBOL
    :return: symbol of token with tokenId
    """
    return Get(GetContext(), concatkey(tokenId, SYMBOL))


def totalSupply(tokenId):
    """
    :param tokenId:  helps to format totalSupply key = tokenId + TOTAL_SUPPLY
    :return: total supply of token with tokenId
    """
    return Get(GetContext(), concatkey(tokenId, TOTAL_SUPPLY))


def balanceOf(acct, tokenId):
    """
    get balance of accout in terms of token with the tokenId
    :param acct: used to check the acct balance
    :param tokenId: the tokenId determines which token balance of acct needs to be checked
    :return: the balance of acct in terms of tokenId tokens
    """
    return Get(GetContext(), concatkey(concatkey(tokenId, BALANCE), acct))


def transfer(fromAcct, toAcct, tokenId, amount):
    """
    transfer amount of tokens in terms of tokenId token from fromAcct to the toAcct
    :param fromAcct:
    :param toAcct:
    :param tokenId:
    :param amount:
    :return:
    """
    RequireWitness(fromAcct)
    Require(checkTokenId(tokenId))
    RequireScriptHash(fromAcct)
    RequireScriptHash(toAcct)

    balanceKey = concatkey(tokenId, BALANCE)
    fromKey = concatkey(balanceKey, fromAcct)
    fromBalance = Get(GetContext(), fromKey)
    if amount > fromBalance:
        return False
    if amount == fromBalance:
        Delete(GetContext(), fromKey)
    else:
        Put(GetContext(), fromKey, fromBalance - amount)

    toKey = concatkey(balanceKey, toAcct)
    toBalance = Get(GetContext(), toKey)
    Put(GetContext(), toKey, toBalance + amount)

    # Notify(["transfer", fromAcct, toAcct, tokenId, amount])
    TransferEvent(fromAcct, toAcct, tokenId, amount)

    return True


def transferMulti(args):
    """
    multi transfer
    :param args:[[fromAccount1, toAccount1, tokenId1, amount1],[fromAccount2, toAccount2, tokenId2, amount2]]
    :return: True or raise exception
    """
    for p in args:
        if len(p) != 4:
            raise Exception('transferMulti failed - input error!')
        if transfer(p[0], p[1], p[2], p[3]) == False:
            raise Exception('transferMulti failed - transfer error!')
    return True


def approve(owner, spender, tokenId, amount):
    """
    approve amount of the tokenId token to toAcct address, it can overwrite older approved amount
    :param owner:
    :param spender:
    :param tokenId:
    :param amount:
    :return:
    """
    RequireWitness(owner)
    RequireScriptHash(owner)
    RequireScriptHash(spender)
    Require(checkTokenId(tokenId))

    ownerBalance = balanceOf(owner, tokenId)
    Require(ownerBalance >= amount)

    key = concatkey(concatkey(concatkey(tokenId, APPROVE), owner), spender)
    Put(GetContext(), key, amount)

    # Notify(['approval', owner, spender, tokenId, amount])
    ApprovalEvent(owner, spender, tokenId, amount)

    return True


def approveMulti(args):
    """
    multi approve
    :param args: args:[[owner1, spender1, tokenId1, amount1],[owner2, spender2, tokenId2, amount2]]
    :return:
    """
    for p in args:
        if len(p) != 4:
            raise Exception('approveMulti failed - input error!')
        if approve(p[0], p[1], p[2], p[3]) == False:
            raise Exception('approveMulti failed - approve error!')
    return True


def allowance(owner, spender, tokenId):
    """
    :param owner:
    :param spender:
    :param tokenId:
    :return:
    """
    key = concatkey(concatkey(concatkey(tokenId, APPROVE), owner), spender)
    return Get(GetContext(), key)


def transferFrom(spender, fromAcct, toAcct, tokenId, amount):
    """
    :param tokenId: this tokenId token should be approved by its owner to toAcct
    :param toAcct: spender
    :param amount: False or True
    :return:
    """
    RequireWitness(spender)
    RequireScriptHash(spender)
    RequireScriptHash(fromAcct)
    RequireScriptHash(toAcct)
    Require(checkTokenId(tokenId))

    fromKey = concatkey(concatkey(tokenId, BALANCE), fromAcct)
    fromBalance = Get(GetContext(), fromKey)
    Require(fromBalance >= amount)

    toKey = concatkey(concatkey(tokenId, BALANCE), toAcct)
    toBalance = Get(GetContext(), toKey)

    approvedKey = concatkey(concatkey(concatkey(tokenId, APPROVE), fromAcct), spender)
    approvedAmount = Get(GetContext(), approvedKey)

    if amount > fromBalance:
        raise Exception('fromAcct does not have enough tokens')
    elif amount == fromBalance:
        Delete(GetContext(), approvedKey)
        Delete(GetContext(), fromBalance - amount)
    else:
        Put(GetContext(), approvedKey, approvedAmount - amount)
        Put(GetContext(), fromKey, fromBalance - amount)

    Put(GetContext(), toKey, toBalance + amount)

    # tokenName = Get(GetContext(), concatkey(tokenId, NAME))

    # Notify(["transfer", fromAcct, toAcct, tokenId, amount])
    TransferEvent(fromAcct, toAcct, tokenId, amount)

    return True


def transferFromMulti(args):
    """
    multiple transferFrom
    :param args: args:[[spender1, fromAcct1, toAcct1, tokenId1, amount1],[spender2, fromAcct2, toAcct2, tokenId2, amount2]]
    :return:
    """
    for p in args:
        if len(p) != 5:
            raise Exception('transferFromMulti failed - input error!')
        if transferFrom(p[0], p[1], p[2], p[3], p[4]) == False:
            raise Exception('transferFromMulti failed - transfer error!')
    return True


def compound(acct):
    """
    Compound the first seven tokens into the precious (8-th) token,
    the first seven tokens of acct will disappear and the precious tokens will be generated
    :param acct:
    :return:
    """
    RequireWitness(acct)
    RequireScriptHash(acct)
    normalIndex = [0, 1, 2, 3, 4, 5, 6]
    normalBalances = [0, 0, 0, 0, 0, 0, 0]
    # here minValue should be the maximum totalSupply
    minValue = 700
    for index in normalIndex:
        tmpBalance = balanceOf(acct, TOKEN_ID_LIST[index])
        normalBalances[index] = tmpBalance
        if minValue > tmpBalance:
            minValue = tmpBalance

    for index in normalIndex:
        tmpKey = concatkey(concatkey(TOKEN_ID_LIST[index], BALANCE), acct)
        Put(GetContext(), tmpKey, normalBalances[index] - minValue)
        Put(GetContext(), concatkey(TOKEN_ID_LIST[index], TOTAL_SUPPLY), totalSupply(TOKEN_ID_LIST[index]) - minValue)

        # tokenName = Get(GetContext(), concatkey(TOKEN_ID_LIST[index], NAME))

        # Notify(["transfer", acct, '', TOKEN_ID_LIST[index], minValue])
        TransferEvent(acct, '', TOKEN_ID_LIST[index], minValue)

    preciousTokenID = TOKEN_ID_LIST[7]

    preciousTokenSupply = totalSupply(preciousTokenID)

    Put(GetContext(), concatkey(preciousTokenID, TOTAL_SUPPLY), preciousTokenSupply + minValue)

    Put(GetContext(), concatkey(concatkey(preciousTokenID, BALANCE), acct), balanceOf(acct, preciousTokenID) + minValue)

    tokenName = Get(GetContext(), concatkey(preciousTokenID, NAME))

    # Notify(["transfer", '', acct, preciousTokenID, minValue])
    TransferEvent('', acct, preciousTokenID, minValue)

    return True

def concatkey(str1, str2):
    return concat(concat(str1, '_'), str2)

#################### For testing usage only starts ######################

def init():
    '''
    based on your requirements, initialize the tokens
    :return:
    '''
    if not Get(GetContext(), INITED) and CheckWitness(admin) == True:
        tt = createMultiTypeToken()
        if tt == True:
            Put(GetContext(), INITED, 'TRUE')
            return True
        raise Exception("init error")

    return False



def createMultiTypeToken():
    Index = [0, 1, 2, 3, 4, 5, 6, 7]
    tokenNameList = ['name1', 'name2', 'name3', 'name4', 'name5', 'name6', 'name7', 'name8']
    tokenSymbolList = ['PS1', 'PS2', 'PS3', 'PS4', 'PS5', 'PS6', 'PS7', 'PS8']
    tokenSupplyList = [100, 200, 300, 400, 500, 600, 700, 0]

    for index in Index:
        # get name, symbol, totalsupply
        tokenName = tokenNameList[index]
        tokenSymbol = tokenSymbolList[index]
        tokenTotalSupply = tokenSupplyList[index]

        tokenId = TOKEN_ID_LIST[index]

        # initiate token name
        Put(GetContext(), concatkey(tokenId, NAME), tokenName)
        # initiate token symbol
        Put(GetContext(), concatkey(tokenId, SYMBOL), tokenSymbol)
        # initiate token totalSupply
        Put(GetContext(), concatkey(tokenId, TOTAL_SUPPLY), tokenTotalSupply)

        # transfer all the tokens to admin
        Put(GetContext(), concatkey(concatkey(tokenId, BALANCE), admin), tokenTotalSupply)

        # Notify(['transfer', '', admin, tokenId, tokenTotalSupply])
        TransferEvent('', admin, tokenId, tokenTotalSupply)

    return True

def checkTokenId(tokenId):
    # here we check if the tokenId is legal with the help of getting its name
    if Get(GetContext(), concatkey(tokenId, NAME)):
        return True
    else:
        return False

#################### For testing usage only ends ######################