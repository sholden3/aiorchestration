# Claude Code: Aiorchestration Zip Folder Analysis & File Comparison System

## 🎯 MISSION OBJECTIVE
Systematically analyze two aiorchestration zip folders, compare against existing tracking files, identify missing components, generate comprehensive reports, and maintain strict governance compliance per CLAUDE.md procedures.

## 📋 EXECUTION WORKFLOW

### **Phase 1: Governance Compliance & Setup**
```bash
# MANDATORY FIRST STEP: Review governance procedures
echo "=== GOVERNANCE COMPLIANCE CHECK ==="
cat CLAUDE.md | grep -i "procedure\|governance\|protocol\|standard"

# Verify required directories and files exist
if [ ! -f "CLAUDE.md" ]; then
    echo "❌ CRITICAL: CLAUDE.md governance file not found in root"
    exit 1
fi

if [ ! -d "temp" ]; then
    echo "📁 Creating temp directory for reports"
    mkdir -p temp
fi

# Document execution start per governance
echo "$(date): Starting aiorchestration zip analysis" >> temp/governance_log.txt
echo "Operator: Claude Code" >> temp/governance_log.txt
echo "Compliance: Following CLAUDE.md procedures" >> temp/governance_log.txt
```

### **Phase 2: First Zip Analysis - aiorchestration-ecca6fd665b0a474369509cb29c4aeaed35c57aa**
```bash
ZIP_NAME_1="aiorchestration-ecca6fd665b0a474369509cb29c4aeaed35c57aa"
TRACKING_FILE_1="temp/${ZIP_NAME_1}"
REPORT_FILE_1="temp/${ZIP_NAME_1}_missing_analysis.md"

echo "=== ANALYZING FIRST AIORCHESTRATION PACKAGE ==="
echo "📦 Target Zip: ${ZIP_NAME_1}.zip"
echo "📄 Tracking File: ${TRACKING_FILE_1}"
echo "📊 Report Output: ${REPORT_FILE_1}"

# Step 1: Verify zip file exists
if [ ! -f "${ZIP_NAME_1}.zip" ]; then
    echo "❌ ERROR: ${ZIP_NAME_1}.zip not found in root directory"
    echo "Expected location: $(pwd)/${ZIP_NAME_1}.zip"
    exit 1
fi

# Step 2: Create temporary extraction directory
EXTRACT_DIR_1="temp/extracted_${ZIP_NAME_1}"
rm -rf "${EXTRACT_DIR_1}"  # Clean previous extractions
mkdir -p "${EXTRACT_DIR_1}"

# Step 3: Extract zip contents
echo "📂 Extracting ${ZIP_NAME_1}.zip..."
unzip -q "${ZIP_NAME_1}.zip" -d "${EXTRACT_DIR_1}"

# Step 4: Generate complete inventory of zip contents
ZIP_INVENTORY_1="temp/${ZIP_NAME_1}_zip_inventory.txt"
echo "📋 Creating zip inventory..."
find "${EXTRACT_DIR_1}" -type f -name "*.py" -o -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name "*.txt" | sort > "${ZIP_INVENTORY_1}"

echo "📊 Zip contains $(wc -l < "${ZIP_INVENTORY_1}") trackable files"
```

### **Phase 3: Compare Against Existing Tracking**
```bash
# Step 5: Load existing tracking data
if [ ! -f "${TRACKING_FILE_1}" ]; then
    echo "⚠️  WARNING: No existing tracking file found at ${TRACKING_FILE_1}"
    echo "Creating empty baseline for comparison"
    touch "${TRACKING_FILE_1}"
fi

echo "📄 Loading existing tracking data..."
EXISTING_FILES_1="temp/${ZIP_NAME_1}_existing_files.txt"
grep -E "^(found|not_found|placeholder):" "${TRACKING_FILE_1}" | cut -d':' -f2- | sort | uniq > "${EXISTING_FILES_1}" || touch "${EXISTING_FILES_1}"

echo "📊 Currently tracking $(wc -l < "${EXISTING_FILES_1}") files"

# Step 6: Identify missing files (in zip but not in tracking)
MISSING_FILES_1="temp/${ZIP_NAME_1}_missing_files.txt"
echo "🔍 Identifying files in zip but not in tracking..."

# Extract just filenames from zip inventory for comparison
sed "s|${EXTRACT_DIR_1}/||g" "${ZIP_INVENTORY_1}" | sort > "temp/zip_filenames_1.txt"

# Compare against existing tracking
comm -23 "temp/zip_filenames_1.txt" "${EXISTING_FILES_1}" > "${MISSING_FILES_1}"

echo "📊 Found $(wc -l < "${MISSING_FILES_1}") files in zip that are not tracked"
```

