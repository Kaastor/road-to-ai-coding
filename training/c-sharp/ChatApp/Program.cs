using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

using var cts = new CancellationTokenSource();
Console.CancelKeyPress += (_, e) => {
    e.Cancel = true;
    cts.Cancel();
};

Console.WriteLine("Welcome to ChatApp!");
Console.WriteLine("===================");

if (Console.IsInputRedirected)
{
    Console.WriteLine("Warning: Input is redirected. Running in non-interactive mode.");
    Console.WriteLine("The application may not work as expected with piped input.");
    return;
}

string username = GetUsername(cts.Token);
var messages = new List<string>();

Console.WriteLine($"\nHello {username}! You can start chatting. Type 'exit' to quit.");
Console.WriteLine("Enter your message and press Enter to send it.\n");

int emptyInputCount = 0;
const int maxEmptyInputs = 10;

while (!cts.Token.IsCancellationRequested)
{
    Console.Write($"{username}: ");
    var input = ReadLineWithTimeout(cts.Token);
    
    if (input == null)
    {
        Console.WriteLine("\nOperation cancelled or timed out.");
        break;
    }
    
    if (string.IsNullOrWhiteSpace(input))
    {
        emptyInputCount++;
        if (emptyInputCount >= maxEmptyInputs)
        {
            Console.WriteLine($"\nReceived {maxEmptyInputs} empty inputs. Exiting to prevent infinite loop.");
            break;
        }
        continue;
    }
    
    emptyInputCount = 0;
        
    if (input.Equals("exit", StringComparison.OrdinalIgnoreCase))
        break;
    
    var message = $"{username}: {input}";
    messages.Add(message);
    
    Console.WriteLine($"Message sent: {message}");
}

Console.WriteLine("\nChat session ended. Goodbye!");

static string GetUsername(CancellationToken cancellationToken)
{
    string username;
    int attempts = 0;
    const int maxAttempts = 5;
    
    do
    {
        if (cancellationToken.IsCancellationRequested)
            throw new OperationCanceledException();
            
        attempts++;
        if (attempts > maxAttempts)
        {
            Console.WriteLine($"Too many failed attempts ({maxAttempts}). Exiting.");
            Environment.Exit(1);
        }
        
        Console.Write("Please enter your username: ");
        username = ReadLineWithTimeout(cancellationToken)?.Trim() ?? string.Empty;
        
        if (string.IsNullOrWhiteSpace(username))
        {
            Console.WriteLine("Username cannot be empty. Please try again.");
        }
    } 
    while (string.IsNullOrWhiteSpace(username));
    
    return username;
}

static string? ReadLineWithTimeout(CancellationToken cancellationToken)
{
    try
    {
        if (cancellationToken.IsCancellationRequested)
            return null;
            
        var task = Task.Run(() => Console.ReadLine(), cancellationToken);
        
        if (task.Wait(TimeSpan.FromSeconds(30), cancellationToken))
        {
            return task.Result;
        }
        else
        {
            Console.WriteLine("\nInput timeout after 30 seconds.");
            return null;
        }
    }
    catch (OperationCanceledException)
    {
        return null;
    }
    catch (AggregateException ex) when (ex.InnerException is OperationCanceledException)
    {
        return null;
    }
}
