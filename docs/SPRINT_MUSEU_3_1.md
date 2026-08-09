# Sprint Museu Histórico 3.1

## Entregas

- Favoritos persistentes com limite de 200 fatos por usuário.
- Coleções pessoais organizadas dentro do “Meu Museu”.
- Missão diária: explorar, salvar e responder um quiz; recompensa única de 25 XP.
- Compartilhamento nativo com `savePreparedInlineMessage` e `WebApp.shareMessage`.
- Painel administrativo restrito a proprietário/sudo.
- Aprovação e recusa de sugestões na Mini App.
- Cancelamento e reagendamento seguro de itens da fila editorial.
- Indicadores de usuários, atividade, favoritos, fila e sugestões.

## Segurança

- Favoritos e compartilhamentos só aceitam IDs presentes na base histórica curada.
- Todas as ações privadas validam `Telegram.WebApp.initData` no servidor.
- Operações administrativas exigem `sudo=true` no MongoDB ou correspondência com `OWNER_ID`.
- Recompensas diárias usam atualização atômica e não podem ser recebidas duas vezes no mesmo dia.

## Configuração adicional da Vercel

Além de `BOT_TOKEN` e `MONGO_CON`, configure `OWNER_ID` com o ID numérico do proprietário. Depois faça um novo deployment.