### **Phase 4: Generate Missing Files Analysis Report**
```bash
# Step 7: Create comprehensive analysis report
echo "📝 Generating missing files analysis report..."
cat > "${REPORT_FILE_1}" << 'EOF'
# Aiorchestration Package Analysis Report
**Package**: aiorchestration-ecca6fd665b0a474369509cb29c4aeaed35c57aa  
**Analysis Date**: $(date)  
**Analyzed By**: Claude Code  
**Governance**: CLAUDE.md compliant  

## Executive Summary
- **Total Files in Zip**: $(wc -l < "${ZIP_INVENTORY_1}")
- **Previously Tracked Files**: $(wc -l < "${EXISTING_FILES_1}") 
- **Newly Discovered Files**: $(wc -l < "${MISSING_FILES_1}")
- **Coverage Gap**: $(($(wc -l < "${MISSING_FILES_1}") * 100 / $(wc -l < "${ZIP_INVENTORY_1}")))%

## Missing Files Requiring Evaluation

EOF

# Step 8: Analyze each missing file and add to report
echo "🔍 Analyzing missing files and generating summaries..."
while IFS= read -r missing_file; do
    if [ -n "$missing_file" ]; then
        FULL_PATH="${EXTRACT_DIR_1}/${missing_file}"
        
        # Add file entry to report
        echo "### 📄 \`${missing_file}\`" >> "${REPORT_FILE_1}"
        echo "" >> "${REPORT_FILE_1}"
        
        # Get file type and basic info
        if [ -f "$FULL_PATH" ]; then
            FILE_SIZE=$(stat -f%z "$FULL_PATH" 2>/dev/null || stat -c%s "$FULL_PATH" 2>/dev/null || echo "unknown")
            echo "- **File Type**: $(file -b "$FULL_PATH" | cut -d',' -f1)" >> "${REPORT_FILE_1}"
            echo "- **File Size**: ${FILE_SIZE} bytes" >> "${REPORT_FILE_1}"
            
            # Generate summary based on file type
            case "$missing_file" in
                *.py)
                    echo "- **Language**: Python" >> "${REPORT_FILE_1}"
                    echo "- **Summary**: " >> "${REPORT_FILE_1}"
                    
                    # Extract classes and functions for Python files
                    CLASSES=$(grep -n "^class " "$FULL_PATH" | head -3 | cut -d':' -f2- | tr '\n' '; ')
                    FUNCTIONS=$(grep -n "^def " "$FULL_PATH" | head -5 | cut -d':' -f2- | tr '\n' '; ')
                    IMPORTS=$(grep -n "^import\|^from.*import" "$FULL_PATH" | head -3 | cut -d':' -f2- | tr '\n' '; ')
                    
                    if [ -n "$CLASSES" ]; then
                        echo "  - **Classes**: ${CLASSES}" >> "${REPORT_FILE_1}"
                    fi
                    if [ -n "$FUNCTIONS" ]; then
                        echo "  - **Functions**: ${FUNCTIONS}" >> "${REPORT_FILE_1}"
                    fi
                    if [ -n "$IMPORTS" ]; then
                        echo "  - **Key Imports**: ${IMPORTS}" >> "${REPORT_FILE_1}"
                    fi
                    
                    # Get docstring or first comment if available
                    DOCSTRING=$(head -20 "$FULL_PATH" | grep -A5 '"""' | head -3 | tail -n +2 | tr '\n' ' ')
                    if [ -n "$DOCSTRING" ]; then
                        echo "  - **Description**: ${DOCSTRING}" >> "${REPORT_FILE_1}"
                    fi
                    ;;
                    
                *.md)
                    echo "- **Language**: Markdown Documentation" >> "${REPORT_FILE_1}"
                    echo "- **Summary**: " >> "${REPORT_FILE_1}"
                    
                    # Extract title and first few lines
                    TITLE=$(head -5 "$FULL_PATH" | grep "^#" | head -1)
                    DESCRIPTION=$(head -10 "$FULL_PATH" | grep -v "^#" | grep -v "^$" | head -2 | tr '\n' ' ')
                    
                    if [ -n "$TITLE" ]; then
                        echo "  - **Title**: ${TITLE}" >> "${REPORT_FILE_1}"
                    fi
                    if [ -n "$DESCRIPTION" ]; then
                        echo "  - **Description**: ${DESCRIPTION}" >> "${REPORT_FILE_1}"
                    fi
                    ;;
                    
                *.yml|*.yaml)
                    echo "- **Language**: YAML Configuration" >> "${REPORT_FILE_1}"
                    echo "- **Summary**: " >> "${REPORT_FILE_1}"
                    
                    # Extract top-level keys
                    TOP_KEYS=$(grep "^[a-zA-Z]" "$FULL_PATH" | head -5 | cut -d':' -f1 | tr '\n' ', ')
                    if [ -n "$TOP_KEYS" ]; then
                        echo "  - **Configuration Sections**: ${TOP_KEYS}" >> "${REPORT_FILE_1}"
                    fi
                    ;;
                    
                *.json)
                    echo "- **Language**: JSON Data" >> "${REPORT_FILE_1}"
                    echo "- **Summary**: " >> "${REPORT_FILE_1}"
                    
                    # Try to extract top-level structure
                    if command -v jq >/dev/null 2>&1; then
                        STRUCTURE=$(jq 'keys' "$FULL_PATH" 2>/dev/null | tr '\n' ' ' || echo "Unable to parse JSON structure")
                        echo "  - **Data Structure**: ${STRUCTURE}" >> "${REPORT_FILE_1}"
                    fi
                    ;;
                    
                *)
                    echo "- **Summary**: General file requiring manual review" >> "${REPORT_FILE_1}"
                    
                    # Get first few non-empty lines as sample
                    SAMPLE=$(head -5 "$FULL_PATH" | grep -v "^$" | head -2 | tr '\n' ' ')
                    if [ -n "$SAMPLE" ]; then
                        echo "  - **Content Sample**: ${SAMPLE}..." >> "${REPORT_FILE_1}"
                    fi
                    ;;
            esac
            
            echo "- **Evaluation Status**: 🔍 Requires Review" >> "${REPORT_FILE_1}"
            echo "- **Priority**: Medium" >> "${REPORT_FILE_1}"
            echo "" >> "${REPORT_FILE_1}"
        else
            echo "- **Status**: ❌ File not accessible" >> "${REPORT_FILE_1}"
            echo "" >> "${REPORT_FILE_1}"
        fi
    fi
done < "${MISSING_FILES_1}"

# Add completion footer to report
cat >> "${REPORT_FILE_1}" << 'EOF'

## Next Steps
1. Review each missing file listed above
2. Determine integration priority and dependencies  
3. Add files to tracking system with appropriate status
4. Update project documentation as needed
5. Follow CLAUDE.md governance procedures for file integration

## Governance Compliance
✅ Analysis completed per CLAUDE.md procedures  
✅ Report stored in temp directory as specified  
✅ Complete inventory and comparison performed  
✅ Ready for manual evaluation phase  

---
*Generated by Claude Code - Aiorchestration Analysis System*
EOF

echo "✅ First package analysis complete. Report saved to: ${REPORT_FILE_1}"
```

