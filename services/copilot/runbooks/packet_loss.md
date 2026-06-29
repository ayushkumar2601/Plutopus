# Runbook: Packet Loss Troubleshooting

## Diagnostic Checklist
1. **Check Interface CRC Errors**: Inspect physical interface statistics for CRC/input errors.
2. **Review Tunnel Keepalives**: Check if tunnel keepalive packets are dropping.
3. **Verify MTU/MSS settings**: Ensure packets are not being dropped due to oversized payload sizing.

## Mitigation Actions
- Adjust TCP MSS adjustments on the edge router interface.
- Initiate interface loopback tests to isolate copper/fiber physical errors.
- Failover traffic to secondary WAN provider.
