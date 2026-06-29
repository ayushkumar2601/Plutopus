# Runbook: Interface Flapping Troubleshooting

## Diagnostic Checklist
1. **Link Flap Counter**: Inspect syslog history to count flap events.
2. **Physical Layer Quality**: Inspect optical transceiver levels (DOM) or copper cable joins.
3. **Keepalive Timers**: Verify interface keepalive parameters.

## Mitigation Actions
- Enable link flap dampening (`carrier-delay` or `dampening`).
- Re-seat the SFP transceiver module.
- Swap physical cabling patch.
