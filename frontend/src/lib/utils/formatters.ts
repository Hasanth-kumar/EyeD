import { format, parseISO } from 'date-fns';

export function formatNumber(value: number): string {
  return new Intl.NumberFormat().format(value);
}

export function formatPercentage(value: number, decimals = 0): string {
  const normalized = value <= 1 ? value * 100 : value;
  return `${normalized.toFixed(decimals)}%`;
}

export function formatDate(value: string, style: 'short' | 'long' = 'short'): string {
  const date = parseISO(value);
  return format(date, style === 'long' ? 'PPPP' : 'PP');
}
