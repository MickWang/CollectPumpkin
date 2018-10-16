"""
A sample of OEP5 smart contract
"""
from boa.interop.System.Storage import GetContext, Get, Put, Delete
from boa.interop.System.Runtime import CheckWitness, GetTime, Notify, Serialize, Deserialize
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash
from boa.builtins import ToScriptHash, sha256, concat
from mycontracts.libs.SafeCheck import Require, RequireScriptHash, RequireWitness

from boa.interop.System.Runtime import Serialize, Deserialize




# modify to the admin address
admin = ToScriptHash('AQf4Mzu1YJrhz9f3aRkkwSm9n3qhXGSh4p')



# TOKEN_ID1 is used to identify different tokens, to help store the token name, token symbol and balance
TOKEN_ID1 = bytearray('b\x01')
TOKEN_ID2 = bytearray('b\x02')
TOKEN_ID3 = bytearray('b\x03')
TOKEN_ID4 = bytearray('b\x04')
TOKEN_ID5 = bytearray('b\x05')
TOKEN_ID6 = bytearray('b\x06')
TOKEN_ID7 = bytearray('b\x07')
TOKEN_ID8 = bytearray('b\x08')

TOKEN_ID_LIST = [TOKEN_ID1, TOKEN_ID2, TOKEN_ID3, TOKEN_ID4, TOKEN_ID5, TOKEN_ID6, TOKEN_ID7, TOKEN_ID8]

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
    if operation == 'name':
        if len(args) != 1:
            return False
        tokenID = args[0]
        return name(tokenID)
    if operation == 'symbol':
        if len(args) != 1:
            return False
        tokenID = args[0]
        return symbol(tokenID)
    if operation == 'balanceOf':
        if len(args) != 2:
            return False
        account = args[0]
        tokenID = args[1]
        return balanceOf(account, tokenID)
    if operation == 'transfer':
        if len(args) != 4:
            return False
        fromAcct = args[0]
        toAcct = args[1]
        tokenID = args[2]
        amount = args[3]
        return transfer(fromAcct, toAcct, tokenID, amount)
    if operation == 'transferMulti':
        return transferMulti(args)
    if operation == 'approve':
        if len(args) != 4:
            return False
        owner = args[0]
        spender = args[1]
        tokenID = args[2]
        amount = args[3]
        return approve(owner, spender, tokenID, amount)
    if operation == 'transferFrom':
        if len(args) != 5:
            return False
        owner = args[0]
        fromAcct = args[1]
        toAcct = args[2]
        tokenID = args[3]
        amount = args[4]
        return transferFrom(owner, fromAcct, toAcct, tokenID, amount)
    if operation == "compound":
        if len(args) != 1:
            return False
        account = args[0]
        return compound(account)
    ############ For testing usage only starts ############
    if operation == 'init':
        if len(args) != 0:
            return False
        return init()
    if operation == "getApproval":
        if len(args) != 3:
            return False
        owner = args[0]
        spender = args[1]
        tokenID = args[2]
        return getApproval(owner, spender, tokenID)
    ############ For testing usage only ends ############
    return False


def name(tokenID):
    """
    :param tokenID: helps to format name key = tokenID + NAME
    :return: name of the token with tokenID
    """
    return Get(GetContext(), concatkey(tokenID, NAME))


def symbol(tokenID):
    """
    :param tokenID: helps to format symbol key = tokenID + SYMBOL
    :return: symbol of token with tokenID
    """
    return Get(GetContext(), concatkey(tokenID, SYMBOL))


def totalSupply(tokenID):
    """
    :param tokenID:  helps to format totalSupply key = tokenID + TOTAL_SUPPLY
    :return: total supply of token with tokenID
    """
    return Get(GetContext(), concatkey(tokenID, TOTAL_SUPPLY))


def balanceOf(acct, tokenID):
    """
    get balance of accout in terms of token with the tokenID
    :param acct: used to check the acct balance
    :param tokenID: the tokenID determines which token balance of acct needs to be checked
    :return: the balance of acct in terms of tokenID tokens
    """
    return Get(GetContext(), concatkey(concatkey(tokenID, BALANCE), acct))


