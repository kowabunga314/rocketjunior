# rocketjunior
System for organizational hierarchy of hardware.


# Starting
### Setup
Execute the file `setup.sh` to configure local environment:

```make init```

### Running
Run `make build` to build and start the local environment.

### Using
Access the Swagger UI on [your local machine](http://localhost:8000/api/v1/swagger-ui/)

Authenticate to the Swagger UI using the credentials provided with this submission.

To show all API endpoints in Swagger including the model extension endpoints, delete the value of the `HIDE_API_EXTENSIONS` setting in `./be/.envrc`.


# Rationale
## Database Design
My task was to design a database that can support deeply-nested self-referential relationships. I took several different approaches and technologies into consideration, and ultimately selected an implementation of a "path" column designed to balance the cost and efficiency of read and write operations.

The "path" column stores a delimited string representing identifiers of all ancestor entities for each record. This approach represents a significant advantage for hierarchical queries, like retrieving all ancestors or descendants. This is possible because we can use pattern matching against the path to find related records (i.e. find all components of stage 1 by getting paths that start with /Rocket/Stage1/)

### Alternatives Considered
#### Nested Sets
Nested set databases provide efficient reads by using left and right boundary values to graph relationships. In short, a parent's left boundary will be less than all of its descendants' left boundaries, and its right boundary will be greater than all of its descendants' right boundaries. Queries are simple and efficient as they are simply performing lookups on two indexed integer columns.

This approach does, however, introduce significant complexity to write operations. Changes to a single element can cascade to many other elements. This process is both expensive and complex. This approach also does not integrate as nicely with ORMs due to the need for additional code to manage boundary values.

#### Graph Database
I strongly considered using a graph database like Neo4j to support this project. Graph databases are extremely effective at handling deep and complex relationships. They can also provide a powerful analytics tool that can help with things like identifying the scope and impact of defects in manufacturing and assembly.

I ultimately chose not to use a graph database for this project because I have limited experience with the technology, and because I did not have a clear vision of how I would integrate it with a REST API. Given more time or access to a SME, this would be an excellent option to explore further.

## API Framework
As a longtime user of Python, I have experience with most of the popular API frameworks. The two that I considered most strongly were Django and FastAPI. While FastAPI is a fantastic framework that enables rapid development and solid performance, I have not used it for several months. I do work with Django daily and have a lot of previous work that I can reference. My familiarity with the framework and its ecosystem and my knowledge of how to support it in a containerized environment led me to choose Django.

## ORM
I chose to use the Django ORM for this project because models can be quickly spun up with a lot of built-in functionality, and they can be easily integrated with Django Rest Framework's Serializers and ViewSets. I did consider using a custom database interface layer for this project. Had I chosen a different design for the database, I would have opted to design a database interface layer to avoid the potentially tricky challenge of adapting unconventional database designs to an ORM.

## Docker & Docker Compose
Selecting Docker and Docker Compose to support this project was an easy choice. Containerization offers many advantages that make developing and deploying code much easier. The biggest factor in this selection were the fact that this project is intended to run on an evaluator's local machine. Using containers to support the application ensures that it will be using the exact same runtime that it did during development. The other important advantage that I had in mind when making this selection is that containerization is the first step to deploying an application with Kubernetes. This idea is discussed more in the **Production-Readiness** section.

# Key Challenges
## Balancing Efficiency of Read and Write Operations

## Managing Node Paths

## Decimal Precision of Property Values
JSON does not support trailing-zero precision of decimal values. In the likely scenario that this application's clients would be other software applications, string values would be used to transmit decimal properties, which would then be converted back into decimal values by the endpoint's consumer. This is a known limitation of JSON and is a fairly common workaround. I added the optional `precision` query parameter to my API endpoints to allow clients to select whether they want to receive truncated decimal values or string values with preserved precision.


# Caveats
## Expensive Writes
Updating entities can cause somewhat expensive write operations.


# Production-Readiness
## Production Infrastructure
This project is designed to be deployed to the cloud using Kubernetes. Using containerized components allows images to be built and cached in a container registry like AWS ECR. These images can be used to deploy the application to a series of Kubernetes pods on a service like AWS EKS. Additional effort to implement such a deployment would involve setting up additional infrastructure like an AWS RDS database, DNS records, Kubernetes nodes, etc. Much of this can be handled with an infrastructure-as-code tool such as Terraform. I would choose Helm to generate Kubernetes manifests because it allows deployments to be broken down by their individual components, and it supports versioning of deployments.

## Deployments

## Secret Handling
Secret handling during deployments is a major concern regarding application security. This project uses an extremely thin environment file (which wasn't strictly necessary because its contents are not particulary sensitive) as a kind of stand-in for more robust secret handling. In a production deployment, sensitive data can be injected into the deployment using a service like GitHub Secrets or AWS Secrets Manager. This approach provides a centralized control for all secrets ensures that sensitive data remains encrypted in transit to the application.

## CI/CD & Automated Testing
CI/CD is critical to the success of an enterprise-level application...

# Additional Thoughts
