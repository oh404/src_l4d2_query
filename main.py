import connector

a = connector.Querier("5.75.164.134", 27015)
f = a.info()
print(f)