import ccxt
import operator
import urllib
import ujson as json
import json
import requests
from contextlib import closing
from collections import defaultdict

resultRewardUSD = {  }
resultRewardBTC = { }
resultRewardPerDay = { }
coinsBlockRewards = { }
coins = {  }
idCoins = {  }
diff = { }
algoDict = defaultdict(set)
fllname = { }

#creo un dizionario di tutte le criptovalute e i relativi algoritmi -> coins
#creo un dizionario con il simbolo della criptovaluta e l'id di criptocompare per la successiva query di block reward
#escludo le criptovalute che hanno N/A come algoritmo

def parseCoinsByAlgorithm():
    url = "https://min-api.cryptocompare.com/data/all/coinlist"
    r = requests.get(url)
    data = r.json()
    data = data["Data"]
    syms = data.keys()

    for coin in syms:
        id_coin  =  data[coin]["Id"]
        algo = str(data[coin]["Algorithm"])
        coinname = data[coin]["CoinName"]
        
        if algo != "N/A":
            fllname[coin] = coinname
            coins[coin] = algo
            idCoins[coin] = id_coin
            algoDict[str(algo)].add(str(coin))

    
def getBlockReward(algoDict):
    #statistiche
    count = 0
    tot = len(algoDict)
    
    for i in algoDict:
        num = idCoins[i]
        url = "https://www.cryptocompare.com/api/data/coinsnapshotfullbyid/?id=" + str(num)
        r = requests.get(url)
        data = r.json()
        test = 0.0

        if ((data["Data"]["General"]["BlockReward"] == test) or (isinstance(data["Data"]["General"]["BlockReward"],unicode) == True)):
            count = count + 1
        else:
            coinsBlockRewards[i] = data["Data"]["General"]["BlockReward"]
            count = count + 1

def getDifficulty(algoDict):
    count = 0
    tot = len(algoDict)

    for coin in algoDict:
        s = coin.lower()
        url = "https://chainz.cryptoid.info/"+str(s)+"/api.dws?q=getdifficulty"
        r = requests.get(url)

        if r.status_code == 404:
            count = count + 1
            s = fllname[coin].lower()
            s.replace(" ", "")
            url = "https://www.coincalculators.io/api.aspx?name="+s

            r= requests.get(url)
            test = r.headers['content-type']
            if test == 'text/html':
                pass
            else:
                r = requests.get(url).json()
                diff[coin] = r["currentDifficulty"]
                coinsBlockRewards[coin] = r["blockReward"]

        else:
            data = r.json()
            diff[coin] = data
            count = count + 1

    

def getNetworkhashrate(coins):
    return 

def getUSDPrice(coin, btcusdprice):
    url = "https://min-api.cryptocompare.com/data/price?fsym="+coin+"&tsyms=USD"
    r = requests.get(url)
    if r.status_code == 404:
        cryptopia  = ccxt.cryptopia()
        cryptopia_markets = cryptopia.load_markets()
        data = cryptopia.fetch_ticker(coin+'/BTC')
        return btcusdprice*data["info"]["LastPrice"]
    else:
        data = r.json()
        return data["USD"]


def getCurrentBTCPrice():
    url = "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD"
    r = requests.get(url)
    p = r.json()
    btcusdprice = p["USD"]
    return btcusdprice

def mining_profitability(algorithm, hashrateMHS, diff, blockreward, resultRewardUSD, resultRewardBTC, resultRewardPerDay):
    btcusdprice = getCurrentBTCPrice()
    parseCoinsByAlgorithm()

    getBlockReward(algoDict[algorithm])
    getDifficulty(algoDict[algorithm])

    for coin in algoDict[algorithm]:

        if(algorithm=="SHA256"):
            blockreward = getBlockReward(brewards, coin)
            std_p = 86400
            parz = hashrateMHS*blockreward*std_p*1000000
            difficulty = getDifficulty(diff, coin)
            den = difficulty * 4294967296

            tot = ( parz / den )
            coinpriceusd= getUSDPrice(coin)
            revenue = tot*coinpriceusd
            ratioUSD = str(revenue / hashrateMHS) + " $/MHs"
            ratioBTC = str( tot / hashrateMHS) + " BTC/MHs"

            # risultati nei dizionari
            resultRewardUSD['BTC'] = ratioUSD
            dizBTC['BTC'] = ratioBTC
            dizperDay['BTC'] = str(revenue) + " $/day"

            #reordering
            resultRewardUSD = sorted(resultRewardUSD.items(), key=operator.itemgetter(1), reverse=True)
            dizBTC = sorted(dizBTC.items(), key=operator.itemgetter(1), reverse=True)
            dizperDay = sorted(dizperDay.items(), key=operator.itemgetter(1), reverse=True)

        elif(algorithm=="Ethash"):
            std_p = 86400
            try:
                blockreward = coinsBlockRewards[coin]
                difficulty = diff[coin]
                tot = ((hashrateMHS*blockreward*std_p*1000000) / difficulty)
                print coin
                coinpriceUSD= getUSDPrice(coin, btcusdprice)
                resultRewardUSD[coin] = round(tot*coinpriceUSD,2)
            except KeyError:
                pass

            
        elif(algorithm=="Cryptonight"):
            diff = getDifficulty()
            blockreward = getBlockReward()
            networkhashrate = getNetworkhashrate()
            tot =   ( ( hashrateMHS * blockreward * 720 ) / networkhashrate )
            print(tot)
            xmrprice = 136
            resultRewardUSD['XMR'] = str(tot*xmrprice) + " $/day"

        elif(algorithm == "Equihash"):
            blockreward = getBlockReward(algoDict["Equihash"])
            pool_fee = 0
            diff = getDifficulty()
            tot = ((hashrate * blockreward) / diff) * (1 - pool_fee) * 3600
            resultRewardUSD['ZEC'] = str(tot) + " $/day"
            print(resultRewardUSD)

        elif(algorithm == "Scrypt"):
            R = getBlockReward()
            diff = getDifficulty()
            T = ( (diff * 2**32 ) / (hashrateMHS * 8.64e7) )
            coinsmined = R/T
            xvgprice = 0.02
            tot = coinsmined*xvgprice
            resultRewardUSD['XVG'] = str(tot) + " $/day"
            print(resultRewardUSD)

        elif(algorithm == "X11"):
            R = getBlockReward()
            D = getDifficulty()
            coinsMined = hashrateMHS * R * 86400 * 10^6 / (Difficulty * 2^32)
            dashprice = 1
            tot = dashprice*coinsMined
            resultRewardUSD['DASH'] = str(tot) + " $/day"
            print(resultRewardUSD)

    res = sorted(resultRewardUSD.items(), key=operator.itemgetter(1), reverse=True)
    print res
    tot = len(resultRewardUSD)
    print "Found " + str(tot) + " coins on " + algorithm

mining_profitability("Ethash", 108.00, diff, coinsBlockRewards, resultRewardUSD, resultRewardBTC, resultRewardPerDay)



    
