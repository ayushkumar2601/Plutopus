# Runbook: Link Congestion Troubleshooting

## Diagnostic Checklist
1. **Top Talkers**: Identify source/destination IPs consuming link bandwidth.
2. **Buffer Overruns**: Review if interface output drops are increasing.
3. **WAN SLA Rules**: Check if SD-WAN SLA rules are forcing too many tunnels onto a single path.

## Mitigation Actions
- Enable traffic rate limiting for guest networks.
- Apply QoS shaping policies to voice/critical traffic.
- Enable load balancing across multiple active WAN tunnels.
