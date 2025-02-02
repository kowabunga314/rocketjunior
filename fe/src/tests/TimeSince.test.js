import React from 'react';
import { render, screen } from '@testing-library/react';
import TimeSince from '../components/TimeSince';

/**
 * Unit tests for TimeSince component. Tests add offsets to timestamp
 * objects to create a time delta that will produce a certain output based
 * on the logic of the TimeSince component.
 */
describe('TimeSince Component', () => {
  // Freeze time: set a fixed current time
  beforeAll(() => {
    jest.useFakeTimers('modern');
    // Set "now" to January 1, 2020 00:00:00 UTC
    jest.setSystemTime(new Date('2020-01-01T00:00:00Z'));
  });

  afterAll(() => {
    jest.useRealTimers();
  });

  test('displays seconds ago', () => {
    // 30 seconds ago from Jan 1, 2020 00:00:00 UTC
    const timestamp = new Date('2020-01-01T00:00:00Z').getTime() - 30 * 1000;
    render(<TimeSince timestamp={timestamp} />);
    expect(screen.getByText(/Created 30 seconds ago/i)).toBeInTheDocument();
  });

  test('displays minutes ago', () => {
    // 5 minutes ago
    const timestamp = new Date('2020-01-01T00:00:00Z').getTime() - 5 * 60 * 1000;
    render(<TimeSince timestamp={timestamp} />);
    expect(screen.getByText(/Created 5 minutes ago/i)).toBeInTheDocument();
  });

  test('displays hours ago', () => {
    // 2 hours ago
    const timestamp = new Date('2020-01-01T00:00:00Z').getTime() - 2 * 60 * 60 * 1000;
    render(<TimeSince timestamp={timestamp} />);
    expect(screen.getByText(/Created 2 hours ago/i)).toBeInTheDocument();
  });

  test('displays days ago', () => {
    // 3 days ago
    const timestamp = new Date('2020-01-01T00:00:00Z').getTime() - 3 * 24 * 60 * 60 * 1000;
    render(<TimeSince timestamp={timestamp} />);
    expect(screen.getByText(/Created 3 days ago/i)).toBeInTheDocument();
  });

  test('displays years ago', () => {
    // 2 years ago
    const timestamp = new Date('2020-01-01T00:00:00Z').getTime() - 2 * 365 * 24 * 60 * 60 * 1000;
    render(<TimeSince timestamp={timestamp} />);
    expect(screen.getByText(/Created 2 years ago/i)).toBeInTheDocument();
  });
});
