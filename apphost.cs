#:sdk Aspire.AppHost.Sdk@13.1.0
#:package Aspire.Hosting.Python@13.1.0
#:package Aspire.Hosting.JavaScript@13.1.0
#:package Aspire.Hosting.Azure.AppContainers@13.1.0

var builder = DistributedApplication.CreateBuilder(args);

// Configure Azure Container App Environment for deployment
var appContainer = builder.AddAzureContainerAppEnvironment("starter-env");

// Python FastAPI Backend
var api = builder.AddUvicornApp("api", "./api", "app.main:app")
    .WithUv()
    .WithHttpHealthCheck("/health")
    .PublishAsAzureContainerApp((infra, app) =>
    {
        var container = app.Template.Containers[0].Value!;
        container.Resources.Cpu = 1;
        container.Resources.Memory = "2Gi";
    });

// React/Vite Frontend
var web = builder.AddViteApp("web", "./web")
    .WithReference(api, "API_ENDPOINT")
    .WaitFor(api)
    .WithExternalHttpEndpoints()
    .PublishAsAzureContainerApp((infra, app) =>
    {
        var container = app.Template.Containers[0].Value!;
        container.Resources.Cpu = 1;
        container.Resources.Memory = "2Gi";
    });

// Force HTTPS for the API URL at deploy time
if (builder.ExecutionContext.IsPublishMode)
{
    api.WithEndpoint("http", e => e.UriScheme = "https");
}

builder.Build().Run();
