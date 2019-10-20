import matplotlib.pyplot as plt
from sklearn.metrics import *
import seaborn as sb
import pandas as pd
import numpy as np 
from data_processing import *

res_path = '../Results/'
models = ['CNN','RNN','LSTM','Resnet','Densenet']
def computeConfMatrix(ytrue,ypred,title):
    cm = confusion_matrix(ytrue, ypred)
    tn, fp, fn, tp = confusion_matrix(ytrue,ypred).ravel()
    sb.set(font_scale=1.4)
    labels = [0,1]
    cm_df = pd.DataFrame(cm,columns= labels,index=labels)
    sb.heatmap(cm_df, annot=True,annot_kws={"size": 16},fmt='d')
    plt.ylabel('Actual labels')
    plt.xlabel('Predicted labels') 
    plt.title('Confusion Matrix for ' + title)
    plt.show()
    return cm,tn, fp, fn, tp
    


def plotROC(ytrue,scores,title,pos_class = 1):    
    fpr, tpr, _ = roc_curve(ytrue, scores[:,pos_class], pos_label=pos_class)
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr,label=str(pos_class) + ' as +ve class(auc = %0.2f)' % roc_auc)
    lw = 2
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC curve for '+title)
    legend = plt.legend(loc="lower right",frameon=True)
    legend.get_frame().set_edgecolor('black')
    plt.show()
    return fpr, tpr



def plotPrecisionRecall(ytrue,scores,title,pos_class = 1):    
    precision, recall, _ = precision_recall_curve(ytrue, scores[:,pos_class], pos_label=pos_class)
    average_precision = average_precision_score(ytrue, scores[:,pos_class])
    plt.plot(recall, precision,label=str(pos_class) + ' as +ve class(ap = %0.2f)' % average_precision)
    #lw = 2
    #plt.plot([0, 1], [0, 1])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve for '+title)
    legend = plt.legend(loc="upper right",frameon=True)
    legend.get_frame().set_edgecolor('black')
    plt.show()
    return precision, recall 

    
    
def computeMetrics(tp,tn,fp,fn):
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    sensitivity = recall
    specificity = tn / (tn + fp)
    tpr = recall
    fpr = fp / (fp + tn)
    f1score = 2*precision*recall/(precision+recall)
    return precision, recall, sensitivity, specificity, tpr,fpr, f1score


def saveResults(ytrue,ypred,scores,fpr,tpr,precision, recall, title):
    print('saving...')
    file_path = res_path +title
    np.savetxt(file_path+'_ytrue.csv', ytrue, delimiter=",")
    np.savetxt(file_path+'_ypred.csv', ypred, delimiter=",")
    np.savetxt(file_path+'_scores.csv', scores, delimiter=",")
    np.savetxt(file_path+'_fpr.csv', fpr, delimiter=",")
    np.savetxt(file_path+'_tpr.csv', tpr, delimiter=",")
    np.savetxt(file_path+'_precision.csv', precision, delimiter=",")
    np.savetxt(file_path+'_recall.csv', recall, delimiter=",")
    print('file saved !!!!!')
    
    
def plotAllROCs(wind_size,pos_class=1):
    for model in models: 
        print(model)
        file_path_fpr = res_path+str(wind_size)+'_'+model+'_fpr.csv'
        file_path_tpr = res_path+str(wind_size)+'_'+model+'_tpr.csv'
        fpr = pd.read_csv(file_path_fpr, sep=',',header=None).values.tolist()
        tpr = pd.read_csv(file_path_tpr, sep=',',header=None).values.tolist()
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr,label= model + '(auc = %0.2f)' % roc_auc)
    lw = 2
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC curves for all the models with '+ str(pos_class) + ' as +ve class')
    legend = plt.legend(loc="center left",frameon=True,bbox_to_anchor=(1,0.5))
    legend.get_frame().set_edgecolor('black')
    plt.show()


    
def plotAllPRs(wind_size,pos_class=1):
    for model in models: 
        file_path_precision =  res_path+str(wind_size)+'_'+model+'_precision.csv'
        file_path_recall =  res_path+str(wind_size)+'_'+model+'_recall.csv'
        file_path_ytrue =  res_path+str(wind_size)+'_'+model+'_ytrue.csv'
        file_path_scores =  res_path+str(wind_size)+'_'+model+'_scores.csv'
        precision = pd.read_csv(file_path_precision, sep=',',header=None).values.tolist()
        recall = pd.read_csv(file_path_recall, sep=',',header=None).values.tolist()
        ytrue = pd.read_csv(file_path_ytrue, sep=',',header=None).values.tolist()
        scores = np.asarray(pd.read_csv(file_path_scores, sep=',',header=None).values.tolist())
        average_precision = average_precision_score(ytrue, scores[:,pos_class])
        plt.plot(recall, precision,label= model + '(ap = %0.2f)' % average_precision)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curves for all the models with '+ str(pos_class) + ' as +ve class')
    legend = plt.legend(loc="center left",frameon=True,bbox_to_anchor=(1,0.5))
    legend.get_frame().set_edgecolor('black')
    plt.show()
    
    
def getStocksList(data_df):
    g = data_df.groupby('SYMBOL')
    df1 = g.count().reset_index()
    df1 = df1[['SYMBOL','CLOSE']].reset_index()
    df1.rename(columns= {'CLOSE':0},inplace=True)
    stocks_list = df1.loc[df1[0]>807]['SYMBOL'].values.tolist()
    #stocks_list = list(g.groups.keys())
    print('length : ' , len(stocks_list))
    #print(stocks_list)
    return stocks_list


