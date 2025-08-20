using Microsoft.AspNetCore.Mvc;
using ChatApp.Services;
using ChatApp.Models;

namespace ChatApp.Controllers;

public class HomeController : Controller
{
    private readonly IChatService _chatService;

    public HomeController(IChatService chatService)
    {
        _chatService = chatService;
    }

    public IActionResult Index()
    {
        return View();
    }

    public IActionResult Chat(string username)
    {
        if (string.IsNullOrWhiteSpace(username))
        {
            return RedirectToAction("Index");
        }

        ViewBag.Username = username;
        var messages = _chatService.GetMessages();
        return View(messages);
    }

    [HttpPost]
    public IActionResult SendMessage(string username, string content)
    {
        if (!string.IsNullOrWhiteSpace(username) && !string.IsNullOrWhiteSpace(content))
        {
            _chatService.AddMessage(username, content.Trim());
        }

        return RedirectToAction("Chat", new { username });
    }

    public IActionResult Error()
    {
        return View();
    }
}