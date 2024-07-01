Per far funzionare il websocket seguire i seguenti passaggi

Deployare questa azure function

az login --tenant 5f0b3e27-d6d7-48e5-982d-c508ad4eec62 (accedere con account alodato815@gmail.com)
Creare un nuovo azure function project in azure (piano gratuito)

https://portal.azure.com/#view/Microsoft_Azure_Billing/FreeServicesBlade
<br>

func azure functionapp publish UniEventAzureFunctApp --resource-group unievent --python --publish-local-settings --no-bundler --force --functions ChatWebSocket

per deployarle tutte invece
func azure functionapp publish UniEventAzureFunctApp --resource-group unievent --python --publish-local-settings --no-bundler --force

[FONDAMENTALE] 
<br>
<br>
Go to Azure portal -> Find your Function App resource -> App keys -> System keys -> webpubsub_extension. Copy out the value as <APP_KEY>.
![img.png](img.png)

Set Event Handler in Azure Web PubSub service. Go to Azure portal -> Find your Web PubSub resource -> Settings. Add a new hub settings mapping to the one function in use. Replace the <FUNCTIONAPP_NAME> and <APP_KEY> to yours.

Hub Name: simplechat
URL Template: https://<FUNCTIONAPP_NAME>.azurewebsites.net/runtime/webhooks/webpubsub?code=<APP_KEY>
User Event Pattern: *
System Events: -(No need to configure in this sample)
![img_1.png](img_1.png)

esempio:
<br>
https://unieventazurefunctapp.azurewebsites.net/runtime/webhooks/webpubsub?code=cetOTlUNNWGbXVAByc3GQ5Vl1g3Ah59zFm578XbCLygSAzFufufGSQ==
