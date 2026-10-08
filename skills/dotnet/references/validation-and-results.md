# Validation and Results

> Load when: adding request validation, error handling without exceptions, or mapping failures to HTTP responses. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: `FluentValidation` / `FluentValidation.DependencyInjectionExtensions` packages, `AbstractValidator<T>` classes; `ErrorOr` (`ErrorOr<T>`) or `FluentResults` packages; a hand-written `Result<T>` type.
- Rule: follow what is there. If `FluentValidation.AspNetCore` auto-validation is wired up, leave it; do not add new code that depends on it.

## New repo default
- FluentValidation `AbstractValidator<T>` per request; register with `services.AddValidatorsFromAssemblyContaining<Program>()` (package `FluentValidation.DependencyInjectionExtensions`).
- Invoke validators manually (in an endpoint, or in a mediator decorator). The FluentValidation docs no longer recommend the ASP.NET auto-validation pipeline for new projects: no async support, MVC and Razor Pages only, hard to debug.
- Hand-rolled `Result<T>` by default. Use ErrorOr or FluentResults only when the repo already has it.
- Expected failures (validation, not found, conflict) are `Result` values; exceptions are for the unexpected.
- At the HTTP edge, translate the Result: validation errors to `TypedResults.ValidationProblem(...)`, others to `TypedResults.Problem(...)` or `NotFound`.

```csharp
public enum ErrorKind { Validation, NotFound, Conflict }

public sealed record Error(ErrorKind Kind, string Code, string Message);

public sealed class Result<T>
{
    public T? Value { get; }
    public IReadOnlyList<Error> Errors { get; }
    public bool IsSuccess => Errors.Count == 0;
    private Result(T? value, IReadOnlyList<Error> errors) => (Value, Errors) = (value, errors);
    public static Result<T> Ok(T value) => new(value, []);
    public static Result<T> Fail(params Error[] errors) => new(default, errors);
}

static IResult ToHttp<T>(Result<T> r) => r switch
{
    { IsSuccess: true } => TypedResults.Ok(r.Value),
    _ when r.Errors[0].Kind == ErrorKind.Validation => TypedResults.ValidationProblem(
        r.Errors.GroupBy(e => e.Code).ToDictionary(g => g.Key, g => g.Select(e => e.Message).ToArray())),
    _ when r.Errors[0].Kind == ErrorKind.NotFound => TypedResults.NotFound(),
    _ => TypedResults.Problem(r.Errors[0].Message, statusCode: StatusCodes.Status409Conflict),
};
```

- Rule: pipeline validation (a mediator decorator) throws FluentValidation's `ValidationException`; a global `IExceptionHandler` (.NET 8+) maps it to a 400. Business errors found inside a handler (not found, conflict) stay `Result` values.

```csharp
public sealed class ValidationExceptionHandler(IProblemDetailsService problems) : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(HttpContext ctx, Exception ex, CancellationToken ct)
    {
        if (ex is not ValidationException ve) return false;
        ctx.Response.StatusCode = StatusCodes.Status400BadRequest;
        return await problems.TryWriteAsync(new ProblemDetailsContext
        {
            HttpContext = ctx,
            ProblemDetails = new HttpValidationProblemDetails(ve.Errors
                .GroupBy(e => e.PropertyName)
                .ToDictionary(g => g.Key, g => g.Select(e => e.ErrorMessage).ToArray())),
        });
    }
}
// Program.cs: AddProblemDetails(); AddExceptionHandler<ValidationExceptionHandler>(); app.UseExceptionHandler();
```

## Avoid
- `FluentValidation.AspNetCore` auto-validation in new code → deprecated approach, no async → call `ValidateAsync` yourself.
- Throwing exceptions for not-found or conflict in a handler → slow, loses typing → return a Result. (Decorator validation may throw; the handler above turns it into a 400.)
- Letting `ValidationException` reach the default `UseExceptionHandler()` → 500 for bad input → register the handler above.
- Mixing two Result libraries in one repo → two error vocabularies → pick the one already present.
- Returning raw `Result` JSON to clients → leaks internals, inconsistent shape → ProblemDetails via `TypedResults`.

## Sources
- https://docs.fluentvalidation.net/en/latest/aspnet.html (fetched 2026-10-04; auto-validation "no longer recommended", `AddValidatorsFromAssemblyContaining`)
- https://github.com/amantinband/error-or (fetched 2026-10-04; `ErrorOr<T>`, `IsError`, `Errors`, `Match`)
- https://learn.microsoft.com/aspnet/core/fundamentals/error-handling (fetched 2026-10-04; `IExceptionHandler.TryHandleAsync` returns `ValueTask<bool>`, `AddExceptionHandler<T>`, `UseExceptionHandler` needs `AddProblemDetails()` or a path, handlers run first, `true` means the handler wrote the full response; `HttpValidationProblemDetails` and `TryWriteAsync` are not shown in that text, so confirm against the API reference)
- https://learn.microsoft.com/aspnet/core/fundamentals/minimal-apis/responses (fetched 2026-10-04; page covers `TypedResults.Problem` and ValidationProblem; the `ValidationProblem` dictionary overload used above is not shown in the fetched text, so confirm it against the API reference)
