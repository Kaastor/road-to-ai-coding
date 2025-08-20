using ChatApp.Models;

namespace ChatApp.Services;

public class InMemoryChatService : IChatService
{
    private readonly List<Message> _messages = new();

    public void AddMessage(string username, string content)
    {
        ArgumentNullException.ThrowIfNull(username, nameof(username));
        ArgumentNullException.ThrowIfNull(content, nameof(content));

        if (string.IsNullOrWhiteSpace(username))
            throw new ArgumentException("Username cannot be empty", nameof(username));

        if (string.IsNullOrWhiteSpace(content))
            throw new ArgumentException("Content cannot be empty", nameof(content));

        var message = new Message(username.Trim(), content.Trim(), DateTime.UtcNow);
        _messages.Add(message);
    }

    public IReadOnlyList<Message> GetMessages()
    {
        return _messages.AsReadOnly();
    }

    public IReadOnlyList<Message> GetRecentMessages(int count)
    {
        if (count < 0)
            throw new ArgumentException("Count cannot be negative", nameof(count));

        return _messages
            .TakeLast(count)
            .ToList()
            .AsReadOnly();
    }
}