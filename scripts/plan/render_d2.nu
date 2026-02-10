use xs.nu *

def main [
    --topic: string = "psychoanalyze.plan"
    --last: int = 500
    --output: string = "docs/plan.jj.d2"
] {
    let events = (
        .cat --topic $topic --last $last
            | get meta
            | where $it != null
    )

    let node_events = ($events | where type == "plan.node.upsert")
    let edge_events = (
        $events
            | where type == "plan.edge.upsert"
            | each {|event| { key: $"($event.edge.from)->($event.edge.to)", edge: $event.edge } }
    )

    let nodes = (
        $node_events
            | group-by node.id
            | transpose
            | each {|row| $row.value | last | get node }
            | sort-by id
    )

    let edges = (
        $edge_events
            | group-by key
            | transpose
            | each {|row| $row.value | last | get edge }
    )

    let lines = [
        "direction: down",
        "",
        "jj_planning: {",
        "\tlabel: \"JJ Revisions (each node = red/green/refactor cycle)\"",
        "\tdirection: down",
        ""
    ]

    let node_lines = ($nodes | each {|node| $"\t($node.id): \"($node.label)\"" })
    let edge_lines = ($edges | each {|edge| $"\t($edge.from) -> ($edge.to)" })

    ($lines | append $node_lines | append [""] | append $edge_lines | append ["}"])
        | str join (char nl)
        | save --force $output
}
