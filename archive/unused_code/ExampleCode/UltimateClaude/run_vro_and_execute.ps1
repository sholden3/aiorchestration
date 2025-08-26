# Run the VRO crisis system
$output = python -c "
# Your VRO crisis code
from vro_crisis_orchestrator import VRO_CRISIS_ORCHESTRATOR
crisis_input = 'Harbor Freight and Home Depot delivery systems are returning NULL for all shipments. The VRO timing calculations have circular dependencies causing infinite loops. System claims nothing is deliverable. Complete business shutdown. Need immediate fix. Path to top level folder that holds folder for project: C:\Users\wesho\Desktop\WorkProjects\ClaudeCodeEnhancements\cache_optimizer_project\test_projects Path for the actual solution level for the project: C:\Users\wesho\Desktop\WorkProjects\ClaudeCodeEnhancements\cache_optimizer_project\test_projects\vro Entry point to solution that we must build from (circular project dependencies): C:\Users\wesho\Desktop\WorkProjects\ClaudeCodeEnhancements\cache_optimizer_project\test_projects\vro\VRO'
analysis = VRO_CRISIS_ORCHESTRATOR.analyze_vro_request(crisis_input)
enhanced_prompt = VRO_CRISIS_ORCHESTRATOR._generate_vro_orchestration_prompt(analysis)
print(enhanced_prompt)
"

# Save enhanced prompt to file for Claude Code
$output | Out-File -FilePath "enhanced_command.txt" -Encoding UTF8

Write-Host "Enhanced prompt generated. Use contents of enhanced_command.txt as next Claude Code command."