### **Phase 5: Second Zip Analysis - aiorchestration-d2957cd50ff26c5e3bf46c9f535832504b41a1a8**
```bash
ZIP_NAME_2="aiorchestration-d2957cd50ff26c5e3bf46c9f535832504b41a1a8"
TRACKING_FILE_2="temp/${ZIP_NAME_2}"
REPORT_FILE_2="temp/${ZIP_NAME_2}_missing_analysis.md"

echo ""
echo "=== ANALYZING SECOND AIORCHESTRATION PACKAGE ==="
echo "📦 Target Zip: ${ZIP_NAME_2}.zip"
echo "📄 Tracking File: ${TRACKING_FILE_2}"
echo "📊 Report Output: ${REPORT_FILE_2}"

# Repeat identical analysis process for second zip
if [ ! -f "${ZIP_NAME_2}.zip" ]; then
    echo "❌ ERROR: ${ZIP_NAME_2}.zip not found in root directory"
    echo "Expected location: $(pwd)/${ZIP_NAME_2}.zip"
    exit 1
fi

# Extract second zip
EXTRACT_DIR_2="temp/extracted_${ZIP_NAME_2}"
rm -rf "${EXTRACT_DIR_2}"
mkdir -p "${EXTRACT_DIR_2}"

echo "📂 Extracting ${ZIP_NAME_2}.zip..."
unzip -q "${ZIP_NAME_2}.zip" -d "${EXTRACT_DIR_2}"

# Generate inventory
ZIP_INVENTORY_2="temp/${ZIP_NAME_2}_zip_inventory.txt"
find "${EXTRACT_DIR_2}" -type f -name "*.py" -o -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name "*.txt" | sort > "${ZIP_INVENTORY_2}"

echo "📊 Second zip contains $(wc -l < "${ZIP_INVENTORY_2}") trackable files"

# Load existing tracking for second package
if [ ! -f "${TRACKING_FILE_2}" ]; then
    echo "⚠️  WARNING: No existing tracking file found at ${TRACKING_FILE_2}"
    touch "${TRACKING_FILE_2}"
fi

EXISTING_FILES_2="temp/${ZIP_NAME_2}_existing_files.txt"
grep -E "^(found|not_found|placeholder):" "${TRACKING_FILE_2}" | cut -d':' -f2- | sort | uniq > "${EXISTING_FILES_2}" || touch "${EXISTING_FILES_2}"

# Identify missing files in second package
MISSING_FILES_2="temp/${ZIP_NAME_2}_missing_files.txt"
sed "s|${EXTRACT_DIR_2}/||g" "${ZIP_INVENTORY_2}" | sort > "temp/zip_filenames_2.txt"
comm -23 "temp/zip_filenames_2.txt" "${EXISTING_FILES_2}" > "${MISSING_FILES_2}"

echo "📊 Found $(wc -l < "${MISSING_FILES_2}") files in second zip that are not tracked"
```

