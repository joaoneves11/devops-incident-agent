# Runbook: API 500 Errors

## Visão geral
Procedimentos para diagnosticar e resolver erros HTTP 500 na API.

## O que investigar primeiro
1. **Logs do serviço** – stack traces e mensagens de erro (priorize o serviço mencionado na pergunta).
2. **Deploy recente** – se houve deploy logo antes do início dos erros, considerar rollback.
3. **Dependências** – banco, cache e APIs externas (timeouts, 5xx em cascata).

## Pré-requisitos
- Acesso a logs e métricas da API
- Histórico de deployments para mudanças recentes

## Passos
1. Verificar logs da API em busca de stack traces e mensagens de erro.
2. Verificar deployments recentes; considerar rollback se houver correlação.
3. Verificar dependências (DB, cache, serviços externos).
4. Aplicar correção ou rollback e monitorar.

## Casos similares / padrões
- Erros 500 após deploy → rollback e comparar diff.
- 500 com "timeout" ou "connection" → ver runbook de Database Timeout e checar gateway externo.
- 500 em um único serviço com pico de erros → bug ou dependência fora; isolar pelo nome do serviço nos logs.

## Escalação
Acionar on-call se os erros persistirem após o rollback.
