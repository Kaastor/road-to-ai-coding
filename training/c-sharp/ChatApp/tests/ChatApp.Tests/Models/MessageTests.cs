using FluentAssertions;
using ChatApp.Models;

namespace ChatApp.Tests.Models;

public class MessageTests
{
    [Fact]
    public void Message_Should_CreateWithCorrectProperties_When_Instantiated()
    {
        var username = "John";
        var content = "Hello World!";
        var timestamp = DateTime.UtcNow;

        var message = new Message(username, content, timestamp);

        message.Username.Should().Be(username);
        message.Content.Should().Be(content);
        message.Timestamp.Should().Be(timestamp);
    }

    [Fact]
    public void ToString_Should_ReturnFormattedMessage_When_Called()
    {
        var username = "John";
        var content = "Hello World!";
        var timestamp = DateTime.UtcNow;
        var message = new Message(username, content, timestamp);

        var result = message.ToString();

        result.Should().Be("John: Hello World!");
    }

    [Fact]
    public void Messages_Should_BeEqual_When_AllPropertiesAreEqual()
    {
        var timestamp = DateTime.UtcNow;
        var message1 = new Message("John", "Hello", timestamp);
        var message2 = new Message("John", "Hello", timestamp);

        message1.Should().Be(message2);
    }

    [Fact]
    public void Messages_Should_NotBeEqual_When_AnyPropertyDiffers()
    {
        var timestamp = DateTime.UtcNow;
        var message1 = new Message("John", "Hello", timestamp);
        var message2 = new Message("Jane", "Hello", timestamp);

        message1.Should().NotBe(message2);
    }
}