def compAnnualReturns(stock,ypred,data_df,window_size,limit,sub_one=True):
    _,_,stock_table = getWindowedData(data_df,stock,window_size)
    stock_table_df = pd.DataFrame(stock_table,columns = ['CLOSE','OPEN','HIGH','LOW','CONTRACTS','DATE','Stock_Class'])
    stock_table_df  = stock_table_df[limit:]
    if sub_one:
        stock_table_df  = stock_table_df[0:stock_table_df.shape[0]-1]
    stock_table_df['Predicted'] = ypred
    
    #print(stock_table_df.head(2))
    i = 0
    startCapital = 100000.0
    totalTransactionLength = 0
    buyPoint = 0
    sellPoint= 0
    gain = 0.0
    totalGain = 0.0
    money = startCapital
    shareNumber = 0.0
    moneyTemp = 0.0
    maximumMoney = 0.0 
    minimumMoney = startCapital
    maximumGain = 0.0
    maximumLost = 100.0
    totalPercentProfit = 0.0
    transactionCount = 0
    successTransactionCount = 0
    failedTransactionCount = 0
    buyPointBAH = 0
    shareNumberBAH = 0
    moneyBAH = startCapital
    maximumProfitPercent = 0.0
    maximumLostPercent = 0.0
    forceSell = False
    transactionCharges = 10
    rows,cols = stock_table_df.shape
    k = 0
    #print(rows,cols)
    num_days = 0 
    while(k<rows):
        if(stock_table_df.iloc[k]['Predicted'] == 0):
            buyPoint = stock_table_df.iloc[k]['CLOSE']
            #buyPoint = stock_table_df.iloc[k]['LOW']
            buyPoint = buyPoint*100
            shareNumber = (money-transactionCharges)/buyPoint
            forceSell = False
            #startDate = datetime.datetime.strptime(stock_table_df.iloc[k]['DATE'], "%Y-%m-%d").date()
    
            for j in range(k,rows):
                sellPoint = stock_table_df.iloc[j]['CLOSE']
                #sellPoint = stock_table_df.iloc[j]['HIGH']
                sellPoint = sellPoint*100;
                moneyTemp = (shareNumber*sellPoint)-transactionCharges
                    
                #stop loss %10
                #if(money*0.9>moneyTemp)
                #    money = moneyTemp
                #    forceSell = true

                #if(stock_table_df.iloc[j][0] == 0 or forceSell == True):
                if(stock_table_df.iloc[j]['Predicted'] == 1 or forceSell == True):
                    sellPoint = stock_table_df.iloc[j]['CLOSE']
                    #sellPoint = stock_table_df.iloc[j]['HIGH']
                    #endDate = datetime.datetime.strptime(stock_table_df.iloc[j]['DATE'], "%Y-%m-%d").date()
                    #dt = endDate-startDate
                    #num_days += dt.days
                    sellPoint = sellPoint*100
                    
                    
                    gain = sellPoint-buyPoint
              
                    if(gain>0):
                        successTransactionCount += 1

                    else:
                        failedTransactionCount += 1


                    if(gain >= maximumGain):
                        maximumGain = gain
                        maximumProfitPercent = (maximumGain/buyPoint)*100;		

                    if(gain <= maximumLost):
                        maximumLost = gain
                        maximumLostPercent = (maximumLost/buyPoint)*100		

                    moneyTemp = (shareNumber*sellPoint)-transactionCharges
                    money = moneyTemp

                    if(money > maximumMoney):
                        maximumMoney = money

                    if(money < minimumMoney):
                        minimumMoney = money

                    transactionCount += 1
                    #print("\\\\"+transactionCount+"."+"("+(k+1)+"-"+(j+1)+") => " + round(sellPoint,2) + "-" + round(buyPoint,2)+ "= " + round(gain,2) + " Capital: \\$" + Precision.round(money,2) );
                    #print(str(transactionCount) + "." + "("+str(k+1)+"-"+str(j+1)+") => " + str(round((gain*shareNumber),2)) + " Capital: Rs" + str(round(money,2)))
                    #builder.append(transactionCount+"."+"("+(k+1)+"-"+(j+1)+") => " + round((gain*shareNumber),2) + " Capital: Rs" + round(money,2)+"\n");

                    #System.out.println(Precision.round(money,2) );
                    totalPercentProfit = totalPercentProfit + (gain/buyPoint);

                    totalTransactionLength = totalTransactionLength + (j-k);
                    k = j+1
                    totalGain = totalGain + gain
                    break
        k += 1

    startDate = datetime.datetime.strptime(stock_table_df.iloc[0]['DATE'], "%Y-%m-%d").date()
    endDate = datetime.datetime.strptime(stock_table_df.iloc[rows-1]['DATE'], "%Y-%m-%d").date()
    #print(startDate)
    #print(endDate)
    dt = endDate-startDate
    print('days:',dt.days)
    #print('num_days:',num_days)
    numberOfDays = dt.days
    #numberOfDays = num_days
    numberOfYears = numberOfDays/365
    if transactionCount == 0:
        transactionCount = 1e-5
    AR = round(((math.exp(math.log(money/startCapital)/numberOfYears)-1)*100),2)
    #BaHAR = (round(((math.exp(math.log(moneyBAH/startCapital)/numberOfYears)-1)*100),2)
    AnT = round((transactionCount/numberOfYears),1)
    PoS = round((successTransactionCount/transactionCount)*100,2)
    ApT = round((totalPercentProfit/transactionCount*100),2)
    L = totalTransactionLength/transactionCount
    MpT = round(maximumProfitPercent,2)
    MlT = round(maximumLostPercent,2)
    MaxCV = round(maximumMoney,2)
    MinCV = round(minimumMoney,2)
    IdleR = round((((rows-totalTransactionLength)/rows)*100),2)
    #print(numberOfYears)
    return AR, AnT, PoS, ApT, L, MpT, MlT, MaxCV, MinCV, IdleR
