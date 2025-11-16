import { describe, it, expect } from "vitest";
import { renderWithProviders, screen } from "~/test/utils";
import { MovieCard } from "~/components/shared/MovieCard";
import type { Movie } from "~/utils/shared/types";

const mockMovie: Movie = {
  id: "1",
  title: "Test Movie",
  description: "A test movie description",
  genre: ["ACTION", "THRILLER"],
  language: "ENGLISH",
  duration: 150,
  rating: "UA",
  releaseDate: "2024-01-01",
  posterUrl: "https://example.com/poster.jpg",
  cast: ["Actor 1", "Actor 2"],
  director: "Director Name",
  averageRating: 8.5,
  totalReviews: 100,
  nowShowing: true,
  comingSoon: false,
};

describe("MovieCard Component", () => {
  it("renders movie title", () => {
    renderWithProviders(<MovieCard movie={mockMovie} />);
    expect(screen.getByText("Test Movie")).toBeInTheDocument();
  });

  it("renders movie rating badge", () => {
    renderWithProviders(<MovieCard movie={mockMovie} />);
    expect(screen.getByText("UA")).toBeInTheDocument();
  });

  it("renders movie genres", () => {
    renderWithProviders(<MovieCard movie={mockMovie} />);
    expect(screen.getByText("ACTION")).toBeInTheDocument();
    expect(screen.getByText("THRILLER")).toBeInTheDocument();
  });

  it("renders movie language and duration", () => {
    renderWithProviders(<MovieCard movie={mockMovie} />);
    expect(screen.getByText(/ENGLISH/)).toBeInTheDocument();
    expect(screen.getByText(/2h 30min/)).toBeInTheDocument();
  });

  it("renders average rating when available", () => {
    renderWithProviders(<MovieCard movie={mockMovie} />);
    expect(screen.getByText("8.5")).toBeInTheDocument();
  });

  it("does not render rating when averageRating is 0", () => {
    const movieWithoutRating = { ...mockMovie, averageRating: 0 };
    renderWithProviders(<MovieCard movie={movieWithoutRating} />);
    expect(screen.queryByText("8.5")).not.toBeInTheDocument();
  });

  it("has link to movie detail page", () => {
    const { container } = renderWithProviders(<MovieCard movie={mockMovie} />);
    const link = container.querySelector('a[href="/movies/1"]');
    expect(link).toBeInTheDocument();
  });
});
