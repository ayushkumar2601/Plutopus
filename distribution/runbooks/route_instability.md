# Runbook: Route Instability Troubleshooting

## Diagnostic Checklist
1. **BGP Flapping**: Verify BGP neighbor states and prefix counts.
2. **OSPF Hello Packets**: Ensure Hello/Dead intervals match across interfaces.
3. **Route Dampening**: Check if dampened routes are blocking path selections.

## Mitigation Actions
- Increase OSPF hello/dead parameters to tolerate short network drops.
- Enable BGP route flap dampening.
- Check static route tracking configurations.
