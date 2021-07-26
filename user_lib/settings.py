def saveToDataFile(data):
    with open('data.txt', 'w') as f: # "a"-for Append, 'w'=for Overwrite
        f.write(data)

def readFromDataFile():
    with open('data.txt', 'r') as f:
        data = f.read()
    return data

# insted of:
# f = open('data.txt', 'w')
# f.write('some test data')
# f.close()
# # read it
# f1 = open('data.txt')
# f1.read()
# f1.close()
# =============================================================================