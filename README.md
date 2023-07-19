# Alunos

BIANCA PEREIRA DE CARVALHO - 202004706

LUIS GUILHERME BARBOSA CUSTODIO - 201905500

# O projeto

### Multithreading

O projeto utiliza multithreading no servidor e no cliente de uma aplicação de chat para melhorar sua escalabilidade.

No servidor cada conexão de cliente é executada em uma thread; e no cliente são executadas duas threads, uma para envio e outra para recebimento de mensagens

### Chat em "grupo"

O chat permite troca de mensagens entre usuários (um para um) e também de um usuário para todos os usuários (um para todos).

#### Problema de escalabilidade

A forma como o chat em "grupo" foi implementado é funcional em pequena escala, ou seja, quando poucos clientes se conectam ao servidor, sua eficencia cai de acordo com que o número de clientes aumenta.

Para melhorar a escalabilidade da aplicaçao o chat em "grupo" poderia ser feito usando uma abordagem Publish-Subscribe ou um sistema de fila de mensagens, como o RabbitMQ.
Assim a aplicaçao usaria sockets para a conexao entre o servidor e os clientes, e usaria o RabbitMQ em "fanout" para distribuir as mensagens para todos os clientes conectados ao servidor.
