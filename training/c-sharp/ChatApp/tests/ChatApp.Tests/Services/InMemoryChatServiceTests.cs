using FluentAssertions;
using ChatApp.Models;
using ChatApp.Services;

namespace ChatApp.Tests.Services;

public class InMemoryChatServiceTests
{
    private readonly InMemoryChatService _chatService;

    public InMemoryChatServiceTests()
    {
        _chatService = new InMemoryChatService();
    }

    [Fact]
    public void AddMessage_Should_StoreMessage_When_ValidInput()
    {
        var username = "John";
        var content = "Hello World!";

        _chatService.AddMessage(username, content);
        var messages = _chatService.GetMessages();

        messages.Should().HaveCount(1);
        messages[0].Username.Should().Be(username);
        messages[0].Content.Should().Be(content);
        messages[0].Timestamp.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(1));
    }

    [Fact]
    public void AddMessage_Should_TrimWhitespace_When_InputHasWhitespace()
    {
        var username = "  John  ";
        var content = "  Hello World!  ";

        _chatService.AddMessage(username, content);
        var messages = _chatService.GetMessages();

        messages[0].Username.Should().Be("John");
        messages[0].Content.Should().Be("Hello World!");
    }

    [Theory]
    [InlineData(null, "content")]
    [InlineData("username", null)]
    public void AddMessage_Should_ThrowArgumentNullException_When_InputIsNull(string username, string content)
    {
        var action = () => _chatService.AddMessage(username, content);

        action.Should().Throw<ArgumentNullException>();
    }

    [Theory]
    [InlineData("", "content")]
    [InlineData("   ", "content")]
    [InlineData("username", "")]
    [InlineData("username", "   ")]
    public void AddMessage_Should_ThrowArgumentException_When_InputIsEmptyOrWhitespace(string username, string content)
    {
        var action = () => _chatService.AddMessage(username, content);

        action.Should().Throw<ArgumentException>();
    }

    [Fact]
    public void GetMessages_Should_ReturnEmptyList_When_NoMessagesAdded()
    {
        var messages = _chatService.GetMessages();

        messages.Should().BeEmpty();
    }

    [Fact]
    public void GetMessages_Should_ReturnAllMessagesInOrder_When_MultipleMessagesAdded()
    {
        _chatService.AddMessage("John", "First message");
        _chatService.AddMessage("Jane", "Second message");
        _chatService.AddMessage("John", "Third message");

        var messages = _chatService.GetMessages();

        messages.Should().HaveCount(3);
        messages[0].Content.Should().Be("First message");
        messages[1].Content.Should().Be("Second message");
        messages[2].Content.Should().Be("Third message");
    }

    [Fact]
    public void GetRecentMessages_Should_ReturnSpecifiedCount_When_MoreMessagesExist()
    {
        _chatService.AddMessage("John", "Message 1");
        _chatService.AddMessage("Jane", "Message 2");
        _chatService.AddMessage("John", "Message 3");
        _chatService.AddMessage("Jane", "Message 4");

        var recentMessages = _chatService.GetRecentMessages(2);

        recentMessages.Should().HaveCount(2);
        recentMessages[0].Content.Should().Be("Message 3");
        recentMessages[1].Content.Should().Be("Message 4");
    }

    [Fact]
    public void GetRecentMessages_Should_ReturnAllMessages_When_CountExceedsAvailable()
    {
        _chatService.AddMessage("John", "Only message");

        var recentMessages = _chatService.GetRecentMessages(5);

        recentMessages.Should().HaveCount(1);
        recentMessages[0].Content.Should().Be("Only message");
    }

    [Fact]
    public void GetRecentMessages_Should_ReturnEmptyList_When_NoMessagesExist()
    {
        var recentMessages = _chatService.GetRecentMessages(5);

        recentMessages.Should().BeEmpty();
    }

    [Fact]
    public void GetRecentMessages_Should_ThrowArgumentException_When_CountIsNegative()
    {
        var action = () => _chatService.GetRecentMessages(-1);

        action.Should().Throw<ArgumentException>();
    }
}