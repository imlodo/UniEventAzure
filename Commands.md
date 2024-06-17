# Required: Azure CLI (https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows?tabs=azure-cli)

# Aprire la shell ed effettuare il login
az login 

# Creare i servizi da portale azure, tramite shell non setta i parametri gratuiti
az group create --name unieventresourcegroup --location eastus

az cosmosdb create --name unieventcosmosdb --resource-group unieventresourcegroup --kind MongoDB --locations regionName=eastus failoverPriority=0 isZoneRedundant=False --default-consistency-level Eventual --enable-free-tier true --throughput 400

az cosmosdb mongodb database create --account-name unieventcosmosdb --resource-group unieventresourcegroup --name unieventmongodb

az cosmosdb mongodb collection create --account-name unieventcosmosdb --resource-group unieventresourcegroup --database-name unieventmongodb --name User --throughput 400


# Per eliminare tutte le risorse create
az group delete --name unieventresourcegroup --yes --no-wait