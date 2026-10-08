# .NET routing evals

Each prompt assumes the `dotnet` skill is loaded. Pass = agent opens every `expect` file, none of the `must-not` files, and shows `behavior` when given.

## E01
prompt: Start a new .NET API for a todo app in this empty folder.
expect: choose-conventions.md, project-structure.md
must-not: detect-conventions.md

## E02
prompt: Repo has src/Shop.Api/Shop.Api.csproj and no .claude/conventions/dotnet.md. Rename OrderService to OrderManager.
expect: detect-conventions.md, csharp-style.md
must-not: choose-conventions.md

## E03
prompt: Review this C# class for style issues: `public class orderSvc { public Order getOrder(int ID) => _db.Orders.Find(ID).Result; }`
expect: csharp-style.md
must-not: grpc.md, signalr.md

## E04
prompt: Add a Billing module to our modular monolith solution.
expect: project-structure.md
must-not: grpc.md

## E05
prompt: What status code should POST /orders return when an order with the same id already exists?
expect: rest-api-design.md
must-not: grpc.md, efcore.md

## E06
prompt: Add the Scalar UI and a v2 API version to our Minimal API.
expect: aspnetcore-api.md
must-not: grpc.md

## E07
prompt: Add an rpc GetInvoice to invoices.proto and implement it on the server.
expect: grpc.md
must-not: signalr.md, rest-api-design.md

## E08
prompt: Push order status updates to connected browsers from NotificationsHub.
expect: signalr.md
must-not: grpc.md

## E09
prompt: Add a CreateOrderCommand with its handler, and log around every handler.
expect: mediator-pattern.md
must-not: grpc.md

## E10
prompt: Validate CreateCustomerRequest — email required, age >= 18 — and return errors without throwing exceptions.
expect: validation-and-results.md
must-not: grpc.md

## E11
prompt: Map the Order entity to OrderDto.
expect: mapping.md
must-not: efcore.md

## E12
prompt: Calls to the payment provider via HttpClient time out under load; add retries and a timeout.
expect: resilience.md
must-not: grpc.md

## E13
prompt: Add a migration that adds a ShippedAt column to the Orders table in our DbContext.
expect: efcore.md
must-not: dapper.md, mongodb.md

## E14
prompt: Write a Dapper query that returns the top 10 customers by revenue.
expect: dapper.md
must-not: efcore.md, mongodb.md

## E15
prompt: Cache product lookups in Redis for 5 minutes.
expect: caching.md
must-not: mongodb.md

## E16
prompt: Store audit events in a MongoDB collection.
expect: mongodb.md
must-not: efcore.md, dapper.md

## E17
prompt: Publish an OrderPlaced event and consume it in the Shipping service over RabbitMQ.
expect: messaging.md
must-not: signalr.md

## E18
prompt: Run a cleanup job every night at 02:00.
expect: background-jobs.md
must-not: messaging.md

## E19
prompt: Add OpenTelemetry tracing and a /health endpoint.
expect: observability.md
must-not: grpc.md

## E20
prompt: Add the API and a Postgres container to our Aspire AppHost.
expect: aspire-and-containers.md
must-not: grpc.md

## E21
prompt: Protect DELETE /orders/{id} so only admins holding an Entra ID JWT can call it.
expect: auth.md
must-not: grpc.md

## E22
prompt: Write unit tests for PriceCalculator with a mocked ITaxService.
expect: testing-unit.md
must-not: testing-integration.md

## E23
prompt: Write an integration test that calls POST /orders against a real Postgres database.
expect: testing-integration.md
must-not: testing-unit.md

## E24
prompt: Build a Blazor page that lists orders.
expect: none
must-not: aspnetcore-api.md, project-structure.md
behavior: says Blazor is out of scope for this skill

## E25
prompt: Add a Razor Pages login form.
expect: none
must-not: auth.md, aspnetcore-api.md
behavior: says Razor Pages is out of scope for this skill

## E26
prompt: Explain the difference between git merge and git rebase.
expect: none
must-not: csharp-style.md

## E27
prompt: .claude/conventions/dotnet.md says "architecture: vertical-slice", but the folder I'm editing uses Controllers/Services/Repositories. Add GET /invoices/{id}.
expect: none
must-not: detect-conventions.md, choose-conventions.md
behavior: flags the mismatch and asks which wins before writing code

## E28
prompt: .claude/conventions/dotnet.md lists AutoMapper. Add mapping for Invoice to InvoiceDto.
expect: mapping.md
must-not: detect-conventions.md
behavior: keeps AutoMapper; does not propose migrating to Mapster

## E29
prompt: Repo root has web/ (React) and api/Shop.Api/Shop.Api.csproj, no conventions file. Add GET /products.
expect: detect-conventions.md, rest-api-design.md
must-not: choose-conventions.md
behavior: scopes the convention scan to api/ only

## E30
prompt: .claude/conventions/dotnet.md exists. Add POST /customers that validates input and saves via EF Core.
expect: rest-api-design.md, validation-and-results.md, efcore.md
must-not: dapper.md, mongodb.md
