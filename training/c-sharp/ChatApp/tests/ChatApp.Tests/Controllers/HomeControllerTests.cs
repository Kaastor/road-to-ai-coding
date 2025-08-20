using Microsoft.AspNetCore.Mvc.Testing;
using FluentAssertions;
using System.Net;

namespace ChatApp.Tests.Controllers;

public class HomeControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;
    private readonly HttpClient _client;

    public HomeControllerTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
        _client = _factory.CreateClient();
    }

    [Fact]
    public async Task Index_Should_ReturnSuccessAndCorrectContentType()
    {
        // Act
        var response = await _client.GetAsync("/");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        response.Content.Headers.ContentType?.ToString().Should().StartWith("text/html");
    }

    [Fact]
    public async Task Index_Should_ContainUsernamePrompt()
    {
        // Act
        var response = await _client.GetAsync("/");
        var content = await response.Content.ReadAsStringAsync();

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        content.Should().Contain("Welcome to ChatApp!");
        content.Should().Contain("Please enter your username");
        content.Should().Contain("name=\"username\"");
    }

    [Fact]
    public async Task Chat_WithUsername_Should_ReturnSuccess()
    {
        // Act
        var response = await _client.GetAsync("/Home/Chat?username=TestUser");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }

    [Fact]
    public async Task Chat_WithUsername_Should_ContainChatInterface()
    {
        // Act
        var response = await _client.GetAsync("/Home/Chat?username=TestUser");
        var content = await response.Content.ReadAsStringAsync();

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        content.Should().Contain("Chat Room");
        content.Should().Contain("Welcome, <strong>TestUser</strong>");
        content.Should().Contain("name=\"content\"");
        content.Should().Contain("Type your message...");
    }

    [Fact]
    public async Task Chat_WithEmptyUsername_Should_RedirectToIndex()
    {
        // Act
        var response = await _client.GetAsync("/Home/Chat?username=");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Redirect);
        response.Headers.Location?.ToString().Should().Be("/");
    }

    [Fact]
    public async Task Chat_WithoutUsername_Should_RedirectToIndex()
    {
        // Act
        var response = await _client.GetAsync("/Home/Chat");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Redirect);
        response.Headers.Location?.ToString().Should().Be("/");
    }

    [Fact]
    public async Task SendMessage_WithValidData_Should_RedirectToChatWithUsername()
    {
        // Arrange
        var formData = new FormUrlEncodedContent(new[]
        {
            new KeyValuePair<string, string>("username", "TestUser"),
            new KeyValuePair<string, string>("content", "Hello World!")
        });

        // Act
        var response = await _client.PostAsync("/Home/SendMessage", formData);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Redirect);
        response.Headers.Location?.ToString().Should().Be("/Home/Chat?username=TestUser");
    }

    [Fact]
    public async Task SendMessage_WithEmptyContent_Should_StillRedirect()
    {
        // Arrange
        var formData = new FormUrlEncodedContent(new[]
        {
            new KeyValuePair<string, string>("username", "TestUser"),
            new KeyValuePair<string, string>("content", "")
        });

        // Act
        var response = await _client.PostAsync("/Home/SendMessage", formData);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Redirect);
        response.Headers.Location?.ToString().Should().Be("/Home/Chat?username=TestUser");
    }
}