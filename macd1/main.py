# Mateusz Fydrych s193410 ®2024
import os
import matplotlib.pyplot as plt
import pandas as pd


CURRENCY_CALATALOG = './currencies/'
NAME_OF_FILE = 'nvda_us_d.csv'
column_names = ["Data", "Otwarcie", "Najwyzszy", "Najnizszy", "Zamkniecie", "Wolumen"]
STARTING_MONEY = 1000
SHORT_MEAN = 12
LONG_MEAN = 26
SIGNAL_MEAN = 9
TREND_MEAN = 50
BUY_SIGN = 'o'
SELL_SIGN = 'x'
BUY_SIGN_SIZE = 25
SELL_SIGN_SIZE = 20


def getData(nazwa_pliku):
    data = pd.read_csv(CURRENCY_CALATALOG + nazwa_pliku)
    return data

def getCurrencyList():
    return [file for file in os.listdir(CURRENCY_CALATALOG) if file.endswith('.csv')]

def getXTicksLength(chart):
    return int(len(chart) / 8)

def printPricePlot(chart, name_of_file):
    plt.subplot(211)
    plt.plot(chart[column_names[0]], chart[column_names[-2]])
    trendMean = getEMA(chart[column_names[-2]], TREND_MEAN)
    plt.plot(chart[column_names[0]], trendMean, linewidth = 1)
    plt.legend(['Price', 'Trend EMA'])
    plt.xlabel('Date')
    plt.ylabel('Closed price')
    xTicks = getXTicksLength(chart)
    plt.xticks(chart[column_names[0]][::xTicks])
    plt.grid(True)
    plt.title(f'Price of {name_of_file}')

#funckja recznie wyliczajaca EMA
def getEMA(chart, mean):
    alpha = 2 / (mean + 1)
    emaResult = []
    s0 = chart[0]
    emaResult.append(s0)
    for i in range(1, len(chart)):
        s = alpha * chart[i] + (1 - alpha) * s0
        emaResult.append(s)
        s0 = s
    print(emaResult)
    return emaResult

def getMACD(chart):
    short_ema = getEMA(chart, SHORT_MEAN)
    long_ema = getEMA(chart, LONG_MEAN)
    macd = []
    for i in range(len(short_ema)):
        macd.append(short_ema[i] - long_ema[i])
    return macd

def getSignal(chart):
    macd = getMACD(chart)
    signal = getEMA(macd, SIGNAL_MEAN)
    return signal

def printMACDPlot(chart, date):
    plt.subplot(212)
    plt.plot(date, getMACD(chart), linewidth = 1)
    plt.plot(date, getSignal(chart), linewidth = 1.2)
    xTicks = getXTicksLength(chart)
    plt.xticks(date[::xTicks])
    min_price = min(getMACD(chart))
    max_price = max(getMACD(chart))
    zero_price = 0
    plt.yticks([min_price, zero_price, max_price])
    plt.legend(['MACD', 'Signal EMA'])
    plt.grid(True)
    plt.tick_params(axis='y', colors='y')
    plt.tick_params(axis='x', colors='y')

def printPlot(chart, name_of_file):
    plt.figure()
    printPricePlot(chart, name_of_file)
    printMACDPlot(chart[column_names[-2]], chart[column_names[0]])
    plt.show()

def printTransactionSignals(chart, transactionSignals, name_of_file):
    plt.figure()
    plt.title(f'Transaction signals of {name_of_file}')
    plt.subplot(111)
    plt.plot(chart[column_names[0]], chart[column_names[-2]], linewidth = 1.2)
    trendMean = getEMA(chart[column_names[-2]], TREND_MEAN)
    plt.plot(chart[column_names[0]], trendMean, linewidth = 1)
    #legend on the top left corner
    plt.legend(['Price', 'Trend EMA'], loc='upper left')
    plt.xlabel('Date')
    plt.ylabel('Closed price')
    xTicks = getXTicksLength(chart)
    plt.xticks(chart[column_names[0]][::xTicks])
    plt.grid(False)
    plt.title(f'Price of {name_of_file}')
    for i in range(len(transactionSignals)):
        if transactionSignals[i] == 0:
            plt.scatter(chart[column_names[0]][i], chart[column_names[-2]][i], color='green', s=BUY_SIGN_SIZE,
                        label='Buy long', marker=BUY_SIGN)
        elif transactionSignals[i] == 1:
            plt.scatter(chart[column_names[0]][i], chart[column_names[-2]][i], color='red', s=BUY_SIGN_SIZE,
                        label='Buy short', marker=BUY_SIGN)
        elif transactionSignals[i] == 2:
            plt.scatter(chart[column_names[0]][i], chart[column_names[-2]][i], color='black', s=SELL_SIGN_SIZE,
                        label='Sell long', marker=SELL_SIGN)
        elif transactionSignals[i] == 3:
            plt.scatter(chart[column_names[0]][i], chart[column_names[-2]][i], color='orange', s=SELL_SIGN_SIZE,
                        label='Sell short', marker=SELL_SIGN)
    plt.show()