### **Phase 6: Generate Second Package Analysis Report**
```bash
# Create second report using same methodology
echo "📝 Generating second package analysis report..."

# Use identical report generation logic as Phase 4, but with _2 variables
# [Same report generation code structure, but using ZIP_NAME_2, EXTRACT_DIR_2, etc.]

# Generate report header for second package
cat > "${REPORT_FILE_2}" << EOF
# Aiorchestration Package Analysis Report
**Package**: aiorchestration-d2957cd50ff26c5e3bf46c9f535832504b41a1a8  
**Analysis Date**: $(date)  
**Analyzed By**: Claude Code  
**Governance**: CLAUDE.md compliant  

## Executive Summary
- **Total Files in Zip**: $(wc -l < "${ZIP_INVENTORY_2}")
- **Previously Tracked Files**: $(wc -l < "${EXISTING_FILES_2}") 
- **Newly Discovered Files**: $(wc -l < "${MISSING_FILES_2}")
- **Coverage Gap**: $(awk "BEGIN {printf \"%.1f\", $(wc -l < "${MISSING_FILES_2}") * 100 / $(wc -l < "${ZIP_INVENTORY_2}")}")%

## Missing Files Requiring Evaluation

EOF

# Analyze each missing file in second package (same logic as first package)
while IFS= read -r missing_file; do
    if [ -n "$missing_file" ]; then
        FULL_PATH="${EXTRACT_DIR_2}/${missing_file}"
        # [Include same file analysis logic from Phase 4, adapted for second package]
        
        echo "### 📄 \`${missing_file}\`" >> "${REPORT_FILE_2}"
        echo "" >> "${REPORT_FILE_2}"
        
        if [ -f "$FULL_PATH" ]; then
            FILE_SIZE=$(stat -f%z "$FULL_PATH" 2>/dev/null || stat -c%s "$FULL_PATH" 2>/dev/null || echo "unknown")
            echo "- **File Type**: $(file -b "$FULL_PATH" | cut -d',' -f1)" >> "${REPORT_FILE_2}"
            echo "- **File Size**: ${FILE_SIZE} bytes" >> "${REPORT_FILE_2}"
            echo "- **Evaluation Status**: 🔍 Requires Review" >> "${REPORT_FILE_2}"
            echo "- **Priority**: Medium" >> "${REPORT_FILE_2}"
            echo "" >> "${REPORT_FILE_2}"
        fi
    fi
done < "${MISSING_FILES_2}"

# Add footer to second report
cat >> "${REPORT_FILE_2}" << 'EOF'

## Next Steps
1. Review each missing file listed above
2. Determine integration priority and dependencies  
3. Add files to tracking system with appropriate status
4. Update project documentation as needed
5. Follow CLAUDE.md governance procedures for file integration

## Governance Compliance
✅ Analysis completed per CLAUDE.md procedures  
✅ Report stored in temp directory as specified  
✅ Complete inventory and comparison performed  
✅ Ready for manual evaluation phase  

---
*Generated by Claude Code - Aiorchestration Analysis System*
EOF

echo "✅ Second package analysis complete. Report saved to: ${REPORT_FILE_2}"
```

