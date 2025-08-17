import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App.jsx";

describe("App", () => {
  it("greets the world by default", () => {
    render(<App />);
    expect(screen.getByRole("heading")).toHaveTextContent("Hello, World!");
  });

  it("greets by name when typed", async () => {
    render(<App />);
    const input = screen.getByLabelText("name");
    await fireEvent.input(input, { target: { value: "Alice" } });
    expect(screen.getByRole("heading")).toHaveTextContent("Hello, Alice!");
  });
});