def transfer(fromAcct, toAcct, tokenID, amount):
    """
    transfer amount of tokens in terms of tokenPrefix token from fromAcct to the toAcct
    :param fromAcct:
    :param toAcct:
    :param tokenID:
    :param amount:
    :return:
    """
    RequireWitness(fromAcct)
    Require(checkTokenPrefix(tokenID))
    RequireScriptHash(fromAcct)
    RequireScriptHash(toAcct)

    balanceKey = concatkey(tokenID, BALANCE)
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

    tokenName = Get(GetContext(), concatkey(tokenID, NAME))

    Notify(['transfer', fromAcct, toAcct, tokenName, amount])

    return True


def transferMulti(args):
    '''
    multi transfer
    :param args:[[fromAccount1, toAccount1, tokenID1, amount1],[fromAccount2, toAccount2, tokenID2, amount2]]
    :return: True or raise exception
    '''
    for p in args:
        if len(p) != 4:
            raise Exception('transferMulti failed - input error!')
        if transfer(p[0], p[1], p[2], p[3]) == False:
            raise Exception('transferMulti failed - transfer error!')
    return True


def approve(owner, spender, tokenID, amount):
    """
    approve amount of the tokenID token to toAcct address, it can overwrite older approved amount
    :param owner:
    :param spender:
    :param tokenID:
    :param amount:
    :return:
    """
    RequireWitness(owner)
    RequireScriptHash(owner)
    RequireScriptHash(spender)
    Require(checkTokenPrefix(tokenID))

    ownerBalance = balanceOf(owner, tokenID)
    Require(ownerBalance >= amount)

    key = concatkey(concatkey(concatkey(tokenID, APPROVE), owner), spender)
    Put(GetContext(), key, amount)

    tokenName = Get(GetContext(), concatkey(tokenID, NAME))

    Notify(['approval', owner, spender, tokenName, amount])

    return True


def transferFrom(spender, fromAcct, toAcct, tokenID, amount):
    """
    :param tokenID: this tokenID token should be approved by its owner to toAcct
    :param toAcct: spender
    :param amount: False or True
    :return:
    """
    RequireWitness(spender)
    RequireScriptHash(spender)
    RequireScriptHash(fromAcct)
    RequireScriptHash(toAcct)
    Require(checkTokenPrefix(tokenID))

    fromKey = concatkey(concatkey(tokenID, BALANCE), fromAcct)
    fromBalance = Get(GetContext(), fromKey)
    Require(fromBalance >= amount)

    toKey = concatkey(concatkey(tokenID, BALANCE_PREFIX), toAcct)
    toBalance = Get(GetContext(), toKey)

    approvedKey = concatkey(concatkey(concatkey(tokenID, APPROVE_PREFIX), fromAcct), spender)
    approvedAmount = Get(GetContext(), approvedKey)

    if amount > fromBalance:
        raise Exception('fromAcct does not have enough tokens')
    elif amount == fromBalance:
        Delete(ctx, approvedKey)
        Delete(ctx, fromKey)
    else:
        Put(GetContext(), approvedKey, approvedAmount - amount)
        Put(GetContext(), fromKey, fromBalance - amount)

    Put(GetContext(), toKey, toBalance + amount)

    tokenName = Get(GetContext(), concatkey(tokenID, NAME))

    Notify(["transfer", fromAcct, toAcct, tokenName, amount])

    return True


