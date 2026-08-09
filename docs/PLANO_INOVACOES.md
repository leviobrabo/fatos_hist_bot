# Plano de inovações — Fatos Históricos

Este documento transforma as dez ideias de produto em entregas compatíveis com a arquitetura atual do bot.

## Decisões de arquitetura

- MongoDB é a fonte de verdade para perfil, preferências, progresso, sugestões, fila editorial e assinaturas.
- O processo do bot executa polling e tarefas agendadas; nenhuma fila importante depende apenas da memória.
- A Mini App usa frontend estático em `public/` e Python Function em `api/`, pronta para Vercel.
- A API valida `Telegram.WebApp.initData` antes de retornar qualquer dado privado.
- Conteúdo histórico assistido usa a base curada do projeto e sempre informa a origem; não inventa respostas.

## Mapa dos dez itens

### 1. Passaporte Histórico

Campos de XP, nível, sequência, última atividade, medalhas e temas descobertos no documento do usuário. Exibição no bot e na Mini App.

### 2. Máquina do Tempo

Comandos `/data`, `/ano`, `/personagem` e `/surpreenda`, usando um índice dos JSONs locais e resultados pagináveis.

### 3. Personalização

Preferências por tema, frequência e horário. O usuário pode alterar pelo comando `/preferencias` ou pela Mini App.

### 4. Quiz competitivo

XP por resposta, sequência diária, ranking semanal/geral, níveis e medalhas. Duelo em tempo real fica como evolução posterior por exigir estado concorrente de partidas.

### 5. Calendário editorial inteligente

Fila persistente, reserva de horários, limite diário, intervalo mínimo, registro de todos os posts observados no canal e reprocessamento seguro após reinício.

### 6. Comunidade

`/sugerir texto | fonte`, fila de moderação e botões de aprovar/recusar para sudo. Sugestões aprovadas entram no calendário editorial.

### 7. Mini App Museu Histórico

Início, passaporte, busca, linha do tempo, preferências e ranking. Interface responsiva e integrada ao tema do Telegram.

### 8. Historiador assistido

`/historiador termo` realiza busca curada e apresenta fatos relacionados e fontes. A camada fica preparada para um provedor de IA futuro, sem exigir uma chave externa nesta entrega.

### 9. Cards compartilháveis

Páginas de fatos com URL estável, metadados sociais e ação de compartilhar pela Mini App. Geração de imagem raster dedicada pode ser adicionada depois sem bloquear o MVP.

### 10. Monetização

Clube Histórico via assinatura mensal em Telegram Stars, status premium no perfil e estrutura para conteýo exclusivo. A publicidade continua limitada pelo calendário editorial.

## Fases e tarefas

- [x] Fase 1 — persistência editorial e modelos MongoDB
- [x] Fase 2 — busca histórica e preferências
- [x] Fase 3 — passaporte, ranking e medalhas
- [x] Fase 4 — sugestões e moderação
- [x] Fase 5 — Clube Histórico e Stars
- [x] Fase 6 — Mini App e API Vercel
- [x] Fase 7 — start/help/comandos/anúncio
- [x] Fase 8 — testes, segurança e roteiro de deploy

## Limites conscientes do MVP

- Duelo síncrono e geração de cards raster são expansões; o MVP entrega ranking e cards compartilháveis por URL.
- Respostas generativas exigem a escolha posterior de um provedor de IA. A primeira versão usa busca curada para preservar credibilidade.
- Deploy real depende das credenciais da conta Vercel e do BotFather; o repositório entrega configuração e instruções prontas.
