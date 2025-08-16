- Generate Umberella solution
```
cd root/training/c-sharp
dotnet new sln -n Training
dotnet sln Training.sln add TodoApi/TodoApi.csproj tests/TodoApi.Tests/TodoApi.Tests.csproj
```

- Generate hello world with tests
```
cd root/training/c-sharp
dotnet new console -n HelloConsole
dotnet new xunit -n HelloConsole.Tests -o tests/HelloConsole.Tests
dotnet add tests/HelloConsole.Tests/HelloConsole.Tests.csproj reference HelloConsole/HelloConsole.csproj
```

- Run project
`dotnet run --project HelloConsole`

- Run tests
`dotnet test`
`dotnet test tests/HelloConsole.Tests/HelloConsole.Tests.csproj`
