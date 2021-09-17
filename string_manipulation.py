def stringGetValue(test,num):
    return float(test.replace('{','').replace('}','').replace('\n','').split(',')[num].split(':')[-1])
    # return test.replace('{','').replace('}','').replace('\n','').split(',')[num].split(' ')[-1].split(':')[-1]
    
    #         self.tempFormatDict={0:'Celsius',1:'Fahrenheit',2:'Kelvin'}

def changeTemp(num,tempDictionary,tempCounter):
    if tempDictionary[tempCounter] == 'Celsius':
        return num
    elif tempDictionary[tempCounter] == 'Fahrenheit':
        num = (num * 1.8) + 32  
        return num
    elif tempDictionary[tempCounter] == 'Kelvin':
        num=num + 273.15
        return num