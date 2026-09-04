# Mergington High School Activities (.NET 10)

ASP.NET Core minimal API port of the FastAPI application. It serves the original browser assets from `wwwroot/static` and retains the existing activity API routes.

## Run locally

```powershell
dotnet run --project src-dotnet
```

Open the URL printed by ASP.NET Core. The application redirects `/` to `/static/index.html`.

## Test

```powershell
dotnet test src-dotnet/tests/tests.csproj
```

Activity data is stored in memory and resets whenever the application restarts.