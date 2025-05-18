import pandas as pd

class SupportResistance:

    def check_breach_after_pullback(self, df, levels, is_resistance=True, lookahead=5):
        results = []

        for idx, level_price in levels:
            breached = False
            pullback_done = False
            breach_idx = None
            breach_price = None
            breach_direction = 1 if is_resistance else -1
            follow_through_count = 0
            cumulative_move = 0.0

            for j in range(1, lookahead + 1):
                if idx + j >= len(df):
                    break

                direction = df['direction'].iloc[idx + j]

                # Pullback detection
                if is_resistance and not pullback_done and direction < 0:
                    pullback_done = True
                elif not is_resistance and not pullback_done and direction > 0:
                    pullback_done = True

                # Breach detection
                if pullback_done:
                    if is_resistance and df['high'].iloc[idx + j] > level_price:
                        breached = True
                        breach_idx = idx + j
                        breach_price = df['high'].iloc[breach_idx]
                        break
                    elif not is_resistance and df['low'].iloc[idx + j] < level_price:
                        breached = True
                        breach_idx = idx + j
                        breach_price = df['low'].iloc[breach_idx]
                        break

            # After breach, check follow-through
            if breached:
                for k in range(breach_idx + 1, len(df)):
                    move_dir = df['direction'].iloc[k]
                    if (is_resistance and move_dir > 0) or (not is_resistance and move_dir < 0):
                        follow_through_count += 1
                        if is_resistance:
                            cumulative_move += df['close'].iloc[k] - df['close'].iloc[k - 1]
                        else:
                            cumulative_move += df['close'].iloc[k - 1] - df['close'].iloc[k]
                    else:
                        break

            results.append({
                'type': 'resistance' if is_resistance else 'support',
                'level_index': idx,
                'level_price': level_price,
                'breached': breached,
                'breach_index': breach_idx,
                'breach_time': df['datetime'].iloc[breach_idx] if breach_idx else None,
                'breach_price': breach_price,
                'breach_direction': breach_direction if breached else None,
                'follow_through_count': follow_through_count if breached else None,
                'cumulative_move': round(cumulative_move, 2) if breached else None
            })

        return results

    def find_support_resistance_with_direction_window(self, df, window=2):
        support_levels = []
        resistance_levels = []

        for i in range(window, len(df) - window):
            prev_dir = df['direction'].iloc[i - window:i]
            next_dir = df['direction'].iloc[i:i + window]

            # Resistance: up trend then down trend
            if all(prev_dir > 0) and all(next_dir < 0):
                resistance_levels.append((i, df['high'].iloc[i]))

            # Support: down trend then up trend
            if all(prev_dir < 0) and all(next_dir > 0):
                support_levels.append((i, df['low'].iloc[i]))

        return support_levels, resistance_levels

    def analyze_structure_breaks(self, df, window=2, lookahead=5):
        support, resistance = self.find_support_resistance_with_direction_window(df, window=window)
        support_breaches = self.check_breach_after_pullback(df, support, is_resistance=False, lookahead=lookahead)
        resistance_breaches = self.check_breach_after_pullback(df, resistance, is_resistance=True, lookahead=lookahead)

        print("Support Breaches")
        print(support_breaches)
        print("Resistance Breaches")
        print(resistance_breaches)

        return support_breaches + resistance_breaches





