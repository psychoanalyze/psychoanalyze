#!/usr/bin/env nu

# Watch and render all D2 files in docs/ to docs/figures/
# Usage: nu watch_all_d2.nu

def main [] {
    print "Starting D2 watch server for all diagrams..."

    # Get all D2 files in docs/
    let d2_files = (ls docs/*.d2 | get name)

    print $"Found ($d2_files | length) D2 files to watch:"
    $d2_files | each {|file| print $"  - ($file)"} | ignore

    # Initial render of all files
    print "\nInitial render..."
    $d2_files | each {|input_file|
        let basename = ($input_file | path basename | str replace '.d2' '')
        let output_file = $"docs/figures/($basename).svg"
        print $"  Rendering ($input_file) -> ($output_file)"
        ^d2 $input_file $output_file
    } | ignore

    print "\nWatching for changes (Ctrl+C to stop)..."

    # Watch all D2 files for changes using D2's built-in watch
    # Launch parallel watch processes for each file
    $d2_files | each {|input_file|
        let basename = ($input_file | path basename | str replace '.d2' '')
        let output_file = $"docs/figures/($basename).svg"

        # Start d2 in watch mode for each file (run in background)
        # Note: This will create multiple d2 processes
        print $"  Starting watch for ($basename)..."
    } | ignore

    # Use d2's native watch for each file
    # We'll use parallel execution
    $d2_files | par-each {|input_file|
        let basename = ($input_file | path basename | str replace '.d2' '')
        let output_file = $"docs/figures/($basename).svg"

        # Run d2 with --watch flag (this blocks, so we use par-each)
        ^d2 $input_file $output_file --watch
    }
}
