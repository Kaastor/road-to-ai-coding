"""Demonstration of Command pattern implementation for text editor with undo/redo."""

import logging
from typing import Any

from .commands import DeleteTextCommand, FormatTextCommand, InsertTextCommand, MacroCommand
from .invoker import TextEditorInvoker
from .text_editor import TextEditor, TextFormat


def setup_logging() -> None:
    """Configure logging for the demonstration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(name)s - %(message)s'
    )


def print_separator(title: str) -> None:
    """Print a formatted separator with title."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_editor_state(editor: TextEditor, invoker: TextEditorInvoker) -> None:
    """Print current state of editor and command history."""
    print(f"\nEditor State:")
    print(f"  {editor}")
    print(f"\nCommand History:")
    print(f"  Can Undo: {invoker.can_undo()} ({invoker.get_undo_stack_size()} commands)")
    print(f"  Can Redo: {invoker.can_redo()} ({invoker.get_redo_stack_size()} commands)")
    
    if invoker.get_last_command_description():
        print(f"  Last Command: {invoker.get_last_command_description()}")
    if invoker.get_next_redo_description():
        print(f"  Next Redo: {invoker.get_next_redo_description()}")


def demonstrate_basic_operations() -> tuple[TextEditor, TextEditorInvoker]:
    """Demonstrate basic text editor operations with commands."""
    print_separator("Basic Text Editor Operations")
    
    # Create editor and invoker
    editor = TextEditor()
    invoker = TextEditorInvoker()
    
    print("Creating text editor and invoker...")
    print_editor_state(editor, invoker)
    
    # Insert some initial text
    print("\n1. Inserting 'Hello World' at position 0")
    insert_cmd = InsertTextCommand(editor, 0, "Hello World")
    invoker.execute_command(insert_cmd)
    print_editor_state(editor, invoker)
    
    # Insert more text
    print("\n2. Inserting '!' at the end")
    insert_cmd2 = InsertTextCommand(editor, editor.length, "!")
    invoker.execute_command(insert_cmd2)
    print_editor_state(editor, invoker)
    
    # Insert text in the middle
    print("\n3. Inserting ' Beautiful' at position 5")
    insert_cmd3 = InsertTextCommand(editor, 5, " Beautiful")
    invoker.execute_command(insert_cmd3)
    print_editor_state(editor, invoker)
    
    return editor, invoker


def demonstrate_undo_redo(editor: TextEditor, invoker: TextEditorInvoker) -> None:
    """Demonstrate undo/redo functionality."""
    print_separator("Undo/Redo Operations")
    
    print("Current state before undo operations:")
    print_editor_state(editor, invoker)
    
    # Undo last command
    print("\n1. Undoing last command (insert ' Beautiful')")
    success = invoker.undo()
    print(f"Undo successful: {success}")
    print_editor_state(editor, invoker)
    
    # Undo another command
    print("\n2. Undoing another command (insert '!')")
    success = invoker.undo()
    print(f"Undo successful: {success}")
    print_editor_state(editor, invoker)
    
    # Redo a command
    print("\n3. Redoing last undone command (insert '!')")
    success = invoker.redo()
    print(f"Redo successful: {success}")
    print_editor_state(editor, invoker)
    
    # Try to redo when nothing to redo
    print("\n4. Redoing again (should have ' Beautiful' to redo)")
    success = invoker.redo()
    print(f"Redo successful: {success}")
    print_editor_state(editor, invoker)


def demonstrate_delete_operations(editor: TextEditor, invoker: TextEditorInvoker) -> None:
    """Demonstrate delete operations with undo/redo."""
    print_separator("Delete Operations")
    
    print("Current state:")
    print_editor_state(editor, invoker)
    
    # Delete some text
    print("\n1. Deleting 'Beautiful ' (10 characters at position 5)")
    delete_cmd = DeleteTextCommand(editor, 5, 10)
    invoker.execute_command(delete_cmd)
    print_editor_state(editor, invoker)
    
    # Delete more text
    print("\n2. Deleting 'World' (5 characters at position 6)")
    delete_cmd2 = DeleteTextCommand(editor, 6, 5)
    invoker.execute_command(delete_cmd2)
    print_editor_state(editor, invoker)
    
    # Undo delete operations
    print("\n3. Undoing delete 'World'")
    invoker.undo()
    print_editor_state(editor, invoker)
    
    print("\n4. Undoing delete 'Beautiful '")
    invoker.undo()
    print_editor_state(editor, invoker)


def demonstrate_formatting_operations(editor: TextEditor, invoker: TextEditorInvoker) -> None:
    """Demonstrate text formatting operations."""
    print_separator("Text Formatting Operations")
    
    print("Current state:")
    print_editor_state(editor, invoker)
    
    # Apply bold formatting
    print("\n1. Applying BOLD formatting to 'Beautiful' (position 6-15)")
    format_cmd = FormatTextCommand(editor, 6, 9, TextFormat.BOLD)
    invoker.execute_command(format_cmd)
    print_editor_state(editor, invoker)
    
    # Apply italic formatting to overlapping text
    print("\n2. Applying ITALIC formatting to 'World!' (position 15-21)")
    format_cmd2 = FormatTextCommand(editor, 15, 6, TextFormat.ITALIC)
    invoker.execute_command(format_cmd2)
    print_editor_state(editor, invoker)
    
    # Apply underline to the entire text
    print("\n3. Applying UNDERLINE formatting to entire text")
    format_cmd3 = FormatTextCommand(editor, 0, editor.length, TextFormat.UNDERLINE)
    invoker.execute_command(format_cmd3)
    print_editor_state(editor, invoker)
    
    # Undo formatting operations
    print("\n4. Undoing UNDERLINE formatting")
    invoker.undo()
    print_editor_state(editor, invoker)
    
    print("\n5. Undoing ITALIC formatting")
    invoker.undo()
    print_editor_state(editor, invoker)


