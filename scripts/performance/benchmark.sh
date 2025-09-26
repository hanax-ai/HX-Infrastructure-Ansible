
#!/bin/bash

# Performance Benchmarking Script for Ansible Infrastructure
# Sprint 2 - Advanced Capabilities Implementation

set -euo pipefail

# Configuration
RESULTS_FILE="performance-results.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TEMP_DIR=$(mktemp -d)
ANSIBLE_PLAYBOOK_DIR="playbooks"
TEST_INVENTORY="tests/inventory/test_hosts"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Initialize results structure
init_results() {
    cat > "$RESULTS_FILE" << EOF
{
  "timestamp": "$TIMESTAMP",
  "benchmarks": {
    "playbook_execution": {},
    "role_performance": {},
    "inventory_parsing": {},
    "template_rendering": {},
    "module_execution": {},
    "overall_metrics": {}
  },
  "environment": {
    "ansible_version": "$(ansible --version | head -n1 | cut -d' ' -f2)",
    "python_version": "$(python3 --version | cut -d' ' -f2)",
    "system_info": {
      "cpu_cores": "$(nproc)",
      "memory_gb": "$(free -g | awk '/^Mem:/{print $2}')",
      "disk_space_gb": "$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')"
    }
  }
}
EOF
}

# Benchmark playbook execution time
benchmark_playbook_execution() {
    log "Benchmarking playbook execution times..."
    
    local playbooks=(
        "playbooks/common/setup.yml"
        "playbooks/security/security.yml"
        "playbooks/deployment/deploy.yml"
    )
    
    for playbook in "${playbooks[@]}"; do
        if [[ -f "$playbook" ]]; then
            local playbook_name=$(basename "$playbook" .yml)
            log "Testing $playbook_name..."
            
            # Dry run timing
            local start_time=$(date +%s.%N)
            ansible-playbook "$playbook" -i "$TEST_INVENTORY" --check --diff > /dev/null 2>&1 || true
            local end_time=$(date +%s.%N)
            local dry_run_time=$(echo "$end_time - $start_time" | bc)
            
            # Syntax check timing
            start_time=$(date +%s.%N)
            ansible-playbook "$playbook" --syntax-check > /dev/null 2>&1 || true
            end_time=$(date +%s.%N)
            local syntax_check_time=$(echo "$end_time - $start_time" | bc)
            
            # Update results
            jq --arg name "$playbook_name" \
               --arg dry_run "$dry_run_time" \
               --arg syntax "$syntax_check_time" \
               '.benchmarks.playbook_execution[$name] = {
                 "dry_run_seconds": ($dry_run | tonumber),
                 "syntax_check_seconds": ($syntax | tonumber),
                 "playbook_path": "'$playbook'"
               }' "$RESULTS_FILE" > "$TEMP_DIR/results.tmp" && mv "$TEMP_DIR/results.tmp" "$RESULTS_FILE"
        fi
    done
}

