export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phone: string;
  role: "USER" | "ADMIN" | "THEATER_OWNER";
  createdAt: string;
}

export interface Movie {
  id: string;
  title: string;
  description: string;
  genre: string[];
  language: string;
  duration: number;
  rating: "U" | "UA" | "A" | "S";
  releaseDate: string;
  posterUrl: string;
  trailerUrl?: string;
  cast: string[];
  director: string;
  averageRating: number;
  totalReviews: number;
  nowShowing: boolean;
  comingSoon: boolean;
}

export interface Theater {
  id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  totalScreens: number;
  amenities: string[];
}

export interface Screen {
  id: string;
  theaterId: string;
  name: string;
  totalSeats: number;
  seatLayout: SeatLayout;
}

export interface SeatLayout {
  rows: number;
  columns: number;
  seats: Seat[];
}

export interface Seat {
  id: string;
  row: string;
  column: number;
  seatNumber: string;
  type: "NORMAL" | "PREMIUM" | "VIP";
  status: "AVAILABLE" | "BOOKED" | "SELECTED" | "LOCKED";
  price: number;
}

export interface Show {
  id: string;
  movieId: string;
  screenId: string;
  theaterId: string;
  movie: Movie;
  theater: Theater;
  screen: Screen;
  startTime: string;
  endTime: string;
  date: string;
  basePrice: number;
  availableSeats: number;
}

export interface Booking {
  id: string;
  userId: string;
  showId: string;
  seats: BookedSeat[];
  totalAmount: number;
  status: "PENDING" | "CONFIRMED" | "CANCELLED" | "EXPIRED";
  bookingDate: string;
  show: Show;
  payment?: Payment;
}

export interface BookedSeat {
  id: string;
  bookingId: string;
  seatId: string;
  seat: Seat;
  price: number;
}

export interface Payment {
  id: string;
  bookingId: string;
  amount: number;
  method: "CREDIT_CARD" | "DEBIT_CARD" | "UPI" | "NET_BANKING" | "WALLET";
  status: "PENDING" | "SUCCESS" | "FAILED" | "REFUNDED";
  transactionId?: string;
  paymentDate: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phone: string;
}

export interface BookingRequest {
  showId: string;
  seatIds: string[];
}

export interface PaymentRequest {
  bookingId: string;
  method: "CREDIT_CARD" | "DEBIT_CARD" | "UPI" | "NET_BANKING" | "WALLET";
  cardNumber?: string;
  cardName?: string;
  cardExpiry?: string;
  cardCvv?: string;
  upiId?: string;
}

export interface MovieFilter {
  genre?: string;
  language?: string;
  rating?: string;
  search?: string;
}

export interface ShowFilter {
  movieId?: string;
  city?: string;
  date?: string;
  theaterId?: string;
}
