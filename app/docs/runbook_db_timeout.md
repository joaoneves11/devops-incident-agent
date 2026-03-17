# Runbook: Database Timeout

## Visão geral
Procedimentos para diagnosticar e resolver timeouts de conexão ou de query no banco de dados.

## O que investigar primeiro
1. **Métricas de pool** – uso do connection pool (perto de 1.0 = esgotado).
2. **Logs com "DatabaseTimeout" ou "connection pool"** – qual serviço e quantos eventos.
3. **Deploy recente** – mudança em queries ou em número de conexões.

## Pré-requisitos
- Acesso a métricas do DB e a logs de slow query
- Conhecimento das configurações de connection pool

## Passos
1. Verificar CPU do DB, conexões e slow queries.
2. Identificar queries longas ou bloqueantes.
3. Escalar conexões ou otimizar queries conforme necessário.
4. Considerar read replicas ou ajuste de connection pooling.

## Casos similares / padrões
- Vários serviços com timeout ao mesmo tempo → problema no DB ou na rede.
- Um serviço só (ex.: payments-api) com pool exhausted → aumento de tráfego ou query nova pesada; ver deploy e mudanças recentes.

## Escalação
Acionar DBA ou on-call se os timeouts continuarem após o tuning.
