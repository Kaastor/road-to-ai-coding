namespace ChatApp.Models;

public record Message(string Username, string Content, DateTime Timestamp)
{
    public override string ToString() => $"{Username}: {Content}";
}