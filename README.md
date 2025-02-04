# rocketjunior
A REST-based application for management of organizational hierarchy of hardware.

Author: Dylan Frost

Interviewing for Senior Ground Software Engineer II


# Starting
### Setup
Execute the file `setup.sh` to configure local environment:

```make init```

> Note: This step is not required if you already have docker and docker compose set up.

### Running
Run `make build` to build and start the local environment.

### Using
1. Access the frontend application on [your local machine](http://localhost:3000)
2. Access the Swagger UI on [your local machine](http://localhost:8000/api/v1/swagger-ui/)
3. Authenticate to the Swagger UI using the credentials provided with this submission.
4. Try out the default endpoints with the provided graphical HTTP client.

To show all API endpoints in Swagger including the model extension endpoints, set  `HIDE_API_EXTENSIONS=false` in `./be/.envrc`.

Run backend API tests with ```make test-be```

Run frontend app tests with ```make test-fe ```

### Troubleshooting
* Make sure that Docker is installed properly on the local machine
* Check for other running containers that might be using the same ports
* If you are having trouble with Makefile commands, check the Makefile to see what commands it is executing and try running them manually
* For help with this application, please reach out to Dylan Frost at dougfrost314@gmail.com

# Introduction
The interview process for Senior Ground Software Engineer at Rocket Lab asks candidates to complete a coding project to prove their proficiency. I was asked to choose either a backend or frontend problem to solve, this project focuses on the backend side of the two challenges offered.

The tasks laid out for this challenge:
- Design a new React application that
  - Allows users to search for a node by its path using a text input
  - Sends search queries to an API after each keypress and debounce in-flight requests
  - Displays a node tree with properties and time since created
  - Displays property values in green when they are in excess of 10
  - Implements a reusable browser-native confirmation dialog
  - Implements a "Delete" button using the confirmation component to delete a node
    - Delete function is not to be connected to an API
  - Implements a helper method to display created times as "time since created"
  - Has unit tests to assert that the color of node properties is rendered correctly
- Design a database to support deeply-nested self-referential node relationships and arbitrary assignment of key/value pairs to nodes
  - The path of a node can be inferred from its hierarchy
  - There are no name requirements on descendant nodes
  - There is no limit to descendant node depth
  - Nodes can have any number of descendant nodes or properties
- Seed the database with basic test data
- Expose HTTP endpoints to:
  - Create a node with a specified ancestor
  - Add a property to a specific node
  - Return the subtree of nodes with their properties for a provided node path

# Rationale
## Database Design
The problem of database design involved evaluating both potential database platforms and implementation strategies. I took several different approaches and technologies into consideration, and ultimately selected an implementation of a "hierarchical path" column designed to balance the cost and efficiency of read and write operations.

The "path" column stores a delimited string representing identifiers of all ancestor entities for each record. This approach represents a significant advantage for hierarchical queries, like retrieving all ancestors or descendants. This is possible because we can use pattern matching against the path to find related records (i.e. find all components of stage 1 by getting paths that start with /Rocket/Stage1/). See the `fetch_descendants` and `build_tree` methods in `be/entity/managers.py` for this implementation.

### Alternatives Considered
#### Nested Sets
Nested set databases provide efficient reads by using left and right boundary values to graph relationships. In short, a parent's left boundary will be less than all of its descendants' left boundaries, and its right boundary will be greater than all of its descendants' right boundaries. Queries are simple and efficient as they are simply performing lookups on two indexed integer columns.

This approach does, however, introduce significant complexity to write operations. Changes to a single element can cascade to many other elements. This process is both expensive and complex. This approach also does not integrate as nicely with ORMs due to the need for additional code to manage boundary values.

[Read more about nested sets.](https://en.wikipedia.org/wiki/Nested_set_model)

#### Graph Database
I strongly considered using a graph database like Neo4j to support this project. Graph databases are extremely effective at handling deep and complex relationships. They can also provide a powerful analytics tool that can help with things like identifying the scope and impact of defects in manufacturing and assembly.

I ultimately chose not to use a graph database for this project because I have limited experience with the technology, and because I did not have a clear vision of how I would integrate it with a REST API. Given more time or access to a SME, this would be an excellent option to explore further.

[Read more about graph databases like Neo4j](https://www.geeksforgeeks.org/neo4j-introduction/)

## API Framework
As a longtime user of Python, I have experience with most of the popular API frameworks. The two that I considered most strongly were Django and FastAPI. While FastAPI is a fantastic framework that enables rapid development and solid performance, I have not used it for several months. I do work with Django daily and have a lot of previous work that I can reference. My familiarity with the framework and its ecosystem and my knowledge of how to support it in a containerized environment led me to choose Django.

## ORM
I chose to use the Django ORM for this project because models can be quickly spun up with a lot of built-in functionality, and they can be easily integrated with Django Rest Framework's Serializers and ViewSets. I did consider using a custom database interface layer for this project. Had I chosen a different design for the database, I would have opted to design a database interface layer to avoid the potentially tricky challenge of adapting unconventional database designs to an ORM.

## Docker & Docker Compose
Selecting Docker and Docker Compose to support this project was an easy choice. Containerization offers many advantages that make developing and deploying code much easier. The biggest factor in this selection were the fact that this project is intended to run on an evaluator's local machine. Using containers to support the application ensures that it will be using the exact same runtime that it did during development. The other important advantage that I had in mind when making this selection is that containerization is the first step to deploying an application with Kubernetes. This idea is discussed more in the **Production-Readiness** section.

Docker also enables a lot of other handy tricks. For example, I have added a "migrations" container. This container starts with the rest of the application, but its job is to wait for the database to become available, then run any unapplied Django migrations, then permanently shut down. This takes the job of making sure the database is up-to-date mostly out of the hands of the developer and it is a nice parallel to CI/CD jobs that would be performing the same task during a deployment. There is also the "json-server" container that hosts the mock API for the frontend application. I could have had this service run on the "fe" container, but I thought it would be nice to move that responsibility away from the container that is responsible for hosting the application. It also provides a slightly more realistic development environment in that the mocked API requests still have to move from one machine to another through a network, which would not be the case with the mock API hosted on the same server as the application without a little more effort.

## Frontend Framework - React
Most of my experience using frontend frameworks has been with Vue. I chose to use React for this project because of the two framework choices available, I did have a little bit of experience and the framework seemed to have more in common with Vue. While the frameworks do feel substantially different to use, many of the same design prinicples apply, such as state management and responsiveness of components. I think that React was a good choice for this project, and that I would be able to quickly get comfortable with using the framework day-to-day.

# Key Challenges
## Balancing Efficiency of Read and Write Database Operations
Without being able to learn more about this project's business requirements, I wanted to choose an approach that would balance efficiency of read and write operations to produce a solution that will be suitable for a wide variety of use cases. The hierarchical path approach that I selected can enable extremely fast reads of these complex relationships, but this performance is not accessible to projects that only make use of ORMs. In order to really take advantage of the performance potential of this design, I created a raw SQL query to efficiently fetch a flat dataset of all nodes in a tree, and a tree builder method to restructure this data into a tree using Python dictionaries.

With the raw sql approach, the API took roughly 300 milliseconds to produce a tree from over 40,000 records. To see this performance in action, take a look at the load test in `be/entity/test/test_stress.py`

## Managing Node Paths
Management of node paths for the use case outlined in this project is fairly straightforward. The API is only meant to create entities or add attributes to entities. Under this design, paths are generated by appending a node's name onto the end of its parent path value.

<details>
  <summary>Further Discussion</summary>
I wanted to add update and delete capabilities to this API as well. You may have noticed that there is a hidden API in this project that exposes the standard REST endpoints for the Entity and Attribute models. This API has an implementation for updating nodes that allows them to be moved anywhere else in the tree, or even to their own tree with no parent node.
</details>

## Decimal Precision of Property Values
JSON does not support trailing-zero precision of decimal values. In the likely scenario that this application's clients would be other software applications, string values would be used to transmit decimal properties, which would then be converted back into decimal values by the endpoint's consumer. This is a known limitation of JSON and is a fairly common workaround. I added the optional `precision` query parameter to my API endpoints to allow clients to select whether they want to receive truncated decimal values or string values with preserved precision.

## Using React
This is my first real project using React. I have practiced with it a few times in the past, but have never created a fully-fledged applicaiton with it. I have a lot of experience using Vue2, and I did expect the framework to enforce a little bit more structure in the application. Vue codebases feel very organized, and each component typically has its content laid out inside of an object that makes it very easy to separate out different parts of a given component into logical sections. This change was not very difficult to adjust to, and I found that by the end of this project, I felt somewhat fluent with the React basics.

# Caveats
## Expensive Writes
Updating entities can cause somewhat expensive write operations. Create operations are cheap, but updates can require changes to many records if the node being updated has many descendants. While this expense cannot be eliminated entirely, it can be greatly reduced by using a path, tree ID, or combination of the two.
- Tree ID: a reference to the root node of a tree
  - Easy and inexpensive to maintain for a given node
  - Can be used to quickly filter records down to an individual tree
- Path: a slash-delimited string listing all nodes from root to current node
  - Allows fast updates of child nodes when moving a parent node by performing an in-place substring replacement operation to update the ancestor portion of a node's path


## Decimal Precision in JSON Payloads
In JSON, decimal values are represented as floating-point numbers, and as a result do not natively support formatting of decimals to retain decimal precision in transit. This limitation can be worked around by passing decimal values as strings to retain their original precision. Because the project prompt specified decimals with trailing-zero precision in the payload, I was unable to entirely meet this specific requirement. The trade-off I chose was to add an optional `precision` query parameter to the subtree API endpoint to allow clients to specify whether they want to receive JSON floating-point decimal values without precision preservation, or string-formatted decimal values with the original precision preserved in the response payload.

I believe that this is an acceptable trade-off. JSON is an industry standard and commonly used by enterprises across the globe and drawbacks like this must be worked around on a regular basis. Because this is a REST API, consumers of the subtree endpoint are likely to be other software applications like frontends or app integrations that can accommodate the need to parse string-formatted decimals back into true decimal types.

The floating-point limitation could have been mitigated by choosing a technology like GraphQL to retrieve information from the database. This approach would have worked well if I had chosen to use a graph database.

## Local Development Environment
I spent a lot of time thinking about how to balance ease of setup of this application for evaluators with the need to create a secure and robust application. During most of this project's development, it utilized `direnv` and `python-decouple` to inject sensitive information from a git-ignored `.env` file. I prefer this approach over using operating system environment variables because it has better support for error handling than pulling the values from the operating system. Ultimately, I chose to remove `direnv` and `python-decouple` to eliminate unnecessary complexity for others who want to run this application. The values being passed in the `.env` file are not sensitive because they only apply to the local environment.

## Frontend Compromises
I made a few compromises on the front end in terms how how I would like the application to behave. I implemented the "Delete" button as described in the instruction, and did not connect it to any actual delete function as described in the instructions. I wanted to indicate somehow that the next step for the application to perform after receiving confirmation was to remove the node from the page. Under normal circumstances, I would have the page re-request the current data and re-render the content with the udpated data. I chose instead to collapse the node that was deleted.
Determining the appropriate behavior of the search input and how it updates the page content was also a little bit tricky. I didn't want to remove content from the screen while the API request executes in the background, so I chose to leave the last-rendered content on the page while further searches execute. In my opinion, this hurts the usability of the page, because it interferes with the page's feedback to the user. To make the page's behavior more clear to the user, I added a spinner overlaid on the right end of the input to indicate that a request is running in the background.

## 404 Errors in the Console
Unfortunately, many of the API requests placed by the frontend will return a 404 error. This happens because a request will attempt to fire after each keystroke in the input element. Most of these requests will contain a partial path that will not match, because the user is in the middle of typing and the path is not yet complete. These 404 responses are shown in the console as errors by the browser. The application itself handles the 404 responses just fine. Unfortunately, I was not able to find the time to suppress these errors in the console.

# Production-Readiness
## Production Infrastructure
This project is designed to be deployed to the cloud using Kubernetes. Using containerized components allows images to be built and cached in a container registry like AWS ECR. These images can be used to deploy the application to a series of Kubernetes pods on a service like AWS EKS. Additional effort to implement such a deployment would involve setting up additional infrastructure like an AWS RDS database, DNS records, Kubernetes nodes, etc. Much of this can be handled with an infrastructure-as-code tool such as Terraform. I would choose Helm to generate Kubernetes manifests because it allows deployments to be broken down by their individual components, and it supports versioning of deployments.

### Summary of Infrastructure
* Containerized application
* Container images contain application in a highly specific environment
* Containers are hosted on a Kubernetes node using services like AWS EKS
* Some services that reside in containers locally can be run directly from cloud services, such as:
  * Database: AWS RDS
    * Backups
    * Replication & Failover
  * Redis Cache: AWS Elasticache
  * Sensitive Data Management: AWS Secrets Manager or GitHub Secrets
* Some new services are required that are not needed localy, such as:
  * Ingress
  * Load Balancing
  * DNS
* Use Helm to break deployment into manageable and logical pieces and to construct Kubernetes manifests
* Use CI/CD tool like GitHub Actions to orchestrate testing, validation, and deployment of application
  * Workflows and automations can be controlled manually or be event-driven
  * Likely setup: automatic test and validation runs when a pull request is created, automatic deploys to test environments after pull requests merged, automatic deploys to production when a release tag is created
* Infrastructure-as-code tools such as Terraform can be used to manage the build, composition, and state of cloud resources

## Secret Handling
Secret handling during deployments is a major concern regarding application security. This project uses an extremely thin environment file (which wasn't strictly necessary because its contents are not particulary sensitive) as a kind of stand-in for more robust secret handling. In a production deployment, sensitive data can be injected into the deployment using a service like GitHub Secrets or AWS Secrets Manager. This approach provides a centralized control for all secrets ensures that sensitive data remains encrypted in transit to the application.

## CI/CD & Automated Testing
CI/CD is critical to the success of an enterprise-level application, speeding up the development lifecycle with automation covering builds, tests, and deployments. GitHub Actions is a perfect candidate to handle CI/CD for applications being hosted in GitHub repositories. Some advantages of using GitHub Workflows:
* Workflows and actions can be easily packaged and shared between projects
* Automations can be highly modular to enable a high rate of reuse for components
* Automations are defined and stored as code in a project's repository, ensuring their behavior only changes when it needs to
* Processes can be started by a wide variety of events in a GitHub repository, or even from outside of the repository

## Authentication
This project retains the default Basic Auth configuration that all new Django projects start with. I would like to have removed this functionality from the project, knowing that it will only ever run as a demo on personal devices with no sensitive information being stored within it. I made the decision to leave authentication in place because part of this project is to explore how an application like this would be deployed to a production environment. If this application needed to be prepared for release, I would get to work on replacing Basic Auth with JWTs for a more secure application that is prepared to support more advanced authentication schemes like OAuth.
I chose not to build any authentication into the frontend of the application. I felt that since I did not have as much React experience as I have Python experience, it was not worth adding this feature. My time was better spent focusing on the core requirements of the project and making sure that I could produce a clean and polished application.

# Assumptions & Deviations
* Assumption: Given the information I have, this project could be used in write-heavy applicaitons like hardware design or in read-heavy applications like analytics. For this reason, I have chosen to balance read and write efficiency.
* Assumption: I am to design this application with production-readiness in mind. This was a driver behind the choice to use tools like Docker/Docker-Compose, direnv, and leaving authentication enabled on a demo app that will not actually run in a production environment.
* Deviation: I have included the `path` field in the response payload. This makes it very easy to understand where a node is located in a tree. If there is a hard business requirement to exclude this field from the response payload, it can be easily disabled in the `ModelSerializer` class.
* Deviation: Attributes in response payload are not represented as Decimal values while retaining originally-provided decimal precision. This has been discussed in previous sections, but in short, JSON does not support decimal formatting but does offer simple workarounds that are not disruptive to most REST API use cases.
