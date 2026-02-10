use xs.nu *

def slugify [text: string] {
    let base = ($text | str trim)
    if ($base | str length) == 0 {
        return "unnamed"
    }

    $base
        | str downcase
        | str replace -a " " "_"
        | str replace -a "-" "_"
        | str replace -a "/" "_"
        | str replace -a ":" "_"
        | str replace -a "." "_"
}

def main [
    --limit: int = 50
    --topic: string = "psychoanalyze.plan"
    --dry-run
] {
    let raw = (
        jj log --no-graph --limit $limit --template 'change_id.short() ++ "\t" ++ description.first_line() ++ "\n"'
    )

    let records = (
        $raw
            | lines
            | where ($it | str length) > 0
            | parse "{change_id}\t{description}"
    )

    let nodes = (
        $records
            | each {|row|
                let desc = ($row.description | default "")
                let basis = if ($desc | str length) > 0 { $desc } else { $row.change_id }
                let slug = (slugify $basis)
                {
                    change_id: $row.change_id
                    description: $desc
                    id: $slug
                }
            }
    )

    let edge_pairs = if ($nodes | length) > 1 {
        0..(($nodes | length) - 2)
            | each {|idx|
                {
                    from: ($nodes | get ($idx + 1) | get id)
                    to: ($nodes | get $idx | get id)
                }
            }
    } else {
        []
    }

    let node_events = (
        $nodes
            | each {|node|
                {
                    type: "plan.node.upsert"
                    node: {
                        id: $node.id
                        label: (if ($node.description | str length) > 0 { $node.description } else { $node.id })
                        kind: "jj"
                        change_id: $node.change_id
                    }
                    source: {
                        jj: {
                            change_id: $node.change_id
                            description: $node.description
                        }
                    }
                }
            }
    )

    let edge_events = (
        $edge_pairs
            | each {|edge|
                {
                    type: "plan.edge.upsert"
                    edge: {
                        from: $edge.from
                        to: $edge.to
                        kind: "jj"
                    }
                }
            }
    )

    let events = ($node_events | append $edge_events)

    if $dry_run {
        $events
    } else {
        $events | each {|event| "" | .append $topic --meta $event }
    }
}