# Benchmark role performance
benchmark_role_performance() {
    log "Benchmarking role performance..."
    
    local roles_dir="roles"
    if [[ -d "$roles_dir" ]]; then
        for role_path in "$roles_dir"/*; do
            if [[ -d "$role_path" ]]; then
                local role_name=$(basename "$role_path")
                log "Testing role: $role_name"
                
                # Create test playbook for role
                local test_playbook="$TEMP_DIR/test_${role_name}.yml"
                cat > "$test_playbook" << EOF
---
- hosts: localhost
  connection: local
  gather_facts: true
  roles:
    - $role_name
EOF
                
                # Time role execution (dry run)
                local start_time=$(date +%s.%N)
                ansible-playbook "$test_playbook" --check > /dev/null 2>&1 || true
                local end_time=$(date +%s.%N)
                local execution_time=$(echo "$end_time - $start_time" | bc)
                
                # Count tasks in role
                local task_count=0
                if [[ -f "$role_path/tasks/main.yml" ]]; then
                    task_count=$(grep -c "^- name:" "$role_path/tasks/main.yml" 2>/dev/null || echo "0")
                fi
                
                # Update results
                jq --arg name "$role_name" \
                   --arg time "$execution_time" \
                   --arg tasks "$task_count" \
                   '.benchmarks.role_performance[$name] = {
                     "execution_seconds": ($time | tonumber),
                     "task_count": ($tasks | tonumber),
                     "avg_task_time": (if ($tasks | tonumber) > 0 then (($time | tonumber) / ($tasks | tonumber)) else 0 end)
                   }' "$RESULTS_FILE" > "$TEMP_DIR/results.tmp" && mv "$TEMP_DIR/results.tmp" "$RESULTS_FILE"
            fi
        done
    fi
}

# Benchmark inventory parsing
benchmark_inventory_parsing() {
    log "Benchmarking inventory parsing..."
    
    local inventories=(
        "environments/development/inventory.yml"
        "environments/staging/inventory.yml"
        "environments/production/inventory.yml"
        "tests/inventory/test_hosts"
    )
    
    for inventory in "${inventories[@]}"; do
        if [[ -f "$inventory" ]]; then
            local inv_name=$(basename "$inventory" | sed 's/\.[^.]*$//')
            log "Testing inventory: $inv_name"
            
            # Time inventory parsing
            local start_time=$(date +%s.%N)
            ansible-inventory -i "$inventory" --list > /dev/null 2>&1 || true
            local end_time=$(date +%s.%N)
            local parse_time=$(echo "$end_time - $start_time" | bc)
            
            # Count hosts
            local host_count=$(ansible-inventory -i "$inventory" --list 2>/dev/null | jq -r '._meta.hostvars | keys | length' 2>/dev/null || echo "0")
            
            # Update results
            jq --arg name "$inv_name" \
               --arg time "$parse_time" \
               --arg hosts "$host_count" \
               '.benchmarks.inventory_parsing[$name] = {
                 "parse_seconds": ($time | tonumber),
                 "host_count": ($hosts | tonumber),
                 "avg_host_time": (if ($hosts | tonumber) > 0 then (($time | tonumber) / ($hosts | tonumber)) else 0 end)
               }' "$RESULTS_FILE" > "$TEMP_DIR/results.tmp" && mv "$TEMP_DIR/results.tmp" "$RESULTS_FILE"
        fi
    done
}

# Benchmark template rendering
benchmark_template_rendering() {
    log "Benchmarking template rendering..."
    
    # Find all template files
    local template_count=0
    local total_render_time=0
    
    while IFS= read -r -d '' template_file; do
        local template_name=$(basename "$template_file")
        log "Testing template: $template_name"
        
        # Create test playbook for template
        local test_playbook="$TEMP_DIR/test_template.yml"
        cat > "$test_playbook" << EOF
---
- hosts: localhost
  connection: local
  gather_facts: true
  tasks:
    - name: Test template rendering
      template:
        src: $template_file
        dest: $TEMP_DIR/rendered_template
      ignore_errors: true
EOF
        
        # Time template rendering
        local start_time=$(date +%s.%N)
        ansible-playbook "$test_playbook" > /dev/null 2>&1 || true
        local end_time=$(date +%s.%N)
        local render_time=$(echo "$end_time - $start_time" | bc)
        
        template_count=$((template_count + 1))
        total_render_time=$(echo "$total_render_time + $render_time" | bc)
        
    done < <(find . -name "*.j2" -type f -print0 2>/dev/null)
    
    # Calculate averages
    local avg_render_time=0
    if [[ $template_count -gt 0 ]]; then
        avg_render_time=$(echo "scale=6; $total_render_time / $template_count" | bc)
    fi
    
    # Update results
    jq --arg count "$template_count" \
       --arg total "$total_render_time" \
       --arg avg "$avg_render_time" \
       '.benchmarks.template_rendering = {
         "template_count": ($count | tonumber),
         "total_render_seconds": ($total | tonumber),
         "avg_render_seconds": ($avg | tonumber)
       }' "$RESULTS_FILE" > "$TEMP_DIR/results.tmp" && mv "$TEMP_DIR/results.tmp" "$RESULTS_FILE"
}

# Benchmark module execution
benchmark_module_execution() {
    log "Benchmarking common module execution..."
    
    local modules=(
        "setup"
        "ping"
        "file"
        "copy"
        "template"
        "service"
        "package"
    )
    
    for module in "${modules[@]}"; do
        log "Testing module: $module"
        
        # Create appropriate test for each module
        local test_playbook="$TEMP_DIR/test_${module}.yml"
        case $module in
            "setup"|"ping")
                cat > "$test_playbook" << EOF
---
- hosts: localhost
  connection: local
  tasks:
    - name: Test $module module
      $module:
EOF
                ;;
            "file")
                cat > "$test_playbook" << EOF
---
- hosts: localhost
  connection: local
  tasks:
    - name: Test file module
      file:
        path: $TEMP_DIR/test_file
        state: touch
EOF
                ;;
            "copy")
                echo "test content" > "$TEMP_DIR/source_file"
                cat > "$test_playbook" << EOF
---
- hosts: localhost
  connection: local
  tasks:
    - name: Test copy module
      copy:
        src: $TEMP_DIR/source_file
        dest: $TEMP_DIR/dest_file
EOF
                ;;
            *)
                # Skip modules that require more complex setup
                continue
                ;;
        esac
        
        # Time module execution
        local start_time=$(date +%s.%N)
        ansible-playbook "$test_playbook" > /dev/null 2>&1 || true
        local end_time=$(date +%s.%N)
        local exec_time=$(echo "$end_time - $start_time" | bc)
        
        # Update results
        jq --arg name "$module" \
           --arg time "$exec_time" \
           '.benchmarks.module_execution[$name] = {
             "execution_seconds": ($time | tonumber)
           }' "$RESULTS_FILE" > "$TEMP_DIR/results.tmp" && mv "$TEMP_DIR/results.tmp" "$RESULTS_FILE"
    done
}

# Calculate overall metrics
calculate_overall_metrics() {
    log "Calculating overall performance metrics..."
    
    # Get system load
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    
    # Get memory usage
    local memory_usage=$(free | awk '/^Mem:/{printf "%.2f", $3/$2 * 100.0}')
    
    # Calculate total benchmark time
    local total_time=0
    
    # Sum up all benchmark times
    total_time=$(jq -r '
        [
            .benchmarks.playbook_execution[].dry_run_seconds,
            .benchmarks.role_performance[].execution_seconds,
            .benchmarks.inventory_parsing[].parse_seconds,
            .benchmarks.template_rendering.total_render_seconds,
            .benchmarks.module_execution[].execution_seconds
        ] | add // 0
    ' "$RESULTS_FILE")
    
    # Update results with overall metrics
    jq --arg load "$load_avg" \
       --arg memory "$memory_usage" \
       --arg total "$total_time" \
       '.benchmarks.overall_metrics = {
         "total_benchmark_seconds": ($total | tonumber),
         "system_load_avg": ($load | tonumber),
         "memory_usage_percent": ($memory | tonumber),
         "performance_score": (100 - ($total | tonumber * 10) - ($memory | tonumber / 2))
       }' "$RESULTS_FILE" > "$TEMP_DIR/results.tmp" && mv "$TEMP_DIR/results.tmp" "$RESULTS_FILE"
}

# Generate performance report
generate_report() {
    log "Generating performance report..."
    
    local report_file="performance-report.md"
    
    cat > "$report_file" << EOF
# Ansible Infrastructure Performance Benchmark Report

**Generated:** $(date)
**Environment:** $(jq -r '.environment.ansible_version' "$RESULTS_FILE")

## Executive Summary

- **Total Benchmark Time:** $(jq -r '.benchmarks.overall_metrics.total_benchmark_seconds' "$RESULTS_FILE")s
- **Performance Score:** $(jq -r '.benchmarks.overall_metrics.performance_score' "$RESULTS_FILE")/100
- **System Load:** $(jq -r '.benchmarks.overall_metrics.system_load_avg' "$RESULTS_FILE")
- **Memory Usage:** $(jq -r '.benchmarks.overall_metrics.memory_usage_percent' "$RESULTS_FILE")%

## Detailed Results

### Playbook Execution Performance
$(jq -r '.benchmarks.playbook_execution | to_entries[] | "- **\(.key):** \(.value.dry_run_seconds)s (dry run), \(.value.syntax_check_seconds)s (syntax check)"' "$RESULTS_FILE")

### Role Performance
$(jq -r '.benchmarks.role_performance | to_entries[] | "- **\(.key):** \(.value.execution_seconds)s (\(.value.task_count) tasks, \(.value.avg_task_time)s avg/task)"' "$RESULTS_FILE")

### Inventory Parsing
$(jq -r '.benchmarks.inventory_parsing | to_entries[] | "- **\(.key):** \(.value.parse_seconds)s (\(.value.host_count) hosts)"' "$RESULTS_FILE")

### Template Rendering
- **Total Templates:** $(jq -r '.benchmarks.template_rendering.template_count' "$RESULTS_FILE")
- **Total Time:** $(jq -r '.benchmarks.template_rendering.total_render_seconds' "$RESULTS_FILE")s
- **Average Time:** $(jq -r '.benchmarks.template_rendering.avg_render_seconds' "$RESULTS_FILE")s

### Module Execution
$(jq -r '.benchmarks.module_execution | to_entries[] | "- **\(.key):** \(.value.execution_seconds)s"' "$RESULTS_FILE")

## Recommendations

$(jq -r '.benchmarks.overall_metrics.performance_score' "$RESULTS_FILE" | awk '{
    if ($1 >= 80) print "✅ **Excellent Performance** - No immediate optimizations needed"
    else if ($1 >= 60) print "⚠️ **Good Performance** - Consider minor optimizations"
    else if ($1 >= 40) print "🔶 **Fair Performance** - Optimization recommended"
    else print "❌ **Poor Performance** - Immediate optimization required"
}')

EOF
    
    success "Performance report generated: $report_file"
}

# Cleanup function
cleanup() {
    log "Cleaning up temporary files..."
    rm -rf "$TEMP_DIR"
}

# Main execution
main() {
    log "Starting Ansible Infrastructure Performance Benchmark"
    log "Results will be saved to: $RESULTS_FILE"
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    # Initialize results file
    init_results
    
    # Run benchmarks
    benchmark_playbook_execution
    benchmark_role_performance
    benchmark_inventory_parsing
    benchmark_template_rendering
    benchmark_module_execution
    
    # Calculate overall metrics
    calculate_overall_metrics
    
    # Generate report
    generate_report
    
    success "Performance benchmarking completed!"
    success "Results: $RESULTS_FILE"
    success "Report: performance-report.md"
    
    # Display summary
    echo
    log "Performance Summary:"
    echo "  Total Time: $(jq -r '.benchmarks.overall_metrics.total_benchmark_seconds' "$RESULTS_FILE")s"
    echo "  Performance Score: $(jq -r '.benchmarks.overall_metrics.performance_score' "$RESULTS_FILE")/100"
    echo "  System Load: $(jq -r '.benchmarks.overall_metrics.system_load_avg' "$RESULTS_FILE")"
    echo "  Memory Usage: $(jq -r '.benchmarks.overall_metrics.memory_usage_percent' "$RESULTS_FILE")%"
}

# Check dependencies
check_dependencies() {
    local deps=("ansible" "ansible-playbook" "jq" "bc")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            error "Required dependency '$dep' is not installed"
            exit 1
        fi
    done
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    check_dependencies
    main "$@"
fi