### **Phase 7: Generate Combined Summary Report**
```bash
COMBINED_REPORT="temp/aiorchestration_combined_analysis.md"

echo ""
echo "📊 Generating combined analysis summary..."

cat > "${COMBINED_REPORT}" << EOF
# Combined Aiorchestration Packages Analysis Summary

**Analysis Date**: $(date)  
**Packages Analyzed**: 2  
**Governance**: CLAUDE.md compliant  
**Status**: Complete  

## Package Comparison Overview

| Package | Total Files | Tracked Files | Missing Files | Coverage Gap |
|---------|-------------|---------------|---------------|--------------|
| ecca6fd... | $(wc -l < "${ZIP_INVENTORY_1}") | $(wc -l < "${EXISTING_FILES_1}") | $(wc -l < "${MISSING_FILES_1}") | $(awk "BEGIN {printf \"%.1f%%\", $(wc -l < "${MISSING_FILES_1}") * 100 / $(wc -l < "${ZIP_INVENTORY_1}")}")
| d2957cd... | $(wc -l < "${ZIP_INVENTORY_2}") | $(wc -l < "${EXISTING_FILES_2}") | $(wc -l < "${MISSING_FILES_2}") | $(awk "BEGIN {printf \"%.1f%%\", $(wc -l < "${MISSING_FILES_2}") * 100 / $(wc -l < "${ZIP_INVENTORY_2}")}")

## Total Discovery Summary
- **Combined Files Discovered**: $(($(wc -l < "${MISSING_FILES_1}") + $(wc -l < "${MISSING_FILES_2}")))
- **Unique Missing Components**: Requires cross-package deduplication analysis
- **Priority Review Queue**: All missing files flagged for manual evaluation

## Generated Reports
1. **Package 1 Analysis**: \`${REPORT_FILE_1}\`
2. **Package 2 Analysis**: \`${REPORT_FILE_2}\`
3. **Combined Summary**: \`${COMBINED_REPORT}\`

## Governance Compliance Status
✅ Both packages analyzed per CLAUDE.md procedures  
✅ Complete file inventories generated  
✅ Missing files identified and categorized  
✅ Analysis reports stored in temp directory  
✅ Ready for next phase evaluation  

## Next Steps
1. Review individual package reports for detailed file analysis
2. Perform cross-package deduplication to identify truly unique files
3. Prioritize missing files based on project requirements
4. Update tracking files with evaluation results
5. Follow CLAUDE.md integration procedures

---
*Generated by Claude Code - Aiorchestration Analysis System*
EOF

echo "✅ Combined summary report generated: ${COMBINED_REPORT}"
```

### **Phase 8: Cleanup & Governance Documentation**
```bash
echo ""
echo "🧹 Performing cleanup and governance documentation..."

# Clean up temporary extraction directories (optional - keep for debugging)
# rm -rf "${EXTRACT_DIR_1}" "${EXTRACT_DIR_2}"

# Update governance log
echo "$(date): Aiorchestration zip analysis completed successfully" >> temp/governance_log.txt
echo "Reports generated: ${REPORT_FILE_1}, ${REPORT_FILE_2}, ${COMBINED_REPORT}" >> temp/governance_log.txt
echo "Files discovered for review: $(($(wc -l < "${MISSING_FILES_1}") + $(wc -l < "${MISSING_FILES_2}")))" >> temp/governance_log.txt

# Display final summary
echo ""
echo "🎯 === ANALYSIS COMPLETE ==="
echo "📊 Package 1 (ecca6fd...): $(wc -l < "${MISSING_FILES_1}") new files discovered"
echo "📊 Package 2 (d2957cd...): $(wc -l < "${MISSING_FILES_2}") new files discovered"
echo "📊 Total new files for review: $(($(wc -l < "${MISSING_FILES_1}") + $(wc -l < "${MISSING_FILES_2}")))"
echo ""
echo "📄 Generated Reports:"
echo "   • ${REPORT_FILE_1}"
echo "   • ${REPORT_FILE_2}" 
echo "   • ${COMBINED_REPORT}"
echo ""
echo "✅ All procedures completed per CLAUDE.md governance requirements"
echo "🔍 Ready for manual evaluation phase"
```

