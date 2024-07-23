# Unievent

# Abstract
Unievent è una piattaforma che consente di pubblicare contenuti. I contenuti possono essere topics o eventi, i contenuti posso avere un immagine descrittiva oppure un video e permettono di connettere persone con gli stessi interessi, attraverso le interazioni e i like. La piattaforma ha tre tipo di utenti: Creator, Organizzatore e Artista. Gli Artisti possono creare sia eventi che topics, i creator possono creare soltanto topics, mentre gli organizzatori solo eventi. Per gli eventi è possibile acquistare un biglietto, ed inoltre è possibile lasciare una recensione.

# Servizi Azure utilizzati
- Azure Cosmos DB (con Mongo DB) per conservare i dati dei contenuti e degli utenti.
- Azure Blob per memorizzare le immagini del profilo degli utenti, e le immagini e i video dei contenuti.
- Azure Function per la logica di backend: interazione col DB, invio immagine, comunicazione fra i servizi.
- Azure Web Pub Sub per le notifiche e la chat tra gli utenti.
- Azure App Service - Utilizzato per il deploy del frontend dell'applicazione.

# Architettura 
L'architettura utilizzerà il modello a tre livelli (Three-Tier Architecture). Questo modello suddivide l'applicazione in tre livelli distinti, ciascuno con responsabilità specifiche:

- Livello di Presentazione (Presentation Tier): gestito da Azure App Service, si occupa dell'interfaccia utente e della presentazione dei dati all'utente.
- Livello di Logica di Business (Business Logic Tier): gestito da Azure Functions, il quale comunicherà con tutti gli altri servizi elencati precedentemente.
- Livello dei Dati (Data Tier): gestito da Azure Blob Storage, il quale si occuperà della gestione dei dati persistenti (immagini) e da Azure Cosmos DB (con Mongo DB) per conservare i dati dei contenuti e degli utenti.
