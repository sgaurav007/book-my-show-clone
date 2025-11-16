import { describe, it, expect, vi } from "vitest";
import { renderWithProviders, screen, fireEvent } from "~/test/utils";
import { TheaterCard } from "~/components/shared/TheaterCard";
import type { Theater } from "~/utils/shared/types";

const mockTheater: Theater = {
  id: "1",
  name: "Cineplex Theater",
  address: "123 Main St",
  city: "Mumbai",
  state: "Maharashtra",
  zipCode: "400001",
  totalScreens: 5,
  amenities: ["Parking", "Food Court", "3D"],
};

describe("TheaterCard Component", () => {
  it("renders theater name", () => {
    renderWithProviders(<TheaterCard theater={mockTheater} />);
    expect(screen.getByText("Cineplex Theater")).toBeInTheDocument();
  });

  it("renders theater address", () => {
    renderWithProviders(<TheaterCard theater={mockTheater} />);
    expect(screen.getByText(/123 Main St/)).toBeInTheDocument();
    expect(screen.getByText(/Mumbai/)).toBeInTheDocument();
  });

  it("renders amenities", () => {
    renderWithProviders(<TheaterCard theater={mockTheater} />);
    expect(screen.getByText("Parking")).toBeInTheDocument();
    expect(screen.getByText("Food Court")).toBeInTheDocument();
    expect(screen.getByText("3D")).toBeInTheDocument();
  });

  it("renders show times when provided", () => {
    const showTimes = ["10:00 AM", "2:00 PM", "6:00 PM"];
    renderWithProviders(<TheaterCard theater={mockTheater} showTimes={showTimes} />);

    expect(screen.getByText("10:00 AM")).toBeInTheDocument();
    expect(screen.getByText("2:00 PM")).toBeInTheDocument();
    expect(screen.getByText("6:00 PM")).toBeInTheDocument();
  });

  it("calls onShowTimeClick when show time is clicked", () => {
    const onShowTimeClick = vi.fn();
    const showTimes = ["10:00 AM", "2:00 PM"];

    renderWithProviders(
      <TheaterCard
        theater={mockTheater}
        showTimes={showTimes}
        onShowTimeClick={onShowTimeClick}
      />
    );

    fireEvent.click(screen.getByText("10:00 AM"));
    expect(onShowTimeClick).toHaveBeenCalledWith("10:00 AM");
  });

  it("does not render show times section when not provided", () => {
    renderWithProviders(<TheaterCard theater={mockTheater} />);
    expect(screen.queryByText("Show Times")).not.toBeInTheDocument();
  });
});