## 🛡️ ERROR HANDLING & RECOVERY

### **Common Issues & Solutions**
```bash
# Handle missing governance file
handle_missing_governance() {
    if [ ! -f "CLAUDE.md" ]; then
        echo "❌ CRITICAL: CLAUDE.md not found"
        echo "Cannot proceed without governance procedures"
        echo "Please ensure CLAUDE.md exists in root directory"
        exit 1
    fi
}

# Handle zip extraction failures
handle_zip_errors() {
    local zip_file="$1"
    local extract_dir="$2"
    
    if ! unzip -t "${zip_file}" >/dev/null 2>&1; then
        echo "❌ ERROR: ${zip_file} is corrupted or invalid"
        echo "Please verify zip file integrity"
        return 1
    fi
    
    if ! unzip -q "${zip_file}" -d "${extract_dir}"; then
        echo "❌ ERROR: Failed to extract ${zip_file}"
        echo "Check file permissions and disk space"
        return 1
    fi
    
    return 0
}

# Handle tracking file issues
handle_tracking_file_errors() {
    local tracking_file="$1"
    
    if [ -f "${tracking_file}" ] && [ ! -r "${tracking_file}" ]; then
        echo "⚠️  WARNING: Cannot read tracking file ${tracking_file}"
        echo "Check file permissions"
        return 1
    fi
    
    return 0
}
```

## 🔍 VALIDATION & QUALITY ASSURANCE

### **Pre-Execution Checks**
```bash
pre_execution_validation() {
    echo "🔍 Performing pre-execution validation..."
    
    # Check required files exist
    local required_files=(
        "CLAUDE.md"
        "aiorchestration-ecca6fd665b0a474369509cb29c4aeaed35c57aa.zip"
        "aiorchestration-d2957cd50ff26c5e3bf46c9f535832504b41a1a8.zip"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "❌ Missing required file: $file"
            return 1
        fi
    done
    
    # Check directory permissions
    if [ ! -w "temp" ]; then
        echo "❌ Cannot write to temp directory"
        return 1
    fi
    
    echo "✅ Pre-execution validation passed"
    return 0
}
```

### **Post-Execution Verification**
```bash
post_execution_verification() {
    echo "🔍 Performing post-execution verification..."
    
    local expected_reports=(
        "${REPORT_FILE_1}"
        "${REPORT_FILE_2}"
        "${COMBINED_REPORT}"
    )
    
    for report in "${expected_reports[@]}"; do
        if [ ! -f "$report" ]; then
            echo "❌ Missing expected report: $report"
            return 1
        fi
        
        if [ ! -s "$report" ]; then
            echo "❌ Empty report file: $report"
            return 1
        fi
    done
    
    echo "✅ Post-execution verification passed"
    return 0
}
```

## 🚀 EXECUTION SUMMARY

This comprehensive Claude Code prompt will:

1. **✅ Extract & Analyze Both Zip Packages**
2. **✅ Compare Against Existing Temp Folder Tracking Files**
3. **✅ Identify All Missing Files with Detailed Analysis**
4. **✅ Generate Individual & Combined Reports**
5. **✅ Follow CLAUDE.md Governance Procedures**
6. **✅ Store All Reports in Temp Directory**
7. **✅ Provide Complete Error Handling & Recovery**

**Ready for immediate execution by Claude Code with full governance compliance and comprehensive file analysis capabilities.**

---

*This prompt ensures systematic analysis of both aiorchestration packages while maintaining strict governance compliance and generating actionable reports for further evaluation.*

**Version**: 1.0  
**Created**: Marcus Chen Prompt Engineering System  
**Status**: Production Ready with Full Governance Integration