# Unit testing

> Load when: writing or changing unit tests, or a task names xUnit, NUnit, MSTest, assertions or mocks. Pinned: .NET 10 / C# 14.

## Existing repo
- How to recognise it: `xunit.v3*` / `xunit` / `NUnit` / `MSTest.TestFramework` package references in test `*.csproj` or `Directory.Packages.props`; assertion packages `Shouldly`, `FluentAssertions`, `AwesomeAssertions`; mock packages `NSubstitute`, `Moq`.
- Rule: follow the framework, assertion library and mock library already in use, and the file layout of existing tests. Do not swap libraries or migrate xUnit v2 to v3 unasked.
- Licence: FluentAssertions v8 and later needs a paid licence for commercial use (free for open-source and non-commercial); v7 and earlier stay open source. Keep it in a repo that already has it. Never upgrade 7 to 8 without telling the user. AwesomeAssertions is the free community fork (Apache 2.0) with a near-identical API.
- Moq: licence: check https://github.com/devlooped/moq before recommending an upgrade.

## New repo default
- Framework: xUnit v3 (`xunit.v3` packages, in-process runner, `TestContext.Current`, assembly fixtures). NUnit or MSTest only when the user asks.
- Assertions: Shouldly (`result.ShouldBe(42)`; failure text names the expression). AwesomeAssertions is the alternative when the team wants the FluentAssertions style. Not FluentAssertions v8.
- Mocks: NSubstitute (`Substitute.For<T>()`, `.Returns(...)`, `.Received()`). Substitute interfaces; classes only with virtual members.
- Pattern: Arrange, Act, Assert with the three parts visible; one Act per test; use `[Theory]` instead of loops or `if` in a test.
- Naming: `Method_Condition_Expected`, for example `Add_SingleNumber_ReturnsSameNumber`.
- Test behaviour, not implementation: assert on outputs and observable effects through public members; do not test private methods; assert interactions only when the interaction is the behaviour.
- Time and other statics: put a seam in front (`TimeProvider`, an interface) and substitute it.
- Keep unit tests free of infrastructure (no database, network, file system); those belong to the integration tests.
- Data access: never mock `DbContext` or `DbSet` to test queries. Test queries against a real database (integration test); unit-test the logic around it.

```csharp
public class PriceCalculatorTests
{
    [Fact]
    public void GetDiscountedPrice_OnTuesday_ReturnsHalfPrice()
    {
        // Arrange
        var clock = Substitute.For<TimeProvider>();
        clock.GetUtcNow().Returns(new DateTimeOffset(2026, 10, 6, 0, 0, 0, TimeSpan.Zero)); // a Tuesday
        var sut = new PriceCalculator(clock);

        // Act
        var actual = sut.GetDiscountedPrice(100);

        // Assert
        actual.ShouldBe(50);
    }
}
```

## Avoid
- Mocking `DbContext` / `DbSet` for queries → LINQ runs in memory, not as SQL, so results differ from production → test against a real database, or hide data access behind a repository and stub that.
- Asserting on private state or call order of internals → tests break on refactor → assert public behaviour.
- Loops, `if` or string building inside a test → the test can have its own bugs → `[Theory]` with `[InlineData]`.
- Shared mutable state via setup methods or static fields → hidden coupling between tests → build the sut in a helper method per test.
- Adding FluentAssertions v8 to a new repo → commercial licence → Shouldly or AwesomeAssertions.
- Magic values and over-specified inputs → unclear intent → named constants, minimal input.

## Sources
- https://xunit.net/docs/getting-started/v3/whats-new (fetched 2026-10-04)
- https://xunit.net/docs/shared-context (fetched 2026-10-04)
- https://learn.microsoft.com/dotnet/core/testing/unit-testing-best-practices (fetched 2026-10-04)
- https://nsubstitute.github.io/help/getting-started/ (fetched 2026-10-04)
- https://github.com/shouldly/shouldly (fetched 2026-10-04)
- https://github.com/AwesomeAssertions/AwesomeAssertions (fetched 2026-10-04)
- https://fluentassertions.com/ (fetched 2026-10-04)
- https://learn.microsoft.com/ef/core/testing/choosing-a-testing-strategy (fetched 2026-10-04)