def printAcountValueHistory(accountValueHistory):
    plt.figure()
    plt.plot(accountValueHistory)
    plt.xlabel('Day number')
    plt.ylabel('Account value')
    plt.grid(True)
    plt.title('Account value history')
    plt.show()

def calculateTransactionMoments(chart):
    macd = getMACD(chart[column_names[-2]])
    signal = getSignal(chart[column_names[-2]])
    trendMean = getEMA(chart[column_names[-2]], TREND_MEAN)
    transactionSignals = []
    isInvested = False
    isLongPosition = False
    # 0 - buy long, 1 - buy short, 2 - sell long, 3 - sell short, 5 - no action
    for i in range(len(macd)):
        #on the last day we need to sell all stocks
        if i == len(macd) - 1 and isInvested:
            if isLongPosition:
                transactionSignals.append(2)

            else:
                transactionSignals.append(3)
            break
        if isInvested:
            if isLongPosition:
                if macd[i] < signal[i] and trendMean[i] > chart[column_names[-2]][i]:
                    transactionSignals.append(2)
                else:
                    transactionSignals.append(5)
                    continue
            else:
                if macd[i] > signal[i] and trendMean[i] < chart[column_names[-2]][i]:
                    transactionSignals.append(3)
                else:
                    transactionSignals.append(5)
                    continue
            isInvested = False
        else:
            if macd[i] > signal[i] and macd[i] > 0:
                transactionSignals.append(0)
                isInvested = True
                isLongPosition = True
            elif macd[i] < signal[i] and macd[i] < 0:
                transactionSignals.append(1)
                isInvested = True
                isLongPosition = False
            else:
                transactionSignals.append(5)
    print(transactionSignals)
    return transactionSignals

def getTransactionResults(chart, name_of_file):
    transactionSignals = calculateTransactionMoments(chart)
    printTransactionSignals(chart, transactionSignals, name_of_file)
    money = STARTING_MONEY
    inStock = 0
    howManyPercentofMoney = 0.2
    buyLongDays, buyShortDays, sellLongDays, sellShortDays, noActionDays = 0, 0, 0, 0, 0
    accountValueHistory = []
    # 0 - buy long, 1 - buy short, 2 - sell long, 3 - sell short, 5 - no action
    for i in range(len(transactionSignals)):
        if transactionSignals[i] == 0:
            if money > 0:
                toInvest = float(money * howManyPercentofMoney)
                inStock = float(toInvest / chart[column_names[-2]][i])
                money -= toInvest
                buyLongDays += 1
        elif transactionSignals[i] == 1:
            if money > 0:
                toInvest = float(money * howManyPercentofMoney)
                inStock = float(toInvest / chart[column_names[-2]][i])
                money -= toInvest
                buyShortDays += 1
        elif transactionSignals[i] == 2:
            if inStock > 0:
                money += inStock * chart[column_names[-2]][i]
                inStock = 0
                sellLongDays += 1
        elif transactionSignals[i] == 3:
            if inStock > 0:
                money += inStock * chart[column_names[-2]][i]
                inStock = 0
                sellShortDays += 1
        elif transactionSignals[i] == 5:
            noActionDays += 1
        accountValueHistory.append(money + inStock * chart[column_names[-2]][i])
        print(f'Money: {money}, inStock: {inStock}, price: {chart[column_names[-2]][i]}')
    if inStock > 0:
        money += inStock * chart[column_names[-2]][len(chart) - 1]
        sellLongDays += 1
    print(f'Final account value: {money:.2f}')
    printAcountValueHistory(accountValueHistory)
    print(f'Buy long days: {buyLongDays}'
          f', buy short days: {buyShortDays}'
          f', sell long days: {sellLongDays}'
          f', sell short days: {sellShortDays}'
          f', no action days: {noActionDays}')

if __name__ == '__main__':
    print(getCurrencyList())
    chart = getData(NAME_OF_FILE)
    print(chart.head(22))
    nazwaWaluty = NAME_OF_FILE.split('_')[0]
    printPlot(chart, nazwaWaluty)
    getTransactionResults(chart, nazwaWaluty)
    # print(getData('wig20_q.csv').head(22)["Data"][0])
