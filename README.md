
<p align="center">

![Image Alt text](/readme_images/inicial.png)

</p>

<p align="center">
<img src="https://img.shields.io/badge/docker-24.0.7-blue"/>
<img src="https://img.shields.io/badge/docker--compose-2.23.3-9cf"/>
<img src="https://img.shields.io/badge/python-3.11-yellowgreen"/>
<img src="https://img.shields.io/badge/framework-fastAPI-brightgreen"/>
<img src="https://img.shields.io/badge/mongo-7.0.5-green"/>
<img src="https://img.shields.io/badge/postgres-16.1-lightgrey"/>
<img src="https://img.shields.io/badge/redis-6.2.5--alpine-red"/>
<img src="https://img.shields.io/badge/rabbitmq-3.10.2--alpine-orange"/>
</p>

---

<h1 align="center">
   🚀 Processamento assíncrono
</h1>
<p align="center">
    <em>
    Projeto desenvolvido com o intuito de exercitar o processamento assíncrono em conjunto com um sistema de tentativas, tratamento de falhas, triggers e logs 
    </em>
</p>

---

Sumário
=================

   * [O projeto](#o-projeto)
   * [Bancos de Dados DB1 e DB2](#bancos-de-dados-db1-e-db2)
   * [APIs Sistema 1 e Sistema 2](#apis-sistema-1-e-sistema-2)
   * [Orquestrador de processos](#orquestrador-de-processos)
   * [Filas](#filas)
   * [Consumidor](#consumidor)
   * [Logs de execução](#logs-de-execução)
        * [Estrutura](#estrutura)
        * [Visualização](#visualização)
   * [Banco de dados para endput](#banco-de-dados-para-endput)
        * [Detalhe](#detalhe)
        * [Resultado esperado](#resultado-esperado)
   * [Makefile](#makefile)

   

---

## O projeto

Este projeto é uma prova de conceito para explorar e exercitar diversas funcionalidades pautadas em diversas tecnologias e suas integrações. O projeto é composto por:

1. Um banco de dados Redis. Focado em orquestrar os processos que serão rodados nas APIs.
2. API 1 utilizando fastAPI. Essa API terá um endpoint para preencher o DB conectado à ela e alguns endpoints envolvendo o processo de gerar mensagens e enviar mensagens para nossa fila primária.
3. Banco de dados PostgreSQL. Responsável por guardar informações basica de um pedido, possivelmente um pedido de uma loja ou marketplace.
4. API 2 utilizando fastAPI. Esta API é uma cópia da anterior. Contudo, foi inserida para demonstrar processamento paralelo e inserção dupla numa mesma exchange/fila.
5. Banco de dados PostgreSQL. Semelhante ao ponto 3, contudo relacionado à API 2.
6. Fila primária utilizando RabbitMQ. Está configurada com um plugin de delay de mensagens de 10 segundos (configurável) para voltar para a fila.
7. Fila DLQ  utilizando RabbitMQ. É trigada pela falha de processamento da filha primária após processar sem sucesso durante 5x.
8. Consumidor em Python. É acionado a partir da fila primária. Tem a função de logar tudo que roda nele no mongo e exercer a função de guardar as informações recebidas da mensagem no PostgreSQL.
9. Um banco de dados mongoDB. Responsável por servir de log para tudo que é consumido no consumer. Nesse banco há um TTL configurável.
10. Banco de dados PostgreSQL. Relacionado à guardar todas as informações processadas pelo consumidor, ou seja, que passaram pela fila e foram processadas com sucesso.

---

## Bancos de Dados DB1 e DB2

Esses bancos de dados possuem uma estrutura simples. Apenas um schema e uma tabela. Contudo, estes foram escolhidos para simbolizar que poderíamos inserir um banco com estrutura mais complexa e ainda assim funcionaria na solução adotada.

Tanto os bancos DB1 e DB2 possuem estruturas iguais. Segue algumas particularidades:

1. O campo ID é sequencial, mas esse dado não será importante na nossa prova de conceito. Optei por não realizar nenhuma associação dele ao meu resultado gerado no banco DB Endput.
2. O campo created_at também não será reaproveitado no nosso output.
3. Os campos que serão reaproveitados no nosso endput serão "product", "price" e "security_check".
4. O campo "security_check" não está realizando nenhuma verificação de segurança. Este, foi criado como um booleano para servir de base para a lógica que será apresentada nas filas e para podermos visualizar na tabela de endput o resultado de maneira mais clara.
5. Há um endpoint em cada uma das APIs para auxiliar no preenchimento dos dados desses 2 bancos.

![Image Alt text](/readme_images/postgresql.png)

_DB1_: http://localhost:5432

_DB2_: http://localhost:5433

---

## APIs Sistema 1 e Sistema 2

Estas APIs são iguais e foram criadas com o auxílio do framework fastAPI. Estas possuem apenas 4 endpoints que podem ser acessadas através de suas respectivas documentações que podem ser encontradas em "/docs" e "/redoc".

Para testarmos os "retrys" da fila, criamos uma lógica dentro das APIs das quais o cosumidor futuramente se beneficiará. Segue a logica de envio de mensagens para a fila:

1. Em cada linha do banco lida, o sistema verifica o campo "security_check".
2. CASO esse campo esteja pré preenchido como TRUE, a API anexa à mensagem um numero máximo de processamento que varia de 1 a 5x. ( Dado que o numero máximo aceito pelo consumidor em termos de processamento de uma mesma mensagem é 5 )
3. CASO esse campo esteja pré preenchido como FALSE, a API anexa à mensagem um número máximo de processamento de 6x. Sabendo que esse numero extrapola o máximo de tentativas, saberemos que essa mensagem irá falhar.
4. Na prática, as mensagem com "security_check" = FALSE sempre irão falhar no processamento do consumidor e nunca chegarão ao nosso banco de dados destino.
5. Outra maneira de encontrar as linhas "security_check" = FALSE é verificar ao termino do processamento se elas se encontram na DLQ.

![Image Alt text](/readme_images/fastapi.png)

_API1_: http://localhost:8001/docs

_API2_: http://localhost:8002/docs

---

## Orquestrador de processos

Com o intuito de criar uma funcionalidade para permitir que nossas APIs processem somente linhas do banco que não foram previamente processadas, utilizamos o Redis para orquestrar esses processos.

A estrutura do Redis é bem enxuta, teremos pouca informação contida nela. A função principal dessa estrutura é registrar qual a última linha do banco que foi processada. Assim, na próxima vez que precisarmso processar algo, partiremos da ultima linha processada + 1.

![Image Alt text](/readme_images/orquestrador.png)

_Redis_: http://localhost:6379

---

## Filas

As filas desse projeto estão utilizando RabbitMQ e um plugin de delay de entrada à fila. As mensagens processadas pelas APIs, caem na fila principal (também chamada de "primary"). 

Através do "localhost:15672" será possível analisar as filas, exchanges e demais componentes do RabbitMQ que foram cadastrados automaticamente pelas configurações contidas no código.

Funcionamento de seu processamento:
1. Caso essas mensagens sejam processadas com sucesso, elas saem da fila primária.
2. Caso sejam processadas sem sucesso, MAS, ainda não estourou o limite de até 5 processamentos, a mensagem volta à fila. Como há um plugin de delay de volta à fila, a mensagem pode demorar um tempo customizável para voltar.
3. Caso a mensagem ultrapasse o limite máximo de processamentos sem sucesso, a mensagem irá cair na "fila morta", também chamada de DLQ. 

![Image Alt text](/readme_images/rabbitMQ.png)

_RabbitMQ_: http://localhost:15672

---

## Consumidor

O consumidor será um agente bastante demandado da estrutura apresentada. Este ficará ouvindo a fila, registrando seu processamento em um banco de dados e registrando informações em outro banco de dados quando conseguir realizar um processamento com sucesso.

![Image Alt text](/readme_images/consumidor.png)

---

## Logs de execução

Os logs de execução serão escritos no mongoDB. Esse banco foi configurado para aceitar uma quantidade de segundos equivalente à um TTL. Ou seja, seus dados irão se autodestruir após um tempo configurável de sua escrita no banco.

### Estrutura

A estrutura do log engloba algumas coisas:

1. Identificador para a mensagem.
    1. O _id é gerado automaticamente para cada mensagem que entra na fila. Caso uma mensagem seja processada erroneamente, ela voltará para a fila, porém com um _id diferente. Para solucionar isso, temos o campo "message_id".
    2. O campo "message_id" é bastante útil pra gente, pois, ao pesquisar sobre uma determinada mensagem, conseguimos obter o historico de processamento dela, seus status e suas informações.
2. Area de processamento. Nessa area guardamos dados referentes à:
    1. Em qual tentativa estamos?
    2. Status atual do processamento.
    3. Quantidade de tentativas necessárias para que a mensagem seja lida com sucesso. (Caso esse campo possua o valor "6", sabemos que esta nunca será lida com sucesso)
3. Informações de origem da mensagem.
4. Dados referentes ao processamento da mensagem em si.
5. Campo de data do processamento. Esse campo será utilizado como referência para o mongodb saber quando auto excluir algumas de suas linhas baseado no tempo de criação.

![Image Alt text](/readme_images/mongodb.png)

### Visualização

Há uma ferramenta visual para enxergarmos o conteúdo desse banco de dados. A ferramenta "Mongo Express" está disponível para verificação.

Ao selecionar o database "local" e collection "messagem", podemos encontrar nossos logs. Nessa página podemos também pegar um "message_id" e pesquisar na area de busca para descobrir o histórico de processamento de uma mensagem.

![Image Alt text](/readme_images/mongodb2.png)

_Mongo Express_: http://localhost:8081

---

## Banco de dados para endput

Após o processamento bem sucedido de todas as mensagens, a ideia do projeto é gravar numa tabela dentro de um outro banco postgresql todas as "orders" que possuam o "security_check" = TRUE.

### Detalhe

Nos detalhes desse banco, podemos perceber sua simplicidade, seguindo o padrão de um schema e uma tabela. A escolha desse banco se fez para seguir um padrão com os bancos de entrada e mostrar que em casos reais e complexos, seria uma possível opção.

![Image Alt text](/readme_images/endput.png)

### Resultado esperado

Dentro do resultado buscado nesse campo, veremos apenas campos com o security_check abaixo. Teremos também a quantidade de linhas esperada para os inputs de securities positivos dentros das APIs.

![Image Alt text](/readme_images/endput2.png)

_DB Endput_: http://localhost:5434

---

## Makefile

Com o intuito de facilitar e agilizar a subida, descida e limpeza dos containers, um Makefile foi criado. Os comandos "make start_with_logs" e "make stop" são provavelmente os comandos mais importantes para auxiliar na hora de iniciar e parar esse projeto.

---