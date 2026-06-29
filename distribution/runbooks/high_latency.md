# Runbook: High Latency Troubleshooting

## Diagnostic Checklist
1. **Verify MPLS/Internet latency metrics**: Inspect tunnel metrics for the last 15-30 minutes.
2. **Review underlay path**: Identify if there is an underlay route shift or carrier issue.
3. **Verify interface utilization**: Check if high link utilization is causing queuing delay.
4. **Inspect QoS queue drops**: Ensure real-time traffic is mapped to priority queues.

## Mitigation Actions
- Shift non-critical traffic classes off the primary tunnel.
- Enable QoS path shaping policies.
- Route traffic via the backup WAN tunnel if underlay conditions are superior.
