# 📝 CODE DOCUMENTATION REQUIREMENTS (MANDATORY)

## Source File Documentation Standards
Every source file MUST include comprehensive documentation that eliminates the need to search external documentation for understanding:

### File Header Requirements (All Files)
```typescript
/**
 * @fileoverview [Concise description of file purpose and functionality]
 * @author [Persona Name] v[Version] - [Date]
 * @architecture [Component it belongs to - Frontend/Backend/Integration]
 * @responsibility [Primary responsibility within system architecture]
 * @dependencies [Key dependencies and why needed]
 * @integration_points [How this connects to other system components]
 * @testing_strategy [What aspects require testing and why]
 * @governance [Which governance frameworks apply - Sarah's/Alex's/Specialist]
 * 
 * Business Logic Summary:
 * - [Primary business rules implemented]
 * - [Key validation logic]
 * - [Error handling approach]
 * 
 * Architecture Integration:
 * - [How this fits in system overview]
 * - [Security boundaries involved]
 * - [Performance considerations]
 */
```

### Class Documentation Requirements
```typescript
/**
 * @class [ClassName]
 * @description [What this class does and why it exists]
 * @architecture_role [How this fits in the overall system design]
 * @business_logic [Key business rules this class enforces]
 * @failure_modes [What can break and how it's handled - Sarah's Framework]
 * @debugging_info [Key information for 3AM debugging - Alex's Framework]
 * 
 * Defensive Programming Patterns:
 * - [Circuit breakers implemented]
 * - [Input validation approach]
 * - [Resource limits enforced]
 * 
 * Integration Boundaries:
 * - [External systems accessed]
 * - [Security controls applied]
 * - [Error propagation strategy]
 */
class ExampleService {
```

### Method Documentation Requirements
```typescript
/**
 * @method [methodName]
 * @description [What this method does in business context]
 * @business_rule [Business logic implemented by this method]
 * @validation [Input validation performed and why]
 * @side_effects [Any state changes or external calls made]
 * @error_handling [How errors are detected and handled]
 * @performance [Expected performance characteristics]
 * @testing_requirements [What scenarios must be tested]
 * 
 * @param {type} paramName - [Business meaning and validation rules]
 * @returns {type} [What is returned and under what conditions]
 * @throws {ErrorType} [When and why this error is thrown]
 * 
 * Architecture Notes:
 * - [How this method fits in component design]
 * - [Security considerations]
 * - [Monitoring/observability hooks]
 * 
 * Sarah's Framework Check:
 * - What breaks first: [Primary failure mode]
 * - How we know: [Detection mechanism]
 * - Plan B: [Fallback strategy]
 */
async exampleMethod(param: Type): Promise<ReturnType> {
```

### Business Logic Documentation
All business logic implementations MUST include:

```typescript
// BUSINESS RULE: [Clear statement of business rule being implemented]
// VALIDATION: [What validation is performed and why]
// ERROR HANDLING: [How business rule violations are handled]
// AUDIT TRAIL: [What gets logged for compliance/debugging]

if (businessCondition) {
    // BUSINESS LOGIC: [Explain the business reasoning]
    // SARAH'S FRAMEWORK: This handles failure mode X with fallback Y
    // ALEX'S 3AM TEST: Debug info includes correlation ID and rule name
    
    return processBusinessRule(data);
}
```

### Integration Point Documentation
```typescript
/**
 * INTEGRATION POINT: [System boundary being crossed]
 * SECURITY BOUNDARY: [Security controls at this point]
 * ERROR PROPAGATION: [How errors are handled across boundary]
 * MONITORING: [What metrics are collected here]
 * GOVERNANCE: [AI governance checks if applicable]
 */
async callExternalSystem(request: RequestType): Promise<ResponseType> {
    // CIRCUIT BREAKER: Protect against external system failures
    // RATE LIMITING: Prevent abuse of external resources  
    // AUDIT LOGGING: Record all boundary crossings for compliance
}
```

## Documentation Validation Rules

### Pre-Commit Documentation Checks (MANDATORY)
```bash
#!/bin/bash
# validate-code-documentation.sh

# Check for mandatory file headers
find . -name "*.ts" -o -name "*.py" | while read file; do
    if ! grep -q "@fileoverview" "$file"; then
        echo "ERROR: Missing @fileoverview in $file"
        exit 1
    fi
    
    if ! grep -q "@business_logic" "$file"; then
        echo "ERROR: Missing business logic documentation in $file" 
        exit 1
    fi
done

# Check for class documentation
grep -r "^class\|^export class" --include="*.ts" | while read -r line; do
    file=$(echo "$line" | cut -d: -f1)
    if ! grep -A 10 -B 5 "$line" "$file" | grep -q "@architecture_role"; then
        echo "ERROR: Missing architecture documentation for class in $file"
        exit 1
    fi
done

# Check for method documentation on public methods
# (Implementation would scan for public methods and verify documentation)

echo "✅ All code documentation requirements met"
```

### Documentation Completeness Score
Every source file receives a documentation score:
```
File Documentation Score = (
    File Header (25 points) +
    Class Documentation (25 points) + 
    Method Documentation (25 points) +
    Business Logic Comments (25 points)
) / 100

Minimum Score Required: 90/100
```

### Integration with Architecture Documentation
Code documentation must reference architecture documentation:
```typescript
/**
 * @architecture_reference docs/architecture/component-design/frontend-architecture.md#ipc-security
 * @security_reference docs/architecture/component-design/security-boundaries.md#ipc-boundary
 * @api_contract_reference docs/architecture/data-flow/api-contracts.md#agent-api
 */
```

## Specialist Persona Documentation Requirements

### When Creating Business Logic (Requires Specialist)
```typescript
/**
 * SPECIALIST DECISION: [Specialist Name] v[Version] - [Date]
 * DECISION REFERENCE: DECISIONS.md#[decision-id]
 * RATIONALE: [Why this approach was chosen by specialist]
 * CONSTRAINTS: [What cannot be changed without specialist approval]
 * VALIDATION: [How to verify correct implementation]
 */
```

### AI Governance Documentation
```typescript
/**
 * AI GOVERNANCE: This component integrates with AI governance system
 * GOVERNANCE_HOOKS: [Which hooks are triggered - pre/post agent spawn, etc.]
 * PERSONA_ORCHESTRATION: [Which personas are activated and when]
 * VALIDATION_PIPELINE: [Which of the 4 gates this passes through]
 * COST_CONTROLS: [Token limits and budget enforcement]
 */
```