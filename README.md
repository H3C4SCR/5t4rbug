# 5T4RBUG

MVP local-first de gestão pessoal de tarefas, feito para estudo com Python, Flask, Jinja e JavaScript.

## O que mudou

O 5T4RBUG não possui mais cadastro, login, senha, sessão de usuário ou banco de dados. O servidor entrega apenas a aplicação web. Cada navegador guarda sua própria lista no `localStorage`, sem enviar tarefas ou identidade para o servidor.

Isso evita misturar as tarefas dos seus amigos, mas também significa que a lista não sincroniza entre dispositivos e pode ser perdida se os dados do navegador forem apagados.

## Rodar localmente

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run.py
```

Abra <http://127.0.0.1:5000> e clique em **Abrir minhas tarefas**.

## Funcionalidades

- Criar, editar, excluir e concluir tarefas.
- Prioridade alta, média ou baixa.
- Status pendente, em andamento ou concluída.
- Prazo opcional.
- Lembrete opcional com data e hora.
- Filtros por status.
- Dados separados por navegador/dispositivo.
- Escape seguro de títulos e descrições usando APIs DOM, sem inserir texto do usuário como HTML.
- HTTPS e cabeçalhos básicos de segurança no deploy.

## Lembretes

Clique em **Ativar lembretes** e permita notificações no navegador. Depois crie uma tarefa, escolha data e hora e marque **Notificar neste horário**.

Os lembretes são uma funcionalidade best-effort: o navegador precisa suportar a Web Notifications API, a página precisa estar em HTTPS ou localhost e normalmente deve permanecer aberta. Se o navegador ou a aba estiverem fechados, o JavaScript não consegue garantir uma notificação agendada. Notificações em background confiáveis exigiriam service worker/push e uma arquitetura adicional.

## Publicar gratuitamente

O arquivo `render.yaml` configura somente um Web Service Free. Não é mais necessário Neon, PostgreSQL, SQLite, Persistent Disk ou variável `DATABASE_URL`.

1. Envie a branch `main` para o GitHub.
2. No Render, escolha **New → Blueprint**.
3. Selecione o repositório `H3C4SCR/5t4rbug`.
4. Confirme o `render.yaml` e o plano Free.
5. Abra o endereço `*.onrender.com`.

O Render Free pode suspender o serviço após inatividade; o primeiro carregamento pode demorar. Como as tarefas ficam no navegador, não há banco remoto para perder, mas a lista de cada navegador não é um backup.

Consulte a [documentação do Render Free](https://render.com/docs/free) e [Web Services](https://render.com/docs/web-services). Esta versão é um beta educacional e não é certificação de conformidade LGPD.

## Privacidade e limites

O servidor não recebe tarefas, e-mail, senha ou identificador pessoal pelo fluxo da aplicação. O `localStorage` é específico da origem e pode ser lido por JavaScript servido pela mesma aplicação; não armazene segredos nele. O HTTPS protege o transporte, mas ainda devemos manter o repositório privado e não inserir dados sensíveis nas tarefas durante os testes.

Antes de uso profissional, adicione exportação/backup local, política de privacidade, revisão de segurança, controle de acesso ao repositório e uma estratégia de sincronização criptografada caso esse requisito apareça.

## Como estudar

1. `run.py` inicia a aplicação.
2. `app/__init__.py` cria o servidor e os cabeçalhos.
3. `app/main/routes.py` expõe somente as páginas públicas.
4. `app/templates/dashboard.html` contém a estrutura visual.
5. `app/static/js/dashboard.js` implementa armazenamento, CRUD, filtros e notificações.
6. `app/static/css/style.css` mantém o layout responsivo.
