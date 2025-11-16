import { describe, it, expect } from "vitest";
import {
  formatCurrency,
  formatDate,
  formatTime,
  formatDuration,
  formatPhoneNumber,
  truncateText,
  capitalizeFirstLetter,
  formatRating,
} from "~/utils/shared/formatters";

describe("Formatters", () => {
  describe("formatCurrency", () => {
    it("formats currency with default INR", () => {
      const result = formatCurrency(1000);
      expect(result).toContain("1,000");
    });

    it("formats currency with custom currency", () => {
      const result = formatCurrency(1000, "USD");
      expect(result).toContain("1,000");
    });
  });

  describe("formatDate", () => {
    it("formats date with default format", () => {
      const result = formatDate("2024-01-15");
      expect(result).toBe("15 Jan 2024");
    });

    it("formats date with custom format", () => {
      const result = formatDate("2024-01-15", "yyyy-MM-dd");
      expect(result).toBe("2024-01-15");
    });
  });

  describe("formatTime", () => {
    it("formats time correctly", () => {
      const result = formatTime("2024-01-15T14:30:00");
      expect(result).toBe("02:30 pm");
    });
  });

  describe("formatDuration", () => {
    it("formats duration in hours and minutes", () => {
      expect(formatDuration(150)).toBe("2h 30min");
    });

    it("formats duration with only hours", () => {
      expect(formatDuration(120)).toBe("2h");
    });

    it("formats duration with only minutes", () => {
      expect(formatDuration(45)).toBe("45min");
    });
  });

  describe("formatPhoneNumber", () => {
    it("formats 10-digit phone number", () => {
      const result = formatPhoneNumber("1234567890");
      expect(result).toBe("(123) 456-7890");
    });

    it("returns original if not 10 digits", () => {
      const result = formatPhoneNumber("12345");
      expect(result).toBe("12345");
    });
  });

  describe("truncateText", () => {
    it("truncates text longer than max length", () => {
      const result = truncateText("This is a long text", 10);
      expect(result).toBe("This is a ...");
    });

    it("does not truncate text shorter than max length", () => {
      const result = truncateText("Short", 10);
      expect(result).toBe("Short");
    });
  });

  describe("capitalizeFirstLetter", () => {
    it("capitalizes first letter", () => {
      expect(capitalizeFirstLetter("hello")).toBe("Hello");
    });

    it("lowercases rest of the string", () => {
      expect(capitalizeFirstLetter("hELLO")).toBe("Hello");
    });
  });

  describe("formatRating", () => {
    it("formats rating to 1 decimal place", () => {
      expect(formatRating(8.567)).toBe("8.6");
    });
  });
});