def compound(acct):
    RequireWitness(acct)
    RequireScriptHash(acct)
    normalIndex = [1, 2, 3, 4, 5, 6, 7]
    normalBalances = [0, 0, 0, 0, 0, 0, 0]
    # here minValue should be the maximum totalSupply
    minValue = 700
    for index in normalIndex:
        tmpBalance = balanceOf(acct, pumpkinKindsID[index])
        normalBalances[index] = tmpBalance
        if minValue > tmpBalance:
            minValue = tmpBalance

    for index in normalIndex:
        tmpKey = concatkey(concatkey(pumpkinKindsID[index], BALANCE_PREFIX), acct)
        Put(GetContext(), tmpKey, normalBalances[index] - minValue)
        Put(GetContext(), concatkey(pumpkinKindsID[index], TOTAL_SUPPLY), totalSupply(pumpkinKindsID[index]) - minValue)
        pumpkinname = Get(GetContext(), concatkey(pumpkinKindsID[index], NAME))
        Notify(["transfer", acct, '', pumpkinname, minValue])

    preciousTokenPrefix = pumpkinKindsID[7]

    preciousPumpkinSupply = totalSupply(preciousTokenPrefix)

    Put(GetContext(), concatkey(preciousTokenPrefix, TOTAL_SUPPLY), preciousPumpkinSupply + minValue)

    Put(GetContext(), concatkey(preciousTokenPrefix), balanceOf(acct, preciousTokenPrefix) + minValue)

    preciouspumpkinname = Get(GetContext(), concatkey(preciousTokenPrefix, NAME))

    Notify(["transfer", '', acct, preciouspumpkinname, minValue])

    return True

def concatkey(str1, str2):
    return concat(concat(str1, '_'), str2)

#################### For testing usage only starts ######################

def init():
    '''
    based on your requirements, initialize the tokens
    :return:
    '''
    Notify(["111_init"])
    if not Get(ctx, INITED) and CheckWitness(admin) == True:
        tt = createMultiKindsPumpkin()
        if tt == True:
            Put(ctx, INITED, 'TRUE')
            return True
        raise Exception("init error")
    else:
        Notify(["222_init"])

    return False

def getApproval(owner, spender, tokenID):
    """
    :param owner:
    :param spender:
    :param tokenID:
    :return:
    """
    key = concatkey(concatkey(concatkey(tokenID, APPROVE_PREFIX), owner), spender)
    return Get(GetContext(), key)


def createMultiKindsPumpkin():
    Index = [1, 2, 3, 4, 5, 6, 7, 8]
    # pumpkinKindsID = [PUMPKIN_ID1, PUMPKIN_ID2, PUMPKIN_ID3,PUMPKIN_ID4, PUMPKIN_ID5, PUMPKIN_ID6, PUMPKIN_ID7, PUMPKIN_ID8]
    pumpkinKindsName = ['name1', 'name2', 'name3', 'name4', 'name5', 'name6', 'name7', 'name8']
    pumpkinKindsSymbol = ['PS1', 'PS2', 'PS3', 'PS4', 'PS5', 'PS6', 'PS7', 'PS8']
    pumpkinKindsTotalSupply = [100, 200, 300, 400, 500, 600, 700, 0]

    for index in Index:
        # get name, symbol, totalsupply
        pumpkinname = pumpkinKindsName[index]
        pumpkinsymbol = pumpkinKindsSymbol[index]
        pumpkintotalsupply = pumpkinKindsTotalSupply[index]

        pumpkinprefix = pumpkinKindsID[index]

        # initiate token name
        Put(GetContext(), concatkey(pumpkinprefix, NAME), pumpkinname)
        # initiate token symbol
        Put(GetContext(), concatkey(pumpkinprefix, SYMBOL), pumpkinsymbol)
        # initiate token totalSupply
        Put(GetContext(), concatkey(pumpkinprefix, TOTAL_SUPPLY), pumpkintotalsupply)

        # transfer all the pumpkin tokens to admin
        Put(GetContext(), concatkey(concatkey(pumpkinprefix, BALANCE_PREFIX), admin), pumpkintotalsupply)
        Notify(['transfer', '', admin, pumpkinname, pumpkintotalsupply])
    return True

def checkTokenPrefix(tokenPrefix):
    # here we check if the tokenPrefix is legal with the help of getting its name
    if Get(GetContext(), concatkey(tokenPrefix, NAME)):
        return True
    else:
        return False

#################### For testing usage only ends ######################