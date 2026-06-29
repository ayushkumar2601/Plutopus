# Runbook: Tunnel Failure Troubleshooting

## Diagnostic Checklist
1. **IPsec/BGP State Check**: Check if BGP peer is stuck in Active/Idle state.
2. **IKE Security Association**: Ensure Phase 1 and Phase 2 keys negotiate correctly.
3. **Check Routing Tables**: Verify if default underlay route is missing.

## Mitigation Actions
- Restart BGP peering session (`clear ip bgp *`).
- Force IPsec SA renegotiation.
- Verify ISP gateway reachability via ICMP echo.