def demonstrate_macro_commands(editor: TextEditor, invoker: TextEditorInvoker) -> None:
    """Demonstrate macro command functionality."""
    print_separator("Macro Command Operations")
    
    print("Current state:")
    print_editor_state(editor, invoker)
    
    # Create a macro that adds signature
    print("\n1. Creating macro to add signature")
    signature_commands = [
        InsertTextCommand(editor, editor.length, "\n\n"),
        InsertTextCommand(editor, editor.length + 2, "Best regards,"),
        InsertTextCommand(editor, editor.length + 15, "\nJohn Doe")
    ]
    
    # Note: We need to calculate positions dynamically for the macro
    # Let's create a simpler version
    macro_cmd = MacroCommand([
        InsertTextCommand(editor, editor.length, "\n\n"),
    ], "Add signature block")
    
    # Add commands one by one to handle position calculations
    current_pos = editor.length + 2
    macro_cmd.add_command(InsertTextCommand(editor, current_pos, "Best regards,"))
    macro_cmd.add_command(InsertTextCommand(editor, current_pos + 13, "\nJohn Doe"))
    
    invoker.execute_command(macro_cmd)
    print_editor_state(editor, invoker)
    
    # Undo the entire macro
    print("\n2. Undoing macro command (should remove entire signature)")
    invoker.undo()
    print_editor_state(editor, invoker)
    
    # Redo the macro
    print("\n3. Redoing macro command")
    invoker.redo()
    print_editor_state(editor, invoker)


def demonstrate_error_handling(editor: TextEditor, invoker: TextEditorInvoker) -> None:
    """Demonstrate error handling in command execution."""
    print_separator("Error Handling")
    
    print("Current state:")
    print_editor_state(editor, invoker)
    
    # Try to delete beyond bounds
    print("\n1. Attempting to delete beyond text bounds")
    try:
        delete_cmd = DeleteTextCommand(editor, 50, 10)
        invoker.execute_command(delete_cmd)
    except ValueError as e:
        print(f"Expected error caught: {e}")
        print_editor_state(editor, invoker)
    
    # Try to insert at invalid position
    print("\n2. Attempting to insert at invalid position")
    try:
        insert_cmd = InsertTextCommand(editor, -5, "Invalid")
        invoker.execute_command(insert_cmd)
    except ValueError as e:
        print(f"Expected error caught: {e}")
        print_editor_state(editor, invoker)
    
    # Try to undo when nothing left to undo (after clearing)
    print("\n3. Clearing history and trying to undo")
    invoker.clear_history()
    success = invoker.undo()
    print(f"Undo after clear successful: {success}")
    print_editor_state(editor, invoker)


def demonstrate_command_history() -> None:
    """Demonstrate command history functionality."""
    print_separator("Command History")
    
    editor = TextEditor()
    invoker = TextEditorInvoker(max_history=3)  # Small history for demonstration
    
    # Execute several commands
    commands = [
        InsertTextCommand(editor, 0, "First"),
        InsertTextCommand(editor, 5, " Second"),
        InsertTextCommand(editor, 12, " Third"),
        InsertTextCommand(editor, 18, " Fourth"),
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n{i}. Executing: {cmd.get_description()}")
        invoker.execute_command(cmd)
        history = invoker.get_history_summary()
        print(f"   Undo stack: {len(history['undo'])} commands")
        print(f"   Redo stack: {len(history['redo'])} commands")
    
    print(f"\nFinal state:")
    print_editor_state(editor, invoker)
    
    # Show complete history
    history = invoker.get_history_summary()
    print(f"\nComplete History Summary:")
    print(f"Undo commands (most recent first):")
    for cmd_desc in history['undo']:
        print(f"  - {cmd_desc}")
    print(f"Redo commands:")
    for cmd_desc in history['redo']:
        print(f"  - {cmd_desc}")


def main() -> None:
    """Main demonstration function."""
    print("Command Pattern Implementation - Text Editor Demo")
    print("=" * 60)
    
    setup_logging()
    
    # Run all demonstrations
    editor, invoker = demonstrate_basic_operations()
    demonstrate_undo_redo(editor, invoker)
    demonstrate_delete_operations(editor, invoker)
    demonstrate_formatting_operations(editor, invoker)
    demonstrate_macro_commands(editor, invoker)
    demonstrate_error_handling(editor, invoker)
    demonstrate_command_history()
    
    print_separator("Demo Complete")
    print("The Command pattern demonstration has finished successfully!")
    print("Key features demonstrated:")
    print("- Command encapsulation and execution")
    print("- Undo/redo functionality with command stacks")
    print("- Text insertion, deletion, and formatting operations")
    print("- Macro commands for complex operations")
    print("- Error handling and recovery")
    print("- Command history management")


if __name__ == "__main__":
    main()