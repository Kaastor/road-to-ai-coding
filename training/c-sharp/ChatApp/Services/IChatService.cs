using ChatApp.Models;

namespace ChatApp.Services;

public interface IChatService
{
    void AddMessage(string username, string content);
    IReadOnlyList<Message> GetMessages();
    IReadOnlyList<Message> GetRecentMessages(int count);
}