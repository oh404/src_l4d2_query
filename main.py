import querier

host = querier.Querier("74.91.124.246", 27015)

# request playerlist and playtime:
print("PLAYERLIST")
players = host.players()

print("==========")
print("GAMEINFO:")
# request gameinfo:
gameinfo = host.info()

print("==========")
print("CVARS:")
# request cvars:
cvars = host.convars()
