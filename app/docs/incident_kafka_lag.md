# Incident: Kafka Consumer Lag

## Visão geral
Procedimentos para diagnosticar e resolver lag de consumer no Kafka.

## O que investigar primeiro
1. **Métricas de lag** – valor atual e tendência (subindo ou estável).
2. **Logs do consumer** – erros ou restarts; throughput (messages/sec).
3. **Deploy recente** no serviço consumidor – mudança de código ou de partições.

## Pré-requisitos
- Acesso a métricas do Kafka e ao status do consumer group
- Conhecimento da quantidade de partições do topic e do throughput

## Passos
1. Identificar consumer groups e partições com lag.
2. Verificar saúde do consumer e throughput (messages/sec).
3. Escalar consumers ou partições se subdimensionado.
4. Investigar processamento lento ou gargalos downstream.

## Casos similares / padrões
- Lag alto após deploy → rollback ou revert do consumer; ver se processamento ficou mais lento.
- Lag crescente com erros nos logs → falha no processamento (ex.: timeout em DB); alinhar com runbook de Database Timeout.

## Escalação
Acionar time de dados/plataforma se o lag não drenar após o scaling.
