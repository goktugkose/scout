## SCOUT: Supporting User Story Completeness via Knowledge Graphs

Requirements engineering practices are important for defining the different aspects of a software project to ensure it meets expectations. 

However, in a collaborative environment, generating requirements can be complex because multiple stakeholders need to represent different aspects of the project and have a common understanding of key concepts. User stories are a popular way of capturing requirements using natural language, but determining the completeness of a set of user stories is a challenging task.

To address this issue, we propose SCOUT that uses a natural language processing pipeline to extract key concepts from user stories and build a knowledge graph by connecting related terms. The knowledge graph and several heuristics are then used to generate suggestions for stakeholders to increase the overall completeness of the user stories.

### How to run?

To run this program, following steps must be followed. <br/>

1. Docker image for web service layer must be created. <br/>
<pre><code>docker build -t scout-ws .</code></pre>

2. Docker image for web interface must be created.
<pre><code>docker build -t scout-wp .</code></pre>


3. Docker image for RDBMS must be created.
<pre><code>docker build -t scout-sqlserver .</code></pre>


4. After creating all required images, system will run on Docker.
<pre><code>docker-compose up -d</code></pre>
