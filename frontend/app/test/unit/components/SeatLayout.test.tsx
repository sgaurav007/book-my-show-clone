import { describe, it, expect, vi } from "vitest";
import { renderWithProviders, screen, fireEvent } from "~/test/utils";
import { SeatLayout } from "~/components/shared/SeatLayout";
import type { Seat } from "~/utils/shared/types";

const mockSeats: Seat[] = [
  {
    id: "1",
    row: "A",
    column: 1,
    seatNumber: "A1",
    type: "NORMAL",
    status: "AVAILABLE",
    price: 200,
  },
  {
    id: "2",
    row: "A",
    column: 2,
    seatNumber: "A2",
    type: "NORMAL",
    status: "BOOKED",
    price: 200,
  },
  {
    id: "3",
    row: "A",
    column: 3,
    seatNumber: "A3",
    type: "PREMIUM",
    status: "AVAILABLE",
    price: 300,
  },
];

describe("SeatLayout Component", () => {
  it("renders screen indicator", () => {
    renderWithProviders(
      <SeatLayout seats={mockSeats} selectedSeats={[]} onSeatSelect={vi.fn()} />
    );
    expect(screen.getByText("Screen This Way")).toBeInTheDocument();
  });

  it("renders seat legend", () => {
    renderWithProviders(
      <SeatLayout seats={mockSeats} selectedSeats={[]} onSeatSelect={vi.fn()} />
    );
    expect(screen.getByText("Available")).toBeInTheDocument();
    expect(screen.getByText("Selected")).toBeInTheDocument();
    expect(screen.getByText("Booked")).toBeInTheDocument();
    expect(screen.getByText("Locked")).toBeInTheDocument();
  });

  it("calls onSeatSelect when available seat is clicked", () => {
    const onSeatSelect = vi.fn();
    renderWithProviders(
      <SeatLayout seats={mockSeats} selectedSeats={[]} onSeatSelect={onSeatSelect} />
    );

    const seat1Button = screen.getByRole("button", { name: "1" });
    fireEvent.click(seat1Button);

    expect(onSeatSelect).toHaveBeenCalledWith("1");
  });

  it("does not call onSeatSelect when booked seat is clicked", () => {
    const onSeatSelect = vi.fn();
    renderWithProviders(
      <SeatLayout seats={mockSeats} selectedSeats={[]} onSeatSelect={onSeatSelect} />
    );

    const seat2Button = screen.getByRole("button", { name: "2" });
    fireEvent.click(seat2Button);

    expect(onSeatSelect).not.toHaveBeenCalled();
  });

  it("renders selected seats with selected color", () => {
    renderWithProviders(
      <SeatLayout seats={mockSeats} selectedSeats={["1"]} onSeatSelect={vi.fn()} />
    );

    const seat1Button = screen.getByRole("button", { name: "1" });
    expect(seat1Button).toHaveStyle({ backgroundColor: "#2196F3" });
  });

  it("disables seats when max seats are selected", () => {
    const selectedSeats = Array.from({ length: 10 }, (_, i) => `${i}`);
    renderWithProviders(
      <SeatLayout
        seats={mockSeats}
        selectedSeats={selectedSeats}
        onSeatSelect={vi.fn()}
      />
    );

    const seat3Button = screen.getByRole("button", { name: "3" });
    expect(seat3Button).toBeDisabled();
  });
});
