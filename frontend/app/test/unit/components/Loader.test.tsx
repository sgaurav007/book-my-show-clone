import { describe, it, expect } from "vitest";
import { renderWithProviders, screen } from "~/test/utils";
import { Loader } from "~/components/shared/Loader";

describe("Loader Component", () => {
  it("renders loader with default size", () => {
    renderWithProviders(<Loader />);
    const loader = screen.getByRole("progressbar");
    expect(loader).toBeInTheDocument();
  });

  it("renders loader with custom size", () => {
    renderWithProviders(<Loader size={60} />);
    const loader = screen.getByRole("progressbar");
    expect(loader).toBeInTheDocument();
  });

  it("renders fullscreen loader when fullScreen prop is true", () => {
    const { container } = renderWithProviders(<Loader fullScreen />);
    const loaderContainer = container.querySelector("div");
    expect(loaderContainer).toHaveStyle({ minHeight: "100vh" });
  });

  it("renders regular loader when fullScreen prop is false", () => {
    const { container } = renderWithProviders(<Loader fullScreen={false} />);
    const loaderContainer = container.querySelector("div");
    expect(loaderContainer).not.toHaveStyle({ minHeight: "100vh" });
  });
});
