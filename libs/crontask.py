class Task():
    def __init__(self, row):
        self.tid=row[0]
        self.name=row[1]
        self.minute=row[2]
        self.hour=row[3]
        self.dom=row[4]
        self.mon=row[5]
        self.dow=row[6]
        self.command=row[7]

    def getTid(self):
        return self.tid

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def getMinute(self):
        return self.minute

    def setMinute(self, minute):
        self.minute = minute

    def getHour(self):
        return self.hour

    def setHour(self, hour):
        self.hour = hour

    def getDom(self):
        return self.dom

    def setDom(self, dom):
        self.dom = dom

    def getMon(self):
        return self.mon

    def setMon(self, mon):
        self.mon = mon

    def getDow(self):
        return self.dow

    def setDow(self, dow):
        self.dow = dow
    
    def getCommand(self):
        return self.command

    def setCommand(self, command):
        self.command = command

    def __str__(self):
        return f'Task({self.tid},{self.name},{self.minute},{self.hour},{self.dom},{self.mon},{self.dow},{self.command})'
