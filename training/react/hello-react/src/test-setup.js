import "@testing-library/jest-dom/vitest"; // vitest adapter (defines/extends expect)
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => cleanup());
