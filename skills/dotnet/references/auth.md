# Authentication and authorization

> Load when: task touches login, JWT, bearer tokens, OIDC, Entra ID, Keycloak, Duende, policies, roles, or ASP.NET Core Identity. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: `AddJwtBearer`, `Microsoft.Identity.Web` (`AddMicrosoftIdentityWebApi`), `AddAuthorization`/`RequireAuthorization`, `AddIdentityApiEndpoints`/`MapIdentityApi`, `Duende.IdentityServer`, an `Authority` setting pointing at Keycloak or Entra.
- Rule: follow what is there. Duende IdentityServer is commercial (see below); never swap the identity provider or token format unasked.

## New repo default
- The API validates tokens; it does not issue them. Use an external OIDC provider (Entra ID, Keycloak, or similar) as the token issuer.
- Entra ID: `Microsoft.Identity.Web`, `AddAuthentication(JwtBearerDefaults.AuthenticationScheme).AddMicrosoftIdentityWebApi(builder.Configuration)`, settings in the `AzureAd` config section.
- Other OIDC providers (Keycloak and so on): `AddJwtBearer` with `Authority` and `Audience` from configuration; keep signature, issuer, audience and lifetime validation on.
- Call `UseAuthentication()` before `UseAuthorization()`; configuring authentication does not by itself restrict any endpoint.
- Secure by default: set a fallback policy requiring an authenticated user, then mark public endpoints with `AllowAnonymous()`. Apply named policies with `RequireAuthorization("PolicyName")`. Endpoints that must stay anonymous, such as health probes, need `.AllowAnonymous()` or the fallback policy returns 401.
- Policies via `AddAuthorizationBuilder().AddPolicy(...)`. Use `RequireClaim`/`RequireRole` for simple rules; a requirement plus handler for real logic.
- `MapIdentityApi<TUser>` (with `AddIdentityApiEndpoints`) only when this app owns its users. Its tokens are not JWTs and it is not a full token server.
- Duende IdentityServer: commercial product. Development, testing and personal projects need no licence; production does. Community Edition is free for for-profits under USD 1M projected annual gross revenue and under USD 3M capital access (non-profits: budget under USD 1M), not for redistribution. Confirm at https://duendesoftware.com/pricing before recommending it.

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(o => builder.Configuration.Bind("Auth:Jwt", o));

builder.Services.AddAuthorizationBuilder()
    .SetFallbackPolicy(new AuthorizationPolicyBuilder()
        .RequireAuthenticatedUser().Build())
    .AddPolicy("orders:write", p => p.RequireClaim("scope", "orders.write"));

var app = builder.Build();
app.UseAuthentication();
app.UseAuthorization();

app.MapGet("/health/live", () => Results.Ok()).AllowAnonymous();
app.MapPost("/orders", CreateOrder).RequireAuthorization("orders:write");
```

## Avoid
- Writing your own token signing or password hashing → easy to get wrong, unaudited → use an OIDC provider or ASP.NET Core Identity.
- Turning off issuer, audience or lifetime validation to "make it work" → accepts forged tokens → fix the `Authority`/`Audience` config.
- Signing keys or client secrets in `appsettings.json` → leak via source control → user secrets, environment, or a vault.
- Using `MapIdentityApi` as the identity provider for several apps or third-party clients → not a token server → use an OIDC provider.
- Assuming `AddAuthentication` protects endpoints → it only authenticates → add a fallback policy or `RequireAuthorization`.
- Recommending Duende without stating its production licence → surprise cost → state it, offer a free provider.

## Sources
- https://learn.microsoft.com/aspnet/core/security/authentication/ (fetched 2026-10-04)
- https://learn.microsoft.com/aspnet/core/security/authorization/policies (fetched 2026-10-04)
- https://learn.microsoft.com/entra/identity-platform/ (fetched 2026-10-04)
- https://learn.microsoft.com/entra/identity-platform/tutorial-web-api-dotnet-core-build-app (AddMicrosoftIdentityWebApi; fetched 2026-10-04)
- https://learn.microsoft.com/aspnet/core/security/authentication/identity-api-authorization (MapIdentityApi; fetched 2026-10-04)
- https://duendesoftware.com/products/identityserver and https://duendesoftware.com/pricing and https://duendesoftware.com/products/communityedition (licence; fetched 2026-10-04)
