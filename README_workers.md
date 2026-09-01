# Seletor SaaS - Motor de Renderização Distribuída (Workers)

> **Arquitetura Distribuída com Django e FastAPI para Orquestração de Edição de Vídeo Assistida por IA em Ambiente SaaS.**

---

## 📌 Sobre o Projeto
Este repositório abriga a implementação dos **nós de processamento descentralizados (Workers)** do ecossistema Seletor SaaS.

Com o crescimento da demanda por cortes virais e edição automatizada de vídeos utilizando Inteligência Artificial, o processamento centralizado na nuvem torna-se financeiramente proibitivo. Para resolver isso, desenvolvemos uma **solução híbrida em Python**:
- Um **Nó Central (Django)** hospeda a aplicação web, gerenciando usuários, faturamento e integrações de pagamento.
- Uma **Fazenda de Nós Escravos (FastAPI)**, alocada em infraestrutura on-premise, herda todo o processamento pesado de IA (análise de engajamento via LLMs, reedição e renderização de vídeo).

## 🚀 Arquitetura do Sistema
O sistema foi projetado sob o padrão mestre-escravo (*Master-Worker*), garantindo tolerância a falhas e isolamento de responsabilidades.

### ⚖️ Load Balancer Integrado
O nó central atua como um *Estoque Central*. Para evitar gargalos, ele delega o fardo pesado através de um **Load Balancer** customizado. O balanceador rastreia a fazenda de workers disponíveis e avalia métricas (como disponibilidade de memória) para rotear e distribuir os vídeos de forma inteligente.

### ⚙️ Workers Stateless
Os nós escravos (este repositório) operam de forma totalmente **sem estado (stateless)**:
1. Recebem um *ping* com a URL de um projeto.
2. Baixam o vídeo longo original (input).
3. Executam a pipeline de IA para mapear os momentos de pico de interesse no conteúdo.
4. Realizam os cortes cirúrgicos das cenas de alta retenção.
5. Devolvem os cortes finais virais via requisição `HTTP POST` para o painel Django.
6. Executam uma limpeza forçada em seu disco local, mitigando o acúmulo de lixo digital nos computadores.

## 🔒 Segurança e Ofuscação de Código
Como estes *workers* são desenhados para rodar em infraestruturas locais com possibilidade de acesso físico por terceiros (reaproveitamento de ociosidade de hardware), tanto as chaves de API das LLMs quanto a propriedade intelectual dos algoritmos de detecção de retenção correm riscos de extração.

> ⚠️ **Por que existem arquivos `.pyd` aqui?**
Para blindar a aplicação, o código-fonte principal em Python foi convertido para C e compilado em extensões nativas binárias (`.pyd`) através do Cython. Este repositório expõe publicamente apenas os invólucros de execução (as "capas" do FastAPI) e os algoritmos pré-compilados, impedindo a engenharia reversa do fluxo de inteligência.

## 🛠️ Resiliência de Rede
A distribuição em redes locais apresenta desafios rigorosos de **Firewalls e VLANs**. 
Durante a implementação, restrições de tráfego cross-subnet nas portas da API foram transpostas. O sistema foi empacotado com um ambiente Python embutido e portátil, iniciando como um serviço fantasma (*background task*) silencioso no Windows. Isso garante que a fazenda inteira se religue sozinha após quedas de energia, sem qualquer intervenção humana.

### ⏱️ Resultados Práticos de Escalabilidade
Em testes de estresse para processamento de 10 vídeos longos:
- **Servidor Único:** $\approx$ 120 minutos (Com alto custo em Nuvem)
- **Fazenda Distribuída (5 Nós):** $\approx$ 25 minutos (Reaproveitando hardware local)

---

### 👨‍💻 Autoria e Links Úteis
- **Desenvolvido por:** Jacson Arruda Ribeiro
- 🔗 [Página Oficial do SaaS (Vendas / Web)](https://shorts-factory-ai.github.io/)
- 🔗 [Conectar no LinkedIn](https://www.linkedin.com/in/jacsonrn